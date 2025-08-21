from typing import Tuple, Dict

import cyipopt
import joblib
import numpy as np

from .lib.core import _SimulatorBase
from .utilities import get_inequalities_from_bounds


class IpoptOptimizationProblem:
    r"""
    Wrapper to pass ILE optimization problem to ipopt.
    """

    def __init__(self, simulator: _SimulatorBase, ineq_constr_matrix: np.ndarray):
        r"""
        Create ipopt optimization problem.
        :param simulator:
            Labeling simulator to evaluate SSR and its gradient.
        :param ineq_constr_matrix:
            Matrix of the parameter inequalities
                .. math:: \mathbf{C} \dot \mathbf{\theta} \le \mathbf{d}
        """
        self.simulator = simulator
        self.ineq_system = simulator.parameter_space.inequality_system
        self.ineq_constr_matrix = ineq_constr_matrix

    def objective(self, x):
        r"""
        Returns the scalar value of the SSR given x.
        :param x:
            Metabolic parameters
        :return:
            SSR value
        """
        if not np.all(self.ineq_system.matrix.dot(x) <= self.ineq_system.bound):
            print("constraint violation: ", np.max(self.ineq_system.matrix.dot(x) - self.ineq_system.bound))
        try:
            return self.simulator.compute_loss(x)
        except Exception:
            raise cyipopt.CyIpoptEvaluationError()

    def gradient(self, x):
        r"""
        Returns the gradient of the SSR with respect to x.
        :param x:
            Metabolic parameters
        :return:
            SSR gradient
        """
        if not np.all(self.ineq_system.matrix.dot(x) <= self.ineq_system.bound):
            print("constraint violation: ", np.max(self.ineq_system.matrix.dot(x) - self.ineq_system.bound))
        try:
            return self.simulator.compute_loss_gradient(x)
        except Exception:
            raise cyipopt.CyIpoptEvaluationError()

    def constraints(self, x):
        r"""
        Returns the value of the constraint function.
        :param x:
            Metabolic parameters
        :return:
            Linear inequality RHS value
        """
        return self.ineq_constr_matrix.dot(x)

    def jacobian(self, x):
        """
        Returns the Jacobian of the constraints with respect to x.
        :param x:
            Metabolic parameters
        :return:
            Linear equality constraint matrix (constant)
        """
        return self.ineq_constr_matrix


class IpoptError(Exception):
    r"""
    Error raised from ipopt.
    """

    pass


