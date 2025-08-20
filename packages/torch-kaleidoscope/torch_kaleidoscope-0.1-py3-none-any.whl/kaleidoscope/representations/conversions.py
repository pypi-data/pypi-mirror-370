import math as base_math
import torch
from torchvision.transforms.v2 import Grayscale
from typing import Any, Dict

from .representations import ColourRepresentation, register_transform
from ._utilities import ColourRepresentationTransform, MultiplicationTransform, StainSeparationTransform
from ._reference_values import (
    rgb_to_x_tensors,
    reference_white_tensors,
    reference_uv_tensors,
    Illuminant,
    Observer,
)

lab_luv_delta_cubed = 0.008856451679035631  # (6.0/29)**3
lab_delta_third_root = 7.787037037037036  # 1.0/3*((6.0/29.0)**(-2.0)))
lab_offset = 0.13793103448275862  # (4.0/29)
luv_half_delta_third_root = 903.2962962962961  # (29.0/3.0)**3.0


@register_transform
class GrayscaleTransform(ColourRepresentationTransform, Grayscale):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.GRAYSCALE


@register_transform
class RGBTransform(ColourRepresentationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.RGB

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        return inpt


@register_transform
class HSVTransform(ColourRepresentationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.HSV

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        x_min, v = torch.aminmax(inpt, dim=0)
        c = v - x_min
        h = torch.where(
            # Piecewise for C = 0
            c == 0,
            0.,
            torch.where(
                # Piecewise for V = R
                v == inpt[0],
                (((inpt[1] - inpt[2]) / c) / 6.) % 1.,
                torch.where(
                    # Piecewise for V = G, falling to V = B
                    v == inpt[1],
                    (2. + ((inpt[2] - inpt[0]) / c)) / 6.,
                    (4. + ((inpt[0] - inpt[1]) / c)) / 6.
                )
            )
        )
        s = torch.where(
            v == 0,
            0.,
            c / v
        )
        return torch.stack([h, s, v], dim=0)


@register_transform
class H2SVTransform(HSVTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.H2SV

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        intm = super().transform(inpt, params)
        # Scale back to the range 0-2pi and then take the sin and cos
        h_sin = torch.sin(intm[0] * (2 * base_math.pi))
        h_cos = torch.cos(intm[0] * (2 * base_math.pi))
        return torch.stack([h_sin, h_cos, intm[1], intm[2]], dim=0)


@register_transform
class H3SVTransform(HSVTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.H3SV

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        intm = super().transform(inpt, params)
        # Scale back to the range 0-2pi and then take the sin and cos
        h_sin = torch.sin(intm[0] * (2 * base_math.pi)) * intm[1]
        h_cos = torch.cos(intm[0] * (2 * base_math.pi)) * intm[1]
        return torch.stack([h_sin, h_cos, intm[1], intm[2]], dim=0)


@register_transform
class YUVTransform(MultiplicationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.YUV
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.YUV]


@register_transform
class YIQTransform(MultiplicationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.YIQ
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.YIQ]


@register_transform
class YCbCrTransform(MultiplicationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.YCBCR
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.YCBCR]

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        intm = super().transform(inpt, params)
        intm[0, :, :] += 16.0
        intm[1, :, :] += 128.0
        intm[2, :, :] += 128.0
        return intm


@register_transform
class YPbPrTransform(MultiplicationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.YPBPR
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.YPBPR]


@register_transform
class YDbDrTransform(MultiplicationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.YDBDR
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.YDBDR]


@register_transform
class XYZTransform(MultiplicationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.XYZ
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.XYZ]

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        intm = torch.where(
            inpt > 0.04045,
            torch.pow((inpt + 0.055) / 1.055, 2.4),
            inpt / 12.92
        )
        intm = super().transform(intm, params)
        return intm


@register_transform
class RGBCIETransform(MultiplicationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.RGBCIE
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.RGBCIE]


@register_transform
class LABTransform(XYZTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.LAB

    def __init__(self, illuminant: Illuminant = Illuminant.D65, observer: Observer = Observer._2):
        super().__init__()
        self.illuminant = illuminant
        self.observer = observer

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        intm = super().transform(inpt, params)
        ref_white = reference_white_tensors[self.illuminant][self.observer]
        for i in range(3):
            intm[i, :, :] = intm[i, :, :]/ref_white[i]
        intm = torch.where(
            intm > lab_luv_delta_cubed,
            intm**(1./3),  # Cube root,
            lab_delta_third_root * intm + lab_offset
        )
        return torch.stack(
            [
                (116.0 * intm[1, :, :]) - 16.0,
                500.0 * (intm[0, :, :] - intm[1, :, :]),
                200.0 * (intm[1, :, :] - intm[2, :, :]),
            ],
            dim=0
        )


@register_transform
class LUVTransform(XYZTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.LUV

    def __init__(self, illuminant: Illuminant = Illuminant.D65, observer: Observer = Observer._2):
        super().__init__()
        self.illuminant = illuminant
        self.observer = observer

    def transform(self, inpt: Any, params: Dict[str, Any]) -> Any:
        intm = super().transform(inpt, params)
        ref_white = reference_white_tensors[self.illuminant][self.observer]
        u0, v0 = reference_uv_tensors[self.illuminant][self.observer]
        L = intm[1, :, :] / ref_white[1]
        L = torch.where(
            L > lab_luv_delta_cubed,
            116.0 * (L**(1./3)) - 16.0,  # **(1./3) to get Cube root,
            luv_half_delta_third_root * L
        )
        return torch.stack(
            [
                L,
                self._uf(L, intm, u0),
                self._vf(L, intm, v0)
            ],
            dim=0
        )

    def _uf(self, L, inpt, u0):
        d = self._df(inpt)
        intm = (4.0 * inpt[0, :, :]) / d
        return 13.0 * L * (intm - u0)

    def _vf(self, L, inpt, v0):
        d = self._df(inpt)
        intm = (9.0 * inpt[1, :, :]) / d
        return 13.0 * L * (intm - v0)

    def _df(self, inpt):
        eps = torch.finfo(inpt.dtype).eps
        return inpt[0, :, :] + (15.0 * inpt[1, :, :]) + (3.0 * inpt[2, :, :]) + eps


@register_transform
class HEDTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.HED
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.HED]


@register_transform
class HDXTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.HDX
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.HDX]


@register_transform
class FGXTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.FGX
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.FGX]


@register_transform
class BEXTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.BEX
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.BEX]


@register_transform
class RBDTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.RBD
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.RBD]


@register_transform
class GDXTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.GDX
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.GDX]


@register_transform
class HAXTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.HAX
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.HAX]


@register_transform
class BROTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.BRO
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.BRO]


@register_transform
class BPXTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.BPX
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.BPX]


@register_transform
class AHXTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.AHX
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.AHX]


@register_transform
class HPXTransform(StainSeparationTransform):
    _from = ColourRepresentation.RGB
    _to = ColourRepresentation.HPX
    _transform_matrix = rgb_to_x_tensors[ColourRepresentation.HPX]
