from dataclasses import dataclass
from enum import Enum
from typing import TypeVar, Callable, NamedTuple

from ._utilities import ColourRepresentationTransform
from ..metrics._reference_values import IMAGENET_METRICS, NormalisationParameters


class TransformKey(NamedTuple):
    from_cr: str
    to_cr: str


@dataclass
class RepresentationDataMixin:
    strict_name: str
    channels: int


class ColourRepresentation(RepresentationDataMixin, Enum):
    """The base enumeration of colour representation availabel in the package.

    Attributes:
        has_conversion_from_rgb: A boolean indicating if a conversion from RGB
        exists for this representation.
        conversion_from_rgb: A function that can be used to convert any image
        tensor from RGB to this representation.
        imagenet_metrics: A named tuple containing the metrics required for
        normalisation based on the ImageNet1k dataset.
    """

    GRAYSCALE = "Grayscale", 1
    RGB = "RGB", 3
    XYZ = "CIE XYZ", 3
    CIEXYZ = XYZ
    LAB = "CIE LAB", 3
    CIELAB = LAB
    LUV = "CIE LUV", 3
    CIELUV = LUV
    YUV = "YUV", 3
    YIQ = "YIQ", 3
    YCBCR = "YCbCr", 3
    YPBPR = "YPbPr", 3
    YDBDR = "YDbDr", 3
    RGBCIE = "CIE RGB", 3
    CIERGB = RGBCIE
    HSV = "HSV", 3
    H2SV = "H2SV", 4
    H3SV = "H3SV", 4
    HED = "HED", 3
    HDX = "HDX", 3
    FGX = "FGX", 3
    BEX = "BEX", 3
    RBD = "RBD", 3
    GDX = "GDX", 3
    HAX = "HAX", 3
    BRO = "BRO", 3
    BPX = "BPX", 3
    AHX = "AHX", 3
    HPX = "HPX", 3

    @property
    def has_conversion_from_rgb(self) -> bool:
        return get_rgb_conversion_to(self) is not None

    @property
    def conversion_from_rgb(self) -> ColourRepresentationTransform:
        return get_rgb_conversion_to(self)

    @property
    def normalisation_metrics(self) -> NormalisationParameters:
        return self.imagenet_metrics

    @property
    def imagenet_metrics(self) -> NormalisationParameters:
        return IMAGENET_METRICS[self.name]

    def __hash__(self) -> int:
        return hash(self.strict_name)


_RGB_TO_DICT = dict()
_TO_RGB_DICT = dict()
_ALL_TF_DICT = dict()

T = TypeVar("CRT", bound=ColourRepresentationTransform)


def register_transform(tf: Callable[..., T]) -> Callable[..., T]:
    if tf._from == ColourRepresentation.RGB:
        _RGB_TO_DICT[tf._to] = tf
    elif tf._to is ColourRepresentation.RGB:
        _TO_RGB_DICT[tf._from] = tf
    _ALL_TF_DICT[TransformKey(tf._from, tf._to)] = tf
    return tf


def get_rgb_conversion_to(cr: ColourRepresentation):
    return _RGB_TO_DICT.get(cr, None)
