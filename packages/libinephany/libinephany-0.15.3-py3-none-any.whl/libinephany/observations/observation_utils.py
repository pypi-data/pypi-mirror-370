# ======================================================================================================================
#
# IMPORTS
#
# ======================================================================================================================

from enum import Enum
from itertools import chain
from typing import Any, Callable

import numpy as np
import pandas as pd
import torch
import torch.optim as optim

from libinephany.pydantic_models.schemas.tensor_statistics import TensorStatistics
from libinephany.utils import optim_utils

# ======================================================================================================================
#
# CONSTANTS
#
# ======================================================================================================================

EXP_AVERAGE = "exp_avg"

# ======================================================================================================================
#
# CLASSES
#
# ======================================================================================================================


class StatisticsCallStage(Enum):

    ON_BATCH_END = "on_batch_end"
    ON_OPTIMIZER_STEP = "on_optimizer_step"
    ON_TRAIN_END = "on_train_end"

    FORWARD_HOOK = "forward_hook"


class StatisticStorageTypes(Enum):

    TENSOR_STATISTICS = TensorStatistics.__name__
    FLOAT = float.__name__
    VECTOR = "vector"


# ======================================================================================================================
#
# FUNCTIONS
#
# ======================================================================================================================


def get_exponential_weighted_average(values: list[float]) -> float:
    """
    :param values: List of values to average via EWA.
    :return: EWA of the given values.
    """

    exp_weighted_average = pd.Series(values).ewm(alpha=0.1).mean().iloc[-1]
    assert isinstance(exp_weighted_average, float)

    return exp_weighted_average


def apply_averaging_function_to_tensor_statistics(
    tensor_statistics: list[TensorStatistics], averaging_function: Callable[[list[float]], float]
) -> TensorStatistics:
    """
    :param tensor_statistics: List of statistics models to average over.
    :param averaging_function: Function to average the values with.
    :return: TensorStatistics containing the average over all given tensor statistics.
    """

    fields = TensorStatistics.model_fields.keys()
    averaged_metrics = {
        field: averaging_function([getattr(statistics, field) for statistics in tensor_statistics]) for field in fields
    }

    return TensorStatistics(**averaged_metrics)


def apply_averaging_function_to_dictionary_of_tensor_statistics(
    data: dict[str, list[TensorStatistics]], averaging_function: Callable[[list[float]], float]
) -> dict[str, TensorStatistics]:
    """
    :param data: Dictionary mapping parameter group names to list of TensorStatistics from that parameter group.
    :param averaging_function: Function to average the values with.
    :return: Dictionary mapping parameter group names to TensorStatistics averaged over all statistics in the given
    TensorStatistics models.
    """

    return {
        group: apply_averaging_function_to_tensor_statistics(
            tensor_statistics=metrics, averaging_function=averaging_function
        )
        for group, metrics in data.items()
    }


def apply_averaging_function_to_dictionary_of_metric_lists(
    data: dict[str, list[float]], averaging_function: Callable[[list[float]], float]
) -> dict[str, float]:
    """
    :param data: Dictionary mapping parameter group names to list of metrics from that parameter group.
    :param averaging_function: Function to average the values with.
    :return: Dictionary mapping parameter group names to averages over all metrics from each parameter group.
    """

    return {group: averaging_function(metrics) for group, metrics in data.items()}


def average_tensor_statistics(tensor_statistics: list[TensorStatistics]) -> TensorStatistics:
    """
    :param tensor_statistics: List of TensorStatistics models to average into one model.
    :return: Averages over all given tensor statistics models.
    """

    averaged = {
        field: sum([getattr(statistics_model, field) for statistics_model in tensor_statistics])
        for field in TensorStatistics.model_fields.keys()
    }
    averaged = {field: total / len(tensor_statistics) for field, total in averaged.items()}

    return TensorStatistics(**averaged)


