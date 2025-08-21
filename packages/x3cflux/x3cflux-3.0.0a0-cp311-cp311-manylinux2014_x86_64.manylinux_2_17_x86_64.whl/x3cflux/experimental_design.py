import itertools
import xml.etree.ElementTree as ET
from typing import List, Dict, Union, Callable, Any

import numpy as np

from .lib.core import create_simulator_from_data, NetworkData, MeasurementConfiguration, ConstantSubstrate, Substrate
from .statistics import _compute_stable_fisher_inverse


class SubstrateMixtureCollection:
    r"""
    Collection of different substrate labeling mixtures.
    """

    def __init__(self, metabolite_name: str, mixtures: List[Dict[str, float]], costs: List[float]):
        r"""
        Create substrate labeling mixture collection.

        :param metabolite_name:
            Name of the metabolite pool corresponding to the substrate.
        :param mixtures:
            List of labeling mixtures, given as Dict mapping binary labeling strings to fractional content.
        :param costs:
            Costs of each labeling mixture.
        """
        self.metabolite_name = metabolite_name
        self.mixtures = mixtures
        self.costs = costs

    def compute_mix_and_costs(self, fractions: np.ndarray):
        r"""
        Compute combined substrate labeling mixture and its costs given fractions.

        :param fractions:
            Fraction that each mixture is contained in the final mixture. All fractions must sum up to one and each
            fraction must be between 0 and 1.
        :return:
             final substrate mixture and its costs
        """
        mix = {}
        costs = 0.0

        num_mixtures = len(self.mixtures)
        assert len(fractions) == num_mixtures and np.allclose(fractions.sum(), 1.0)

        for k in range(num_mixtures):
            assert 0.0 <= fractions[k] <= 1.0

            mixture_fraction = self.mixtures[k]
            for labeling in mixture_fraction:
                if labeling not in mix:
                    mix.update({labeling: 0})
                mix[labeling] += fractions[k] * mixture_fraction[labeling]
                costs += fractions[k] * self.costs[k]

        return mix, costs


def parse_substrate_mixture_collections(file_name: str):
    r"""
    Parse collection of substrate mixtures from mixture xml file.

    :param file_name:
        Absolute path to the file
    :return:
        List of SubstrateMixtureCollection, containing mixtures given for each substrate pool
    """
    ns = {"fml": "http://www.13cflux.net/fluxml"}
    tree = ET.parse(file_name)
    root = tree.getroot()

    assert root.tag == ("{" + ns["fml"] + "}mixture")
    assert root.find("fml:input", ns) is not None

    substrate_labeling_configs = {}
    for input_elem in root.findall("fml:input", ns):
        name = input_elem.attrib["pool"]

        configs = []
        for labeling in input_elem.findall("fml:label", ns):
            costs = 0.0
            if "costs" in labeling.attrib:
                costs = labeling.attrib["costs"]
            if not np.allclose(float(labeling.text), 0.0):
                configs.append((labeling.attrib["cfg"], float(labeling.text), float(costs)))

        if name not in substrate_labeling_configs:
            substrate_labeling_configs.update({name: []})
        substrate_labeling_configs[name].append(configs)

    substr_mix_collections = []
    for name in substrate_labeling_configs:
        labeling_configs = substrate_labeling_configs[name]
        mixtures = []
        costs = []

        for i, labeling_config in enumerate(labeling_configs):
            mixtures.append({labeling[0]: labeling[1] for labeling in labeling_config})
            costs.append(sum(map(lambda config: config[1] * config[2], labeling_config)))

        substr_mix_collections.append(SubstrateMixtureCollection(name, mixtures, costs))

    return substr_mix_collections


def create_mixed_substrate(substr_mixture: SubstrateMixtureCollection, fractions: np.ndarray, name: str = None):
    r"""
    Create substrate pool from collection of substrate labeling mixtures.

    :param substr_mixture:
        Collection of substrate labeling mixtures from which a final composition is generated.
    :param fractions:
        Fraction that each mixture is contained in the final mixture. All fractions must sum up to one and each
        fraction must be between 0 and 1.
    :param name:
        Optional identifier used for the substrate pool.
    :return:
        Substrate pool as x3cflux.ConstantSubstrate object
    """
    mix, costs = substr_mixture.compute_mix_and_costs(fractions)
    return ConstantSubstrate(name if name else "", substr_mixture.metabolite_name, costs, mix)


