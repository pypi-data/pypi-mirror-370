from typing import Tuple, Dict, List

import cyipopt
import hopsy
import joblib
import numpy as np
import scipy.linalg as linalg
import scipy.optimize as optimize
import scipy.stats as stats

from .lib.core import (
    _SimulatorBase,
    StationaryParameterSpace,
    NonStationaryParameterSpace,
    NetworkData,
    MeasurementConfiguration,
    ParameterConstraints,
    DefinitionConstraint,
    create_simulator_from_data,
)
from .optimization import IpoptOptimizationProblem, IpoptError
from .utilities import get_non_constant_names, get_inequalities_from_bounds, compute_closest_interior_point


def _compute_stable_fisher_inverse(scaled_jacobian: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Compute inverse of the free parameter Fisher information matrix. The algorithm is stable with regard to parameter
    non-identifiability.
    :param scaled_jacobian:
        Jacobian matrix of forward simulation at the MLE, scaled by measurement standard deviations
    :return:
        covariance matrix estimate, array of non-identifiable parameters
    """
    _, R, P = linalg.qr(scaled_jacobian, pivoting=True)

    # Compute reduced inverse of R and determine rank
    rank = 0
    tol = np.finfo(float).eps * abs(R[0, 0])
    for k in range(scaled_jacobian.shape[1]):
        if abs(R[k, k]) < tol:
            break
        R[k, k] = 1.0 / R[k, k]
        for j in range(k):
            temp = R[k, k] * R[j, k]
            R[j, k] = 0.0
            R[: j + 1, k] -= temp * R[: j + 1, j]
        rank += 1

    for k in range(rank):
        for j in range(k):
            temp = R[j, k]
            R[: j + 1, j] += temp * R[: j + 1, k]
        temp = R[k, k]
        R[: k + 1, k] *= temp

    # Form lower triangle of the covariance matrix and report non-identifiable parameters
    non_det_idx = np.zeros(scaled_jacobian.shape[1] - rank, dtype=int)
    diagonal = np.zeros(scaled_jacobian.shape[1])
    for j in range(scaled_jacobian.shape[1]):
        j_orig = P[j]
        singular = j > (rank - 1)
        if singular:
            non_det_idx[j - rank] = j_orig

        for i in range(j + 1):
            if singular:
                R[i, j] = 0.0
            i_orig = P[i]
            if i_orig > j_orig:
                R[i_orig, j_orig] = R[i, j]
            elif i_orig < j_orig:
                R[j_orig, i_orig] = R[i, j]

        diagonal[j_orig] = R[j, j]

    # Make R symmetric
    for j in range(scaled_jacobian.shape[1]):
        R[: j + 1, j] = R[j, : j + 1]
    np.fill_diagonal(R, diagonal)

    return R[: scaled_jacobian.shape[1], : scaled_jacobian.shape[1]], non_det_idx


def compute_free_parameter_covariance(simulator: _SimulatorBase, mle: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Compute asymptotic free parameter covariance from Maximum Likelihood theory. The algorithm used for inversion of the
    Fisher information is stable with regard to non-identifiable parameters.

    :param simulator:
         Labeling simulator to evaluate the Hessian/Fisher information matrix
    :param mle:
        Maximum Likelihood estimator of the free parameters
    :return:
        covariance matrix estimate, array of non-identifiable parameters
    """
    std_devs = simulator.measurement_standard_deviations
    std_devs_vector = np.concatenate((np.concatenate(std_devs[0]), std_devs[1]))
    scaled_jacobian = np.diagflat(1.0 / std_devs_vector) @ simulator.compute_jacobian(mle)
    return _compute_stable_fisher_inverse(scaled_jacobian)


def _compute_parameter_covariance(free_covariance, first_deps, second_deps):
    value = 0.0
    for first_dep_idx in range(len(first_deps) - 1):
        for second_dep_idx in range(len(second_deps) - 1):
            first_idx, first_coeff = first_deps[first_dep_idx]
            second_idx, second_coeff = second_deps[second_dep_idx]
            value += first_coeff * second_coeff * free_covariance[first_idx, second_idx]
    return value


def _compute_covariance_if_determinable(
    covariance, free_covariance, free_non_det_idx, row_idx, col_idx, first_deps, second_deps
):
    if all([dep[0] not in free_non_det_idx for dep in second_deps]):
        covariance[row_idx, col_idx] = _compute_parameter_covariance(free_covariance, first_deps, second_deps)


def compute_full_parameter_covariance(simulator: _SimulatorBase, mle: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Computes asymptotic parameter covariance matrix from Maximum Likelihood theory for all parameters. The matrix is
    based on the asymptotic free parameter covariance matrix. The algorithm is stable with regard to non-identifiable
    parameters.

    :param simulator:
         Labeling simulator to evaluate the Hessian/Fisher information matrix
    :param mle:
        Maximum Likelihood estimator of the free parameters
    :return:
        covariance matrix estimate, array of non-identifiable parameters
    """
    free_covariance, free_non_det_idx = compute_free_parameter_covariance(simulator, mle)

    parameter_space = simulator.parameter_space
    stationary = isinstance(parameter_space, StationaryParameterSpace)

    net_class = parameter_space.net_flux_classification
    dep_net_params = net_class.dependent
    num_free_net, num_dep_net = len(net_class.free), len(net_class.dependent)

    xch_class = parameter_space.exchange_flux_classification
    dep_xch_params = xch_class.dependent
    num_free_xch, num_dep_xch = len(xch_class.free), len(xch_class.dependent)

    if not stationary:
        pool_class = parameter_space.pool_size_classification
        dep_pool_params = pool_class.dependent
        num_free_pool, num_dep_pool = len(pool_class.free), len(pool_class.dependent)

    num_all_params = parameter_space.num_parameters
    num_constr_params = len(net_class.constraint) + len(xch_class.constraint)
    if not stationary:
        num_constr_params += len(pool_class.constraint)
    covariance = np.zeros((num_all_params - num_constr_params, num_all_params - num_constr_params))
    non_det_idx = []

    # Compute full covariance matrix:
    #
    # First compute upper triangular, then mirror at diagonal. Use the following rules:
    # 1. Paste values from free parameter covariance matrix
    # 2. cov(sum_i a_i*X_i, sum_j b_j*X_j) = sum_i sum_j a_i*b_j*cov(X_i, X_j) for dependent parameters

    for row_idx in range(num_free_net):
        if row_idx in free_non_det_idx:
            non_det_idx.append(row_idx)
            continue

        curr_deps = [(row_idx, 1.0), (-1, 0.0)]

        covariance[row_idx, row_idx:num_free_net] = free_covariance[row_idx, row_idx:num_free_net]
        col_offset = num_free_net
        for col_idx in range(col_offset, col_offset + num_dep_net):
            _compute_covariance_if_determinable(
                covariance,
                free_covariance,
                free_non_det_idx,
                row_idx,
                col_idx,
                curr_deps,
                dep_net_params[col_idx - col_offset][1],
            )

        col_offset += num_dep_net
        covariance[row_idx, col_offset : col_offset + num_free_xch] = covariance[
            row_idx, num_free_net : num_free_net + num_free_xch
        ]
        col_offset += num_free_xch
        for col_idx in range(col_offset, col_offset + num_dep_xch):
            _compute_covariance_if_determinable(
                covariance,
                free_covariance,
                free_non_det_idx,
                row_idx,
                col_idx,
                curr_deps,
                dep_xch_params[col_idx - col_offset][1],
            )

        if not stationary:
            col_offset += num_dep_xch
            covariance[row_idx, col_offset : col_offset + num_free_pool] = free_covariance[
                row_idx, num_free_net + num_free_xch :
            ]
            col_offset += num_free_pool
            for col_idx in range(col_offset, col_offset + num_dep_pool):
                _compute_covariance_if_determinable(
                    covariance,
                    free_covariance,
                    free_non_det_idx,
                    row_idx,
                    col_idx,
                    curr_deps,
                    dep_pool_params[col_idx - col_offset][1],
                )

    row_offset = num_free_net
    for row_idx in range(row_offset, row_offset + num_dep_net):
        curr_deps = dep_net_params[row_idx - row_offset][1]
        if any([dep[0] in free_non_det_idx for dep in curr_deps]):
            non_det_idx.append(row_idx)
            continue

        col_offset = row_offset
        for col_idx in range(row_idx, col_offset + num_dep_net):
            _compute_covariance_if_determinable(
                covariance,
                free_covariance,
                free_non_det_idx,
                row_idx,
                col_idx,
                curr_deps,
                dep_net_params[col_idx - col_offset][1],
            )

        col_offset += num_dep_net
        for col_idx in range(col_offset, col_offset + num_free_xch):
            _compute_covariance_if_determinable(
                covariance,
                free_covariance,
                free_non_det_idx,
                row_idx,
                col_idx,
                curr_deps,
                [(num_free_net + (col_idx - col_offset), 1.0), (-1, 0.0)],
            )

        col_offset += num_free_xch
        for col_idx in range(col_offset, col_offset + num_dep_xch):
            _compute_covariance_if_determinable(
                covariance,
                free_covariance,
                free_non_det_idx,
                row_idx,
                col_idx,
                curr_deps,
                dep_xch_params[col_idx - col_offset][1],
            )

        if not stationary:
            col_offset += num_dep_xch
            for col_idx in range(col_offset, col_offset + num_free_pool):
                _compute_covariance_if_determinable(
                    covariance,
                    free_covariance,
                    free_non_det_idx,
                    row_idx,
                    col_idx,
                    curr_deps,
                    [(num_free_net + num_free_xch + (col_idx - col_offset), 1.0), (-1, 0.0)],
                )
            col_offset += num_free_pool
            for col_idx in range(col_offset, col_offset + num_dep_pool):
                _compute_covariance_if_determinable(
                    covariance,
                    free_covariance,
                    free_non_det_idx,
                    row_idx,
                    col_idx,
                    curr_deps,
                    dep_pool_params[col_idx - col_offset][1],
                )

    row_offset += num_dep_net
    for row_idx in range(row_offset, row_offset + num_free_xch):
        if row_idx in free_non_det_idx:
            non_det_idx.append(row_idx)
            continue

        free_param_idx = num_free_net + (row_idx - row_offset)
        curr_deps = [(free_param_idx, 1.0), (-1, 0.0)]

        col_offset = row_offset
        covariance[row_idx, row_idx : col_offset + num_free_xch] = free_covariance[
            free_param_idx, free_param_idx : num_free_net + num_free_xch
        ]
        col_offset += num_free_xch
        for col_idx in range(col_offset, col_offset + num_dep_xch):
            _compute_covariance_if_determinable(
                covariance,
                free_covariance,
                free_non_det_idx,
                row_idx,
                col_idx,
                curr_deps,
                dep_xch_params[col_idx - col_offset][1],
            )

        if not stationary:
            col_offset += num_dep_xch
            covariance[row_idx, col_offset : col_offset + num_free_pool] = free_covariance[
                free_param_idx, num_free_net + num_free_xch :
            ]
            col_offset += num_free_pool
            for col_idx in range(col_offset, col_offset + num_dep_pool):
                _compute_covariance_if_determinable(
                    covariance,
                    free_covariance,
                    free_non_det_idx,
                    row_idx,
                    col_idx,
                    curr_deps,
                    dep_pool_params[col_idx - col_offset][1],
                )

    row_offset += num_free_xch
    for row_idx in range(row_offset, row_offset + num_dep_xch):
        curr_deps = dep_xch_params[row_idx - row_offset][1]

        if any([dep[0] in free_non_det_idx for dep in curr_deps]):
            non_det_idx.append(row_idx)
            continue

        col_offset = row_offset
        for col_idx in range(row_idx, col_offset + num_dep_xch):
            _compute_covariance_if_determinable(
                covariance,
                free_covariance,
                free_non_det_idx,
                row_idx,
                col_idx,
                curr_deps,
                dep_xch_params[col_idx - col_offset][1],
            )

        if not stationary:
            col_offset += num_dep_xch
            for col_idx in range(col_offset, col_offset + num_free_pool):
                _compute_covariance_if_determinable(
                    covariance,
                    free_covariance,
                    free_non_det_idx,
                    row_idx,
                    col_idx,
                    curr_deps,
                    [(num_free_net + num_free_xch + (col_idx - col_offset), 1.0), (-1, 0.0)],
                )
            col_offset += num_free_pool
            for col_idx in range(col_offset, col_offset + num_dep_pool):
                _compute_covariance_if_determinable(
                    covariance,
                    free_covariance,
                    free_non_det_idx,
                    row_idx,
                    col_idx,
                    curr_deps,
                    dep_pool_params[col_idx - col_offset][1],
                )

    if not stationary:
        row_offset += num_dep_xch
        for row_idx in range(row_offset, row_offset + num_free_pool):
            if row_idx in free_non_det_idx:
                non_det_idx.append(row_idx)
                continue

            free_param_idx = num_free_net + num_free_xch + (row_idx - row_offset)
            curr_deps = [(free_param_idx, 1.0), (-1, 0.0)]

            col_offset = row_offset
            covariance[row_idx, row_idx : col_offset + num_free_pool] = free_covariance[free_param_idx, free_param_idx:]
            col_offset += num_free_pool
            for col_idx in range(col_offset, num_all_params - num_constr_params):
                _compute_covariance_if_determinable(
                    covariance,
                    free_covariance,
                    free_non_det_idx,
                    row_idx,
                    col_idx,
                    curr_deps,
                    dep_pool_params[col_idx - col_offset][1],
                )

        row_offset += num_free_pool
        for row_idx in range(row_offset, row_offset + num_dep_pool):
            curr_deps = dep_pool_params[row_idx - row_offset][1]

            if any([dep[0] in free_non_det_idx for dep in curr_deps]):
                non_det_idx.append(row_idx)
                continue

            col_offset = row_offset
            for col_idx in range(row_idx, col_offset + num_dep_pool):
                _compute_covariance_if_determinable(
                    covariance,
                    free_covariance,
                    free_non_det_idx,
                    row_idx,
                    col_idx,
                    curr_deps,
                    dep_pool_params[col_idx - col_offset][1],
                )

    # Symmetrize covariance matrix
    lower_idx = np.tril_indices(covariance.shape[0], -1)
    covariance[lower_idx] = covariance.T[lower_idx]

    return covariance, np.array(non_det_idx)


def _compute_optimum(
    name: str,
    next_value: float,
    max_obj_value: float,
    mle_all_dict: Dict[str, float],
    network_data: NetworkData,
    configuration: MeasurementConfiguration,
    bounds: Dict[str, Tuple[float, float]],
    **kwargs,
):
    net_constr = configuration.net_flux_constraints
    xch_constr = configuration.exchange_flux_constraints
    pool_constr = configuration.pool_size_constraints

    if name.endswith(".n"):
        stripped_name = name[:-2]
        def_constr = [constr for constr in net_constr.definition_constraints] + [
            DefinitionConstraint("profile_likelihood", stripped_name, next_value)
        ]
        net_constr = ParameterConstraints(
            def_constr, net_constr.equality_constraints, net_constr.inequality_constraints
        )
    elif name.endswith(".x"):
        stripped_name = name[:-2]
        def_constr = [constr for constr in xch_constr.definition_constraints] + [
            DefinitionConstraint("profile_likelihood", stripped_name, next_value)
        ]
        xch_constr = ParameterConstraints(
            def_constr, xch_constr.equality_constraints, xch_constr.inequality_constraints
        )
    else:
        def_constr = [constr for constr in pool_constr.definition_constraints] + [
            DefinitionConstraint("profile_likelihood", name, next_value)
        ]
        pool_constr = ParameterConstraints(
            def_constr, pool_constr.equality_constraints, pool_constr.inequality_constraints
        )

    new_config = MeasurementConfiguration(
        configuration.name,
        configuration.comment,
        configuration.stationary,
        configuration.substrates,
        configuration.measurements,
        net_constr,
        xch_constr,
        pool_constr,
        [],
    )
    simulator = create_simulator_from_data(network_data, new_config)
    simulator.parameter_space.constraint_violation_tolerance = 1e-1
    ineq_sys = simulator.parameter_space.inequality_system
    ineq_constr_matrix = ineq_sys.matrix
    ineq_constr_bound = ineq_sys.bound
    if bounds is not None and len(bounds) != 0:
        bound_lhs, bound_rhs = get_inequalities_from_bounds(
            simulator, dict(filter(lambda item: item[0] != name, bounds.items()))
        )
        ineq_constr_matrix = np.row_stack((ineq_constr_matrix, bound_lhs))
        ineq_constr_bound = np.concatenate((ineq_constr_bound, bound_rhs))
    mle = compute_closest_interior_point(
        np.array([mle_all_dict[n] for n in simulator.parameter_space.free_parameter_names]),
        ineq_constr_matrix,
        ineq_constr_bound,
    )

    def check_if_lower(
        alg_mod, iter_count, obj_value, inf_pr, inf_du, mu, d_norm, reguralization_size, alpha_du, alpha_pr, ls_trials
    ):
        if obj_value < max_obj_value:
            return False
        else:
            return True

    options = {
        "tol": 1e-3,
        "acceptable_tol": 1e-2,
        "max_iter": 500,
        "acceptable_iter": 50,
        "hessian_approximation": "limited-memory",
        "jac_d_constant": "yes",
        "bound_relax_factor": 0.0,
        "mu_strategy": "adaptive",
        "print_level": 0,
    }
    mfa_problem = IpoptOptimizationProblem(simulator, ineq_constr_matrix)
    mfa_problem.intermediate = check_if_lower
    nonlinear_problem = cyipopt.Problem(
        n=ineq_constr_matrix.shape[1], m=ineq_constr_bound.shape[0], problem_obj=mfa_problem, cu=ineq_constr_bound
    )
    try:
        options.update(kwargs)
        for name in options:
            nonlinear_problem.add_option(name, options[name])
    except Exception as e:
        raise IpoptError(e.args)

    _, info = nonlinear_problem.solve(mle)
    return info["obj_val"]


def _run_binary_search(
    name: str,
    extreme_value: float,
    max_obj_value: float,
    mle_all_dict: Dict[str, float],
    network_data: NetworkData,
    configuration: MeasurementConfiguration,
    bounds: Dict[str, Tuple[float, float]],
    rel_tol: float,
    abs_tol: float,
    **kwargs,
):
    current_value = mle_all_dict[name]
    next_value = (current_value + extreme_value) / 2
    while (
        abs((extreme_value - current_value) / current_value) > rel_tol or abs(extreme_value - current_value) > abs_tol
    ):
        obj_value = _compute_optimum(
            name, next_value, max_obj_value, mle_all_dict, network_data, configuration, bounds, **kwargs
        )
        if obj_value < max_obj_value:
            current_value = next_value
        else:
            extreme_value = next_value
        next_value = (current_value + extreme_value) / 2
    return current_value


def _compute_effective_bounds(
    ineq_matrix: np.ndarray, ineq_bound: np.ndarray, obj_coeffs: List[Tuple[int, float]], offset: int, minimize: bool
) -> float:
    objective = np.zeros(ineq_matrix.shape[1])
    for pair in obj_coeffs:
        objective[pair[0]] = pair[1] + offset

    result = optimize.linprog(
        objective if minimize else -objective, bounds=(None, None), A_ub=ineq_matrix, b_ub=ineq_bound
    )
    if result.status != 0:
        raise ValueError(result.message)

    return result.fun if minimize else -result.fun


def _run_single_profile_likelihood(
    name: str,
    curr_bounds: Tuple[float, float],
    max_obj_value: float,
    mle_all_dict,
    network_data: NetworkData,
    configuration: MeasurementConfiguration,
    bounds: Dict[str, Tuple[float, float]],
    rel_tol: float,
    abs_tol: float,
    **kwargs,
):
    lower_bound, upper_bound = curr_bounds
    ci_lower = _run_binary_search(
        name, lower_bound, max_obj_value, mle_all_dict, network_data, configuration, bounds, rel_tol, abs_tol, **kwargs
    )
    ci_upper = _run_binary_search(
        name, upper_bound, max_obj_value, mle_all_dict, network_data, configuration, bounds, rel_tol, abs_tol, **kwargs
    )
    return ci_lower, ci_upper


def run_profile_likelihood_cis(
    network_data: NetworkData,
    configuration: MeasurementConfiguration,
    mle: np.ndarray,
    alpha: float = 0.95,
    names: List[str] = None,
    bounds: Dict[str, Tuple[float, float]] = None,
    num_procs: int = -1,
    rel_tol: float = 1e-3,
    abs_tol: float = 1e-3,
    **kwargs,
):
    r"""
    Run confidence interval estimation based on profile likelihoods for all parameters. A simple binary search is used
    to find to point where the PL threshold is exceeded. For re-optimizing, the interior point optimizer ipopt and its
    Python interface cyipopt are used. ipopt can be configured by passing the appropriate kwargs.
    See A. Wächter and L. T. Biegler (2006), https://link.springer.com/article/10.1007/s10107-004-0559-y.

    :param network_data:
        x3cflux.NetworkData object containing structural information about the metabolic network
    :param configuration:
        x3cflux.MeasurementConfiguration object containing description and data of a labeling measurement
    :param mle:
        Maximum Likelihood estimator of the free parameters
    :param alpha:
        Confidence level of the interval (between 0 and 1)
    :param names:
        Compute profile likelihoods only for a subset of parameters given by name.
    :param bounds:
        Parameter boundary constraints
    :param num_procs:
        Number of parallel workers. If the value is below one, the number of workers is set to the number of available
        CPU's.
    :param rel_tol:
        Relative convergence criterion for binary search.
    :param abs_tol:
        Absolute convergence criterion for binary search.
    :param kwargs:
        Pass ipopt options as kwargs. See https://coin-or.github.io/Ipopt/OPTIONS.html.
    :return:
    """
    assert 0 < alpha < 1

    simulator = create_simulator_from_data(network_data, configuration)
    obj_value = simulator.compute_loss(mle)
    max_obj_value = obj_value + stats.chi2(1).ppf(alpha)
    names_all, mle_all = simulator.parameter_space.parameter_names, simulator.parameter_space.compute_parameters(mle)
    mle_all_dict = {names_all[k]: mle_all[k] for k in range(simulator.parameter_space.num_parameters)}

    # Add given boundary constraints
    ineq_sys = simulator.parameter_space.inequality_system
    ineq_constr_matrix = ineq_sys.matrix
    ineq_constr_bound = ineq_sys.bound
    if bounds is not None and len(bounds) != 0:
        bound_lhs, bound_rhs = get_inequalities_from_bounds(simulator, bounds)
        ineq_constr_matrix = np.row_stack((ineq_constr_matrix, bound_lhs))
        ineq_constr_bound = np.concatenate((ineq_constr_bound, bound_rhs))

    # Produce list of non-constraint parameters or check existing list
    net_class = simulator.parameter_space.net_flux_classification
    xch_class = simulator.parameter_space.exchange_flux_classification
    if isinstance(simulator.parameter_space, NonStationaryParameterSpace):
        pool_class = simulator.parameter_space.pool_size_classification

    non_const_names = get_non_constant_names(simulator)
    if names is None:
        names = non_const_names
    else:
        for name in names:
            if name not in non_const_names:
                raise ValueError(f'Cannot compute likelihood profile of constant parameter "{name}"')

    individual_bounds = []
    for name in names:
        offset = 0
        if name in simulator.parameter_space.free_parameter_names:
            formula = [(simulator.parameter_space.free_parameter_names.index(name), 1), (-1, 0)]
        else:
            if name.endswith(".n"):
                matches = [x[1] for x in net_class.dependent if x[0] == net_class.names.index(name[:-2])]
            elif name.endswith(".x"):
                matches = [x[1] for x in xch_class.dependent if x[0] == xch_class.names.index(name[:-2])]
                offset += len(net_class.free)
            else:
                matches = [x[1] for x in pool_class.dependent if x[0] == pool_class.names.index(name)]
                offset += len(net_class.free) + len(xch_class.free)

            if len(matches) == 0:
                continue
            else:
                formula = matches[0]

        try:
            lower_bound = (
                _compute_effective_bounds(ineq_constr_matrix, ineq_constr_bound, formula[:-1], offset, minimize=True)
                + formula[-1][1]
            )
            upper_bound = (
                _compute_effective_bounds(ineq_constr_matrix, ineq_constr_bound, formula[:-1], offset, minimize=False)
                + formula[-1][1]
            )
            individual_bounds.append((lower_bound, upper_bound))
        except ValueError as e:
            raise ValueError(f'Failed to compute bounds of "{name}": {e}')

    assert num_procs > 0
    result = []
    if num_procs > 1:
        parallel = joblib.Parallel(n_jobs=min(num_procs, len(names)), return_as="generator")
        for output in parallel(
            joblib.delayed(_run_single_profile_likelihood)(
                name,
                individual_bounds[i],
                max_obj_value,
                mle_all_dict,
                network_data,
                configuration,
                bounds,
                rel_tol,
                abs_tol,
                **kwargs,
            )
            for i, name in enumerate(names)
        ):
            result.append(output)
    else:
        for i, name in enumerate(names):
            result.append(
                _run_single_profile_likelihood(
                    name,
                    individual_bounds[i],
                    max_obj_value,
                    mle_all_dict,
                    network_data,
                    configuration,
                    bounds,
                    rel_tol,
                    abs_tol,
                    **kwargs,
                )
            )

    return result


def convert_to_hopsy_problem(
    simulator: _SimulatorBase, bounds: Dict[str, Tuple[float, float]] = None, include_model: bool = True
):
    r"""
    Convenience function to construct hopsy problem from simulator. Useful for interoperability with hopsy.

    :param simulator:
        Labeling simulator for drawing inequality system
    :param bounds:
        Parameter boundary constraints
    :param include_model:
        Include the labeling model in the hopsy.Problem for non-uniform sampling

    :return:
       hopsy.Problem
    """
    ineq_sys = simulator.parameter_space.inequality_system
    ineq_constr_matrix = ineq_sys.matrix
    ineq_constr_bound = ineq_sys.bound
    if bounds is not None and len(bounds) != 0:
        bound_lhs, bound_rhs = get_inequalities_from_bounds(simulator, bounds)
        ineq_constr_matrix = np.row_stack((ineq_constr_matrix, bound_lhs))
        ineq_constr_bound = np.concatenate((ineq_constr_bound, bound_rhs))

    if include_model:
        return hopsy.Problem(A=ineq_constr_matrix, b=ineq_constr_bound, model=HopsyModel(simulator))
    else:
        return hopsy.Problem(A=ineq_constr_matrix, b=ineq_constr_bound)


class HopsyModel:
    r"""
    Wrapper to pass ILE sampling problem to hopsy.
    """

    def __init__(self, simulator: _SimulatorBase):
        r"""
        Create hopsy sampling model.

        :param simulator:
            Labeling simulator to evaluate negative log likelihood, log likelihood gradient and fisher information.
        """
        self.simulator = simulator

    def log_density(self, x):
        r"""
        Compute log likelihood up to a constant. This is equal to
        .. math:: -\frac{1}{2} SSR(\boldsymbol \theta)

        :param x:
            Metabolic parameters
        :return:
            Negative log likelihood value
        """
        return -0.5 * self.simulator.compute_loss(x)

    def log_gradient(self, x):
        r"""
        Compute gradient of the log likelihood. This is equal to
        .. math:: \frac{\partial}{\partial \boldsymbol \theta} \left(-\frac{1}{2} SSR(\boldsymbol \theta)\right)

        :param x:
            Metabolic parameters
        :return:
            og likelihood value
        """
        return -0.5 * self.simulator.compute_loss_gradient(x)

    def log_curvature(self, x):
        r"""
        Compute the expected Fisher information, i.e. the second moment of the score. This is equal to the linearized
        local Hessian of the SSR.

        :param x:
            Metabolic parameters
        :return:
            Local Fisher information matrix
        """
        return self.simulator.compute_linearized_hessian(x)


def run_uniform_sampling(
    simulator: _SimulatorBase,
    num_samples: int,
    bounds: Dict[str, Tuple[float, float]] = None,
    rounding: bool = True,
    **kwargs,
):
    r"""
    Run uniform sampling of the Polytope induces by the metabolic mode. Markov Chain Monte Carlo (MCMC) as implemented
    in the Polytope sampling toolbox hopsy is used and can be configured by passing appropriate kwargs. See
    Paul, R. et al. (2024), https://doi.org/10.1093/bioinformatics/btae430.

    :param simulator:
        Labeling simulator for drawing inequality system
    :param num_samples:
        Number of samples to generate
    :param bounds:
        Parameter boundary constraints
    :param rounding:
        Rounds the polytope before sampling. Rounding significantly increases the efficiency of sampling, but might
        take some time for large models.
    :param kwargs:
        Pass hopsy options as kwargs. See https://modsim.github.io/hopsy/generated/hopsy.sample.html.
    :return:
        Generated samples
    """
    problem = convert_to_hopsy_problem(simulator, bounds=bounds, include_model=False)
    problem.starting_point = hopsy.compute_chebyshev_center(problem)

    if rounding:
        problem = hopsy.round(problem)

    mc = hopsy.MarkovChain(problem, hopsy.UniformCoordinateHitAndRunProposal)
    rng = hopsy.RandomNumberGenerator(seed=42)
    _, samples = hopsy.sample(mc, rng, n_samples=num_samples, **kwargs)

    return samples


def run_non_uniform_sampling(
    simulator: _SimulatorBase,
    num_samples: int,
    starting_point: np.ndarray = None,
    bounds: Dict[str, Tuple[float, float]] = None,
    num_chains: int = 1,
    proposal: hopsy.PyProposal = hopsy.GaussianCoordinateHitAndRunProposal,
    **kwargs,
):
    r"""
    Run non-uniform sampling to estimate the posterior distribution induced by the given labeling data.
    Markov Chain Monte Carlo (MCMC) as implemented in the Polytope sampling toolbox hopsy is used and can be configured
    by passing appropriate kwargs. See Paul, R. et al. (2024), https://doi.org/10.1093/bioinformatics/btae430.

    :param simulator:
         Labeling simulator
    :param num_samples:
        Number of samples to generate
    :param starting_point:
        Point from where to start sampling
    :param bounds:
        Parameter boundary constraints
    :param num_chains:
        Number of Markov chains to run
    :param proposal:
        Proposal to use for Metropolis-Hastings
    :param kwargs:
        Pass hopsy options as kwargs. See https://modsim.github.io/hopsy/generated/hopsy.sample.html.
    :return:
        Generated samples
    """

    problem = convert_to_hopsy_problem(simulator, bounds=bounds, include_model=True)
    if starting_point is None:
        problem.starting_point = hopsy.compute_chebyshev_center(problem)
    else:
        problem.starting_point = starting_point

    mcs, rngs = hopsy.setup(problem, 42, n_chains=num_chains, proposal=proposal)
    _, samples = hopsy.sample(mcs, rngs, n_samples=num_samples, n_procs=num_chains, **kwargs)

    return samples
