from typing import List, Tuple, Union, Any, Dict

import cvxpy as cp
import hopsy
import numpy as np
from scipy import stats

from .lib.core import (
    _SimulatorBase,
    NetworkData,
    MeasurementConfiguration,
    LabelingMeasurement,
    MeasurementDataSet,
    create_simulator_from_data,
    FluxMeasurement,
    NonStationaryParameterSpace,
)


def get_non_constant_names(simulator: _SimulatorBase) -> List[str]:
    """
    Returns the names of non-constant (i.e. neither explicitly nor implicitly constrained) parameters.

    :param simulator:
        Simulator object
    :return:
        List of names
    """
    net_class = simulator.parameter_space.net_flux_classification
    xch_class = simulator.parameter_space.exchange_flux_classification
    if isinstance(simulator.parameter_space, NonStationaryParameterSpace):
        pool_class = simulator.parameter_space.pool_size_classification

    non_const_names = []
    for name in simulator.parameter_space.parameter_names:
        if name.endswith(".n"):
            idx = net_class.names.index(name[:-2])
            if (
                next(filter(lambda pair: pair[0] == idx, net_class.constraint), None) is None
                and next(filter(lambda pair: pair[0] == idx, net_class.quasi_constraint), None) is None
            ):
                non_const_names.append(name)
        elif name.endswith(".x"):
            idx = xch_class.names.index(name[:-2])
            if (
                next(filter(lambda pair: pair[0] == idx, xch_class.constraint), None) is None
                and next(filter(lambda pair: pair[0] == idx, xch_class.quasi_constraint), None) is None
            ):
                non_const_names.append(name)
        else:
            if (
                next(filter(lambda pair: pair[0] == idx, pool_class.constraint), None) is None
                and next(filter(lambda pair: pair[0] == idx, pool_class.quasi_constraint), None) is None
            ):
                non_const_names.append(name)

    return non_const_names