def next_fractional_weights(num_mixtures: int, num_ticks: int):
    r"""
    Generator of fractional weights by using equidistant steps for each mixture.

    :param num_mixtures:
        Number of mixtures in the collection
    :param num_ticks:
        Number of equidistant steps (between 0 and 1)
    :return:
        Mixture weight generator
    """
    assert num_mixtures >= 2 and num_ticks >= 2

    dim_simplex = num_mixtures - 1
    step_width = 1.0 / (num_ticks - 1)
    state = np.zeros(dim_simplex)
    end = False
    bary_coords = np.zeros(num_mixtures)

    while not end:
        output = False
        bary_sum = 0.0
        while not output:
            coord_index = 0
            for coord_index in range(dim_simplex):
                bary_coords[coord_index] = step_width * state[coord_index]
                bary_sum += bary_coords[coord_index]
                if bary_sum > 1.0:
                    break

            bary_coords[-1] = 1.0 - bary_sum
            if bary_sum > 1.0:
                state[coord_index:] = num_ticks
            else:
                output = True

            occurrences = np.where(state != num_ticks)[0]
            if len(occurrences) == 0:
                end = True
                break
            coord_index = occurrences[-1]
            state[coord_index] += 1

            state[coord_index + 1 :] = 0

        if not end:
            yield bary_coords.copy()


def compute_mixture_samples(mixture_collections: List[SubstrateMixtureCollection], num_ticks: Union[int, List[int]]):
    r"""
    Compute substrate mixture samples from a simplex according to given granularity.

    :param mixture_collections:
        List of SubstrateMixtureCollection objects defining the mixture components, one for each substrate.
    :param num_ticks:
        The number of ticks used to sample a substrate mixture collection. If given as int, the same number of ticks
        will be used for every substrate pool. Otherwise, a list containing number of ticks for each mixture collection
        must be specified.
    :return:
        substrate mixture samples and associated fractional content of all mixture components
    """
    mix_substrates = []
    if isinstance(num_ticks, list):
        assert len(mixture_collections) == len(num_ticks)
        mix_weights_combs = [
            [weight for weight in next_fractional_weights(len(mixture.mixtures), num_ticks_mix)]
            for mixture, num_ticks_mix in zip(mixture_collections, num_ticks)
        ]
    else:
        mix_weights_combs = [
            [weight for weight in next_fractional_weights(len(mixture.mixtures), num_ticks)]
            for mixture in mixture_collections
        ]
    for weights in itertools.product(*mix_weights_combs):
        mix_substrates.append([create_mixed_substrate(mixture_collections[i], weights[i]) for i in range(len(weights))])

    return mix_substrates, list(itertools.product(*mix_weights_combs))


def create_simulator_from_inputs(
    network_data: NetworkData,
    meas_config: MeasurementConfiguration,
    multi_substrates: List[List[Substrate]],
    fixed_substrates: List[Substrate] = None,
):
    r"""
    Creates simulator for multiple labeling experiments from given measurement configuration, replacing inputs according
    to given substrates. This is predominantly interesting for experimental design, where trying multiple substrate
    mixtures can be reframed as massive set of labeling experiments.

    :param network_data:
        Structural data of underlying metabolic network
    :param meas_config:
        Structural data of 13C measurements:
    :param multi_substrates:
        Substrates lists to simulated simultaneously.
    :param fixed_substrates:
        Optional choice of substrates fixed at each iteration.
    :return:
        Simulator object for all simultaneous substrates.
    """

    fixed_substrates = fixed_substrates if fixed_substrates is not None else []
    multi_meas_configs = [
        MeasurementConfiguration(
            "",
            meas_config.comment,
            meas_config.stationary,
            substrates + fixed_substrates,
            meas_config.measurements,
            meas_config.net_flux_constraints,
            meas_config.exchange_flux_constraints,
            meas_config.pool_size_constraints,
            meas_config.parameter_entries,
        )
        for substrates in multi_substrates
    ]

    return create_simulator_from_data(network_data, multi_meas_configs)


