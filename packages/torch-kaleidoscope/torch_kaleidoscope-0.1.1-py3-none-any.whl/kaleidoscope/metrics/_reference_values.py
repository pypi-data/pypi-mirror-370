import torch
from collections import namedtuple

NormalisationParameters = namedtuple(
    "NormalisationParameters",
    [
        "mean",
        "std_dev",
    ]
)

IMAGENET_METRICS = {
    'GRAYSCALE': NormalisationParameters(
        torch.Tensor([0.4595]),
        torch.Tensor([0.2165]),
    ),
    'RGB': NormalisationParameters(
        torch.Tensor([0.4849, 0.4570, 0.4060]),
        torch.Tensor([0.2254, 0.2211, 0.2211]),
    ),
    'XYZ': NormalisationParameters(
        torch.Tensor([0.2501, 0.2604, 0.2484]),
        torch.Tensor([0.1967, 0.2082, 0.2190]),
    ),
    'LAB': NormalisationParameters(
        torch.Tensor([48.6236,  1.8921,  8.5784]),
        torch.Tensor([22.1661,  7.9098, 11.5100]),
    ),
    'LUV': NormalisationParameters(
        torch.Tensor([48.6236,  6.6841,  8.6115]),
        torch.Tensor([22.1661, 13.0704, 13.6248]),
    ),
    'YUV': NormalisationParameters(
        torch.Tensor([0.4595, -0.0263, 0.0223]),
        torch.Tensor([0.2165,  0.0383, 0.0512]),
    ),
    'YIQ': NormalisationParameters(
        torch.Tensor([0.4595, 0.0330, -0.0099]),
        torch.Tensor([0.2165, 0.0582,  0.0261]),
    ),
    'YCBCR': NormalisationParameters(
        torch.Tensor([116.6385, 121.2371, 132.0575]),
        torch.Tensor([ 47.4224,   9.8264,   9.3094]),  # noqa: E201
    ),
    'YPBPR': NormalisationParameters(
        torch.Tensor([0.4595, -0.0302, 0.0181]),
        torch.Tensor([0.2165,  0.0439, 0.0416]),
    ),
    'YDBDR': NormalisationParameters(
        torch.Tensor([0.4595, -0.0805, -0.0483]),
        torch.Tensor([0.2165,  0.1170,  0.1108]),
    ),
    'RGBCIE': NormalisationParameters(
        torch.Tensor([0.0726, 0.0832, 0.0795]),
        torch.Tensor([0.0336, 0.0400, 0.0422]),
    ),
    'HSV': NormalisationParameters(
        torch.Tensor([0.2902, 0.3193, 0.5260]),
        torch.Tensor([0.2074, 0.1837, 0.2254]),
    ),
    'H2SV': NormalisationParameters(
        torch.Tensor([0.2404, 0.3047, 0.3193, 0.5260]),
        torch.Tensor([0.4230, 0.5106, 0.1837, 0.2254]),
    ),
    'H3SV': NormalisationParameters(
        torch.Tensor([0.3022, 0.0867, 0.4206, 0.5116]),
        torch.Tensor([0.2049, 0.1710, 0.1847, 0.2052]),
    ),
    'HED': NormalisationParameters(
        torch.Tensor([0.0844, 0.0027, 0.1025]),
        torch.Tensor([0.0798, 0.0097, 0.0792]),
    ),
    'HDX': NormalisationParameters(
        torch.Tensor([0.0646, 0.0993, 0.0373]),
        torch.Tensor([0.0636, 0.0770, 0.0344]),
    ),
    'FGX': NormalisationParameters(
        torch.Tensor([0.1084, 0.0393, 0.0006]),
        torch.Tensor([0.0809, 0.0383, 0.0017]),
    ),
    'BEX': NormalisationParameters(
        torch.Tensor([0.0903, 0.0581, 0.0864]),
        torch.Tensor([0.0724, 0.0460, 0.0651]),
    ),
    'RBD': NormalisationParameters(
        torch.Tensor([0.0057, 0.0717, 0.1270]),
        torch.Tensor([0.0196, 0.0674, 0.0987]),
    ),
    'GDX': NormalisationParameters(
        torch.Tensor([0.0472, 0.1234, 0.0076]),
        torch.Tensor([0.0442, 0.0887, 0.0141]),
    ),
    'HAX': NormalisationParameters(
        torch.Tensor([0.0594, 0.1050, 0.0625]),
        torch.Tensor([0.0624, 0.0825, 0.0517]),
    ),
    'BRO': NormalisationParameters(
        torch.Tensor([0.0779, 0.0177, 0.0923]),
        torch.Tensor([0.0652, 0.0251, 0.0700]),
    ),
    'BPX': NormalisationParameters(
        torch.Tensor([0.0657, 0.0970, 0.0523]),
        torch.Tensor([0.0593, 0.0718, 0.0412]),
    ),
    'AHX': NormalisationParameters(
        torch.Tensor([0.0162, 0.1512, 0.1168]),
        torch.Tensor([0.0261, 0.1129, 0.0899]),
    ),
    'HPX': NormalisationParameters(
        torch.Tensor([0.1538, 0.0058, 0.1229]),
        torch.Tensor([0.1167, 0.0152, 0.0940]),
    ),
}