def create_one_hot_observation(vector_length: int, one_hot_index: int | None) -> list[int | float]:
    """
    :param vector_length: Length of the one-hot vector.
    :param one_hot_index: Index of the vector whose element should be set to 1.0, leaving all others as 0.0.
    :return: Constructed one-hot vector in a list.
    """

    if one_hot_index is not None and one_hot_index < 0:
        raise ValueError("One hot indices must be greater than 0.")

    one_hot = np.zeros(vector_length, dtype=np.int8)

    if one_hot_index is not None:
        one_hot[one_hot_index] = 1

    as_list = one_hot.tolist()

    assert isinstance(as_list, list), "One-hot vector must be a list."

    return as_list


def create_one_hot_depth_encoding(agent_controlled_modules: list[str], parameter_group_name: str) -> list[int | float]:
    """
    :param agent_controlled_modules: Ordered list of parameter group names in the inner model.
    :param parameter_group_name: Name of the parameter group to create a depth one-hot vector for.
    :return: Constructed one-hot depth encoding in a list.

    :note: GANNO encodes depths to one-hot vectors of length 3 regardless of the size of the model.
    """

    module_index = agent_controlled_modules.index(parameter_group_name)
    number_of_modules = len(agent_controlled_modules)

    one_hot_index = min(2, (module_index * 3) // number_of_modules)

    return create_one_hot_observation(vector_length=3, one_hot_index=one_hot_index)


def tensor_on_local_rank(tensor: torch.Tensor | None) -> bool:
    """
    :param tensor: Tensor to check whether it is owned by the local rank, partially or entirely.
    :return: Whether the tensor is owned by the local rank.
    """

    valid_tensor = tensor is not None and tensor.numel() > 0
    device_index = tensor.device.index if valid_tensor else None

    xpu_available = torch.xpu.is_available()
    cuda_available = torch.cuda.is_available()

    if valid_tensor and xpu_available and tensor.is_xpu:
        current_device = torch.xpu.current_device()
        return device_index == current_device

    elif valid_tensor and cuda_available and tensor.is_cuda:
        current_device = torch.cuda.current_device()
        return device_index == current_device

    return valid_tensor


def form_update_tensor(
    optimizer: optim.Optimizer, parameters: list[torch.Tensor], parameter_group: dict[str, Any]
) -> None | torch.Tensor:
    """
    :param optimizer: Optimizer to form the update tensor from.
    :param parameters: Parameters to create the update tensor from.
    :param parameter_group: Parameter group within the optimizer the given parameters came from.
    :return: None or the formed update tensor.
    """

    if type(optimizer) in optim_utils.ADAM_OPTIMISERS:
        updates_list = [optimizer.state[p][EXP_AVERAGE].view(-1) for p in parameters if tensor_on_local_rank(p)]
        return torch.cat(updates_list) if updates_list else None

    elif type(optimizer) in optim_utils.SGD_OPTIMISERS:
        return optim_utils.compute_sgd_optimizer_update_stats(
            optimizer=optimizer, parameter_group=parameter_group, parameters=parameters
        )

    else:
        raise NotImplementedError(f"Optimizer {type(optimizer).__name__} is not supported!")


def null_standardizer(value_to_standardize: float, **kwargs) -> float:
    """
    :param value_to_standardize: Value to mock the standardization of.
    :return: Given value to standardize.
    """

    return value_to_standardize


def create_sinusoidal_depth_encoding(
    agent_controlled_modules: list[str], parameter_group_name: str, dimensionality: int
) -> list[int | float]:
    """
    :param agent_controlled_modules: Ordered list of parameter group names in the inner model.
    :param parameter_group_name: Name of the parameter group to create a depth encoding for.
    :param dimensionality: Length of the depth vector.
    :return: Sinusoidal depth encoding.
    """

    assert dimensionality % 2 == 0, "Dimensionality of a sinusoidal depth encoding must be even."

    depth = agent_controlled_modules.index(parameter_group_name)

    positions = np.arange(dimensionality // 2)
    frequencies = 1 / (10000 ** (2 * positions / dimensionality))

    encoding = np.zeros(dimensionality)
    encoding[0::2] = np.sin(depth * frequencies)
    encoding[1::2] = np.cos(depth * frequencies)

    vector = encoding.tolist()

    return vector


def concatenate_lists(lists: list[list[Any]]) -> list[Any]:
    """
    :param lists: Lists to concatenate.
    :return: Concatenated lists.
    """

    return list(chain(*lists))
