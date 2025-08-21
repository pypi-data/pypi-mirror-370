import torch
from torch.utils.data import DataLoader, Dataset
from typing import Callable


def iterate_dataset(
    dataset: Dataset,
    collector_fn: Callable[[torch.Tensor], tuple[torch.Tensor]],
    num_workers: int = 0
) -> tuple[torch.Tensor]:
    dataloader = DataLoader(
        dataset=dataset,
        num_workers=num_workers,
        batch_size=None,
    )
    collector_list = []
    for data, _ in dataloader:
        collector_list.append(collector_fn(data))
    collector_tuples = tuple(zip(*collector_list))
    metric_list = []
    for tensor_tuple in collector_tuples:
        metric_list.append(torch.mean(torch.stack(tensor_tuple), 0))
    return tuple(metric_list)


def std_mean_by_colour_channel(sample: torch.Tensor):  # For an assumed (C, H, W) torchvision tensor
    return torch.std_mean(sample, (1, 2))