def _compute_d_criterion(jac, stddev):
    cov, nonident_idx = _compute_stable_fisher_inverse(np.diagflat(1.0 / stddev) @ jac)
    return np.linalg.det(np.delete(np.delete(cov, nonident_idx, axis=0), nonident_idx, axis=1))


def _compute_a_criterion(jac, stddevs):
    cov, nonident_idx = _compute_stable_fisher_inverse(np.diagflat(1.0 / stddevs) @ jac)
    return np.trace(np.delete(np.delete(cov, nonident_idx, axis=0), nonident_idx, axis=1))


def _compute_c_criterion(jac, stddevs):
    cov, nonident_idx = _compute_stable_fisher_inverse(np.diagflat(1.0 / stddevs) @ jac)
    return np.diag(np.delete(np.delete(cov, nonident_idx, axis=0), nonident_idx, axis=1)).max()


def _compute_e_criterion(jac, stddevs):
    cov, nonident_idx = _compute_stable_fisher_inverse(np.diagflat(1.0 / stddevs) @ jac)
    _, sv, _ = np.linalg.svd(np.delete(np.delete(cov, nonident_idx, axis=0), nonident_idx, axis=1))
    return sv[sv > 0.0].min() ** 2


def compute_ed_criteria(
    network_data: NetworkData,
    configuration: MeasurementConfiguration,
    free_parameters: np.ndarray,
    substrate_mixtures: List[List[ConstantSubstrate]],
    criterion: Union[str, Callable] = "D",
    batch_size: int = 1,
) -> List[Any]:
    r"""
    Compute statistics from Experimental Design on a grid of substrates mixtures.

    :param network_data:
        Structural data of underlying metabolic network
    :param configuration:
        Structural data of 13C measurements
    :param free_parameters:
        A vector of valid free parameters.
    :param substrate_mixtures:

    :param criterion:
        Criterion to be computed upon the Fisher information matrix (FIM), either as string
        (supported: "D", "A", "C" and "E"). Alternatively, a custom function can be specified taking the jacobian of the
        measurements and standard deviations.
    :param batch_size:
        Number of mixtures for which criteria are computed simultaneously. The actual batch size used might slightly
        deviate if batch_size does not divide num_ticks.
    :return:
        List of tuples that associates fractional content of all mixture components (according to the specified order)
        with the criteria values.
    """
    fixed_substrates = []
    mix_substrate_names = [substr.metabolite_name for substr in substrate_mixtures[0]]
    for substrate in configuration.substrates:
        if substrate.metabolite_name not in mix_substrate_names:
            fixed_substrates.append(substrate)

    if not isinstance(criterion, Callable):
        if isinstance(criterion, str):
            if criterion == "D":
                criterion = _compute_d_criterion
            elif criterion == "A":
                criterion = _compute_a_criterion
            elif criterion == "C":
                criterion = _compute_c_criterion
            elif criterion == "E":
                criterion = _compute_e_criterion
            else:
                raise ValueError(f'"criterion" {criterion} is not supported')
        else:
            raise ValueError(f'{type(criterion)} is not a valid type for "criterion"')

    criteria_values = []
    batch_idx = np.linspace(0, len(substrate_mixtures), len(substrate_mixtures) // batch_size + 1)
    for i in range(len(batch_idx) - 1):
        lower_idx = int(batch_idx[i])
        upper_idx = int(batch_idx[i + 1])

        simulator = create_simulator_from_inputs(
            network_data, configuration, substrate_mixtures[lower_idx:upper_idx], fixed_substrates
        )
        jacobians = simulator.compute_multi_jacobians(free_parameters)
        stddevs = simulator.measurement_standard_deviations  # todo: if available, use measurement
        stddevs_flat = np.concatenate(
            (
                np.concatenate(stddevs[0][: (len(stddevs[0]) // (upper_idx - lower_idx))]),
                stddevs[1][: (len(stddevs[1]) // (upper_idx - lower_idx))],
            )
        )

        for i, jac in enumerate(jacobians):
            criteria_values.append(criterion(jac, stddevs_flat))

    return criteria_values
