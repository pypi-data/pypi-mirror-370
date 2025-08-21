import torch
from typing import Any, Dict
from torchvision.transforms.v2 import Transform

log_floor_reference = torch.tensor(1e-6)


@property
def NotImplementedField(self):
    raise NotImplementedError


class ColourRepresentationTransform(Transform):
    # Use these to define the colour spaces for transforms, crucial for registration to the API
    _from = NotImplementedField
    _to = NotImplementedField

    def __init__(self) -> None:
        super().__init__()


class MultiplicationTransform(ColourRepresentationTransform):
    # Use this to define the multiplication matrix for the final result
    _transform_matrix = NotImplementedField

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        intm = torch.permute(inpt, (1, 2, 0))
        intm = torch.matmul(intm, self._transform_matrix)
        return torch.permute(intm, (2, 0, 1))


class StainSeparationTransform(MultiplicationTransform):
    _transform_matrix = NotImplementedField

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        intm = torch.maximum(inpt, log_floor_reference)
        intm = torch.log(intm)
        intm = intm / torch.log(log_floor_reference)
        intm = super().transform(intm, params)
        intm = torch.maximum(intm, torch.tensor(0))
        return intm