def run_optimization(
    simulator: _SimulatorBase, starting_point: np.ndarray, bounds: Dict[str, Tuple[float, float]] = None, **kwargs
) -> Tuple[np.ndarray, float]:
    r"""
    Run optimization from given starting point.

    Optimization uses the interior point optimizer ipopt and its Python interface cyipopt. ipopt can be configured by
    passing the appropriate kwargs. See A. Wächter and L. T. Biegler (2006),
    https://link.springer.com/article/10.1007/s10107-004-0559-y.

    :param simulator:
        Labeling simulator to evaluate the SSR and its gradient
    :param starting_point:
        Starting point/initial guess of metabolic parameters. Shape has to be either (N,) or (N, 1) with N being the
        number of metabolic parameters
    :param bounds:
        Parameter boundary constraints
    :param kwargs:
        Pass ipopt options as kwargs. See https://coin-or.github.io/Ipopt/OPTIONS.html.
    :return:
        Optimal parameters and SSR value at the local optimum
    """

    ineq_sys = simulator.parameter_space.inequality_system
    ineq_constr_matrix = ineq_sys.matrix
    ineq_constr_bound = ineq_sys.bound

    assert (
        len(starting_point.shape) == 1 or (len(starting_point.shape) == 2 and starting_point.shape[1] == 1)
    ) and len(starting_point) == ineq_constr_matrix.shape[1]

    if bounds is not None and len(bounds) != 0:
        bound_lhs, bound_rhs = get_inequalities_from_bounds(simulator, bounds)
        ineq_constr_matrix = np.row_stack((ineq_constr_matrix, bound_lhs))
        ineq_constr_bound = np.concatenate((ineq_constr_bound, bound_rhs))

    # Create optimization problem
    nonlinear_problem = cyipopt.Problem(
        n=ineq_constr_matrix.shape[1],
        m=ineq_constr_matrix.shape[0],
        problem_obj=IpoptOptimizationProblem(simulator, ineq_constr_matrix),
        cu=ineq_constr_bound,
    )

    # Set default options
    options = {
        "tol": 1e-6,  # Relative tolerance for convergence
        "acceptable_tol": 1e-3,  # Relative tolerance for premature convergence
        "hessian_approximation": "limited-memory",  # Quasi-newton approximation of Hessian
        "jac_d_constant": "yes",  # Linear inequality constraints
        "bound_relax_factor": 0.0,  # Hard boundary constraints
        "mu_strategy": "adaptive",  # Update strategy for KKT boundary parameters
        "print_level": 0,  # Print as little as possible
    }

    # Set kwargs options
    try:
        options.update(kwargs)
        for name in options:
            nonlinear_problem.add_option(name, options[name])
    except Exception as e:
        raise IpoptError(e.args)

    # Run optimization
    optimum, info = nonlinear_problem.solve(starting_point)
    if info["status"] == 0:
        return optimum, info["obj_val"]
    elif info["status"] > -5:
        print(
            "Optimization terminated prematurely: {}. Results might be not optimal.".format(
                info["status_msg"].decode("UTF-8")
            )
        )
        return optimum, info["obj_val"]
    else:
        raise IpoptError('Optimization failed: "{}"'.format(info["status_msg"].decode("UTF-8")))


def _run_single_optimization(
    simulator: _SimulatorBase, starting_point: np.ndarray, bounds: Dict[str, Tuple[float, float]], **kwargs
):
    try:
        return run_optimization(simulator, starting_point, bounds, **kwargs)
    except IpoptError as e:
        print(e)
        return starting_point, np.inf


def run_multi_optimization(
    simulator: _SimulatorBase,
    starting_points: np.ndarray,
    bounds: Dict[str, Tuple[float, float]] = None,
    num_procs: int = -1,
    **kwargs,
) -> Tuple[np.ndarray, np.ndarray]:
    r"""
    Run multi-start parallel optimization from given starting points.

    Optimization uses the interior point optimizer ipopt and its Python interface cyipopt. ipopt can be configured by
    passing the appropriate kwargs. See A. Wächter and L. T. Biegler (2006),
    https://link.springer.com/article/10.1007/s10107-004-0559-y.

    :param simulator:
        Labeling simulator to evaluate the SSR and its gradient
    :param starting_points:
        Starting point/initial guess of metabolic parameters. Shape has to be (N, M) with N being the number of
        metabolic parameters and M being the number of multi-starts
    :param bounds:
        Parameter boundary constraints
    :param num_procs:
        Number of processes to use. Defaults to ``multiprocessing.cpu_count()`` and will be reduced if the number of
        multi-starts is lower than ``num_procs``.
    :param kwargs:
        Pass ipopt options as kwargs. See https://coin-or.github.io/Ipopt/OPTIONS.html
    :return:
        Matrix of optimal parameters and vector of SSR values at each local optimum
    """

    assert len(starting_points.shape) == 2
    num_points = starting_points.shape[1]

    assert num_procs > 0
    result = []
    if num_procs > 1:
        parallel = joblib.Parallel(n_jobs=min(num_procs, num_points), return_as="generator")
        for output in parallel(
            joblib.delayed(_run_single_optimization)(simulator, starting_points[:, i], bounds, **kwargs)
            for i in range(num_points)
        ):
            result.append(output)
    else:
        result = []
        for i in range(num_points):
            result.append(run_optimization(simulator, starting_points[:, i], bounds, **kwargs))

    # Collect results
    optima = np.zeros(starting_points.shape)
    obj_vals = np.zeros(num_points)
    for i in range(num_points):
        optima[:, i] = result[i][0]
        obj_vals[i] = result[i][1]

    return optima, obj_vals