def get_inequalities_from_bounds(
    simulator: _SimulatorBase, bounds: Dict[str, Tuple[float, float]]
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Turns a list of bounds into a system of linear inequality constraints of a metabolic model (defined by the
    simulator).

    :param simulator:
        Simulator object, whose parameters to bound
    :param bounds:
        Parameter boundary constraints
    :return:
        Matrix and vector of a linear inequality system
    """
    free_parameter_names = simulator.parameter_space.free_parameter_names
    num_free_params = len(free_parameter_names)
    non_constant_names = get_non_constant_names(simulator)

    names = []
    for name in bounds:
        if name in non_constant_names:
            names.append(name)
        else:
            print(f'Bounding constant parameter "{name}" has no effect')
    num_bounds = 2 * len(names)

    net_class = simulator.parameter_space.net_flux_classification
    xch_class = simulator.parameter_space.exchange_flux_classification
    if isinstance(simulator.parameter_space, NonStationaryParameterSpace):
        pool_class = simulator.parameter_space.pool_size_classification

    ineq_constr_matrix = np.zeros((num_bounds, num_free_params))
    ineq_constr_bound = np.zeros(num_bounds)

    for i, name in enumerate(names):
        if name in free_parameter_names:
            ineq_constr_matrix[i, free_parameter_names.index(name)] = 1
            ineq_constr_bound[i] = bounds[name][1]
            ineq_constr_matrix[i + len(names), free_parameter_names.index(name)] = -1
            ineq_constr_bound[i + len(names)] = -bounds[name][0]
        else:
            offset = 0
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
                for j in range(len(formula) - 1):
                    ineq_constr_matrix[i, formula[j][0] + offset] = formula[j][1]
                    ineq_constr_matrix[i + len(names), formula[j][0] + offset] = -formula[j][1]
                ineq_constr_bound[i] = bounds[name][1] - formula[-1][1]
                ineq_constr_bound[i + len(names)] = formula[-1][1] - bounds[name][0]

    return ineq_constr_matrix, ineq_constr_bound


def compute_closest_interior_point(
    point: np.ndarray,
    inequality_matrix: np.ndarray,
    inequality_bound: np.ndarray,
    margin: Union[float, np.ndarray] = 1e-1,
):
    """
    Computes an interior point of the polytope that is closest in 2-norm to the given one.

    This method relies on least squares optimization to compute the closest point. A margin is added to the polytope
    bounds to not ensure that the interior point is not exactly on the boundary. This margin is decreased iteratively
    if the solution fails, starting from 0.1.

    :param point:
        a point with shape (N,)
    :param inequality_matrix:
        inequality matrix (M, N) of the polytope
    :param inequality_bound:
        inequality bound (M,) of the polytope
    :param margin:
        absolute distance to each respective bound. Might also be given as a vector of distances for each bound.
        Default: 0.1
    :return:
        interior point
    :raises:
        Exception if constraints could not be fulfilled even after many attempts
    """
    if np.all(inequality_matrix @ point < inequality_bound):
        return point

    num_constraints, num_params = inequality_matrix.shape

    fixed_mean = cp.Variable(num_params)
    objective = cp.Minimize(cp.sum_squares(np.eye(num_params) @ fixed_mean - point))

    finished = False
    if isinstance(margin, float):
        epsilon_vector = margin * np.ones(num_constraints)
    elif isinstance(margin, np.ndarray) and len(margin.shape) == 1:
        epsilon_vector = margin
    else:
        raise Exception("Type of margin not supported")
    while not finished:
        constraints = [inequality_matrix @ fixed_mean <= inequality_bound - epsilon_vector]
        problem = cp.Problem(objective, constraints)
        result = problem.solve(solver="OSQP")
        finished = type(result) is float and result < float("inf")
        epsilon_vector /= 10.0

    slacks = inequality_bound - inequality_matrix @ fixed_mean.value
    if np.min(slacks) < 0:
        raise Exception(f"Constraints {np.where(np.min(slacks) < 0)[0]} are not satisfied")

    return fixed_mean.value


def _perturb_measurement_group(
    meas_values: np.ndarray, meas_std: np.ndarray, num_samples: int, random_seed: int = None
) -> np.ndarray:
    num_meas = len(meas_values)

    problem = hopsy.Problem(
        np.row_stack((np.identity(num_meas), -np.identity(num_meas))),
        np.concatenate((np.ones(num_meas), np.zeros(num_meas))),
        hopsy.Gaussian(meas_values, np.diagflat(np.square(meas_std))),
    )
    problem = hopsy.add_equality_constraints(problem, np.ones(num_meas).reshape((1, -1)), np.ones(1))
    problem.starting_point = compute_closest_interior_point(
        np.linalg.solve(
            problem.transformation.T @ problem.transformation, problem.transformation.T.dot(meas_values - problem.shift)
        ),
        problem.A,
        problem.b,
        1e-9,
    )

    mc = hopsy.MarkovChain(problem, hopsy.GaussianCoordinateHitAndRunProposal)
    rng = hopsy.RandomNumberGenerator(random_seed if random_seed else 42 * np.random.randint(0, 100))
    mc.proposal.stepsize = np.median(meas_std)
    acc, samples = hopsy.sample(mc, rng, n_samples=num_samples, thinning=2 * num_meas)

    return samples[0]


def compute_perturbed_measurements(
    simulator: _SimulatorBase,
    params: np.ndarray,
    measurement_standard_deviations: Tuple[List[np.ndarray], List[float]] = None,
    num_samples: int = 1,
    random_seed: int = None,
) -> Union[Tuple[List[np.ndarray], List[float]], List[Tuple[List[np.ndarray], List[float]]]]:
    """
    Computes noisy measurements from simulated ones.

    Noise simulation is based on given absolute errors. Errors are assumed to be normally distributed. Constraints are
    considered automatically and Markov Chain Monte Carlo algorithms are used to draw appropriate random numbers. The
    current version does not work for parameter measurements that contain multiple parameters and does not consider
    special error models.

    :param simulator:
        simulator for noise-free measurements
    :param params:
        parameters to simulate noise-free measurements from
    :param measurement_standard_deviations:
        standard deviations, defaults to the given standard deviations from the simulator
    :param num_samples:
        number of noisy measurements to generate
    :param random_seed:
        for deterministic measurement generation
    :return:
        noisy measurement data
    """
    perturbed_measurements = [([], []) for _ in range(num_samples)]

    simulated_measurements = simulator.compute_measurements(params)
    if measurement_standard_deviations is None:
        measurement_standard_deviations = simulator.measurement_standard_deviations

    for i, meas in enumerate(simulated_measurements[0]):
        sim_meas = _perturb_measurement_group(meas, measurement_standard_deviations[0][i], num_samples, random_seed)
        for j in range(num_samples):
            perturbed_measurements[j][0].append(sim_meas[j])

    net_class = simulator.parameter_space.net_flux_classification
    xch_class = simulator.parameter_space.exchange_flux_classification
    if isinstance(simulator.parameter_space, NonStationaryParameterSpace):
        pool_class = simulator.parameter_space.pool_size_classification

    configs = simulator.configurations
    meas_names = [[meas.name for meas in config.measurements] for config in configs]
    for i, meas in enumerate(simulated_measurements[1]):
        meas_name = simulator.measurement_names[1][i]
        mean, std = simulated_measurements[1][i], measurement_standard_deviations[1][i]
        lb, ub = -np.inf, np.inf

        measurement = [
            configs[i].measurements[sub_names.index(meas_name)]
            for i, sub_names in enumerate(meas_names)
            if meas_name in sub_names
        ][0]
        param_name = str(measurement.measurement_formula)
        if isinstance(measurement, FluxMeasurement):
            if measurement.specification.net:
                idx = net_class.names.index(param_name)
                if idx in net_class.bounds:
                    lb, ub = net_class.bounds[idx]
            else:
                idx = xch_class.names.index(param_name)
                if idx in xch_class.bounds:
                    lb, ub = xch_class.bounds[idx]
        else:
            idx = pool_class.names.index(param_name)
            if idx in pool_class.bounds:
                lb, ub = pool_class.bounds[idx]

        sim_meas = stats.truncnorm.rvs(
            loc=mean, scale=std, a=(lb - mean) / std, b=(ub - mean) / std, size=num_samples, random_state=random_seed
        )
        for j in range(num_samples):
            perturbed_measurements[j][1].append(sim_meas[j])

    if num_samples == 1:
        return perturbed_measurements[0]
    else:
        return perturbed_measurements


def create_simulator_from_measurements(
    simulated_measurements: Tuple[List[np.ndarray], List[float]],
    base_simulator: Any = None,
    network_data: NetworkData = None,
    configurations: List[MeasurementConfiguration] = None,
    measurement_names: Tuple[List[str], List[str]] = None,
    measurement_time_stamps: List[List[float]] = None,
    measurement_standard_deviations: Tuple[List[np.ndarray], List[float]] = None,
) -> Any:
    """
    Creates a new simulator object from measurement data.

    :param simulated_measurements:
        measurement data
    :param base_simulator:
        Simulator from which measurements were generated. If supplied, all arguments except simulated_measurements are
        optional.
    :param network_data:
        network data
    :param configurations:
        measurement configurations to copy the data into
    :param measurement_names:
        names of measurements
    :param measurement_time_stamps:
        time stamps of measurements
    :param measurement_standard_deviations:
        standard deviations of measurements
    :return:
        simulator object using given measurement data
    """
    label_meas_values, param_meas_values = simulated_measurements

    if base_simulator is not None:
        if network_data is None:
            network_data = base_simulator.network_data
        if configurations is None:
            configurations = base_simulator.configurations
        if measurement_names is None:
            measurement_names = base_simulator.measurement_names
        if measurement_time_stamps is None:
            measurement_time_stamps = base_simulator.measurement_time_stamps
        if measurement_standard_deviations is None:
            measurement_standard_deviations = base_simulator.measurement_standard_deviations
    else:
        assert (
            network_data is not None
            and configurations is not None
            and measurement_names is not None
            and measurement_time_stamps is not None
            and measurement_standard_deviations is not None
        )

    new_configs = []
    for config in configurations:
        measurement_data = []
        for meas in config.measurements:
            if isinstance(meas, LabelingMeasurement):
                idx = measurement_names[0].index(meas.name)
                offset = 0
                if idx != 0:
                    offset = sum(map(lambda ts: len(ts), measurement_time_stamps[:idx]))
                data = MeasurementDataSet(
                    measurement_time_stamps[idx],
                    label_meas_values[offset : offset + len(measurement_time_stamps[idx])],
                    measurement_standard_deviations[0][offset : offset + len(measurement_time_stamps[idx])],
                    [],
                )
                measurement_data.append(
                    type(meas)(
                        meas.name, meas.auto_scalable, meas.metabolite_name, meas.num_atoms, meas.specification, data
                    )
                )
            else:
                idx = measurement_names[1].index(meas.name)
                measurement_data.append(
                    type(meas)(
                        meas.name,
                        meas.auto_scalable,
                        meas.measurement_formula,
                        meas.specification,
                        param_meas_values[idx],
                        meas.standard_deviation,
                        None,
                    )
                )

        new_configs.append(
            MeasurementConfiguration(
                config.name,
                config.comment,
                config.stationary,
                config.substrates,
                measurement_data,
                config.net_flux_constraints,
                config.exchange_flux_constraints,
                config.pool_size_constraints,
                config.parameter_entries,
            )
        )

    return create_simulator_from_data(network_data, new_configs)
