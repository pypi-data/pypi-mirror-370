import torch.nn as nn
import torchvision.models as models


def mutate_Conv2d(conv: nn.Conv2d, channels: int = 3):
    if conv.in_channels == channels:
        return conv
    else:
        return nn.Conv2d(
            in_channels=channels,
            out_channels=conv.out_channels,
            kernel_size=conv.kernel_size,
            stride=conv.stride,
            padding=conv.padding,
            dilation=conv.dilation,
            groups=conv.groups,
            bias=conv.bias is not None,
            padding_mode=conv.padding_mode,
        )


def mutate_Conv3d(conv: nn.Conv3d, channels: int = 3):
    if conv.in_channels == channels:
        return conv
    else:
        return nn.Conv3d(
            in_channels=channels,
            out_channels=conv.out_channels,
            kernel_size=conv.kernel_size,
            stride=conv.stride,
            padding=conv.padding,
            dilation=conv.dilation,
            groups=conv.groups,
            bias=conv.bias is not None,
            padding_mode=conv.padding_mode,
        )


def mutate_backbone(backbone, channels: int = 3):
    first_key = list(backbone.keys())[0]
    if first_key == "conv1" and isinstance(backbone["conv1"], nn.Conv2d):
        backbone["conv1"] = mutate_Conv2d(backbone["conv1"])
    elif first_key == "0" and isinstance(backbone["0"][0], nn.Conv2d):
        backbone["0"][0] = mutate_Conv2d(backbone["0"][0])
    else:
        raise TypeError("Backbone not recognised, manual mutation advised.")
    return backbone


def mutate_model(model: nn.Module, channels: int = 3) -> nn.Module:
    """Modify and return a model in place to alter the number of input colour channels it takes.

    Args:
        model (torch.nn.Module): A torchvision model to be modified.
        channels (int, optional): The number of input channels desired. Defaults to 3.

    Raises:
        TypeError: _description_

    Returns:
        torch.nn.Module: The original model after modification.
    """
    # Classification Block
    if isinstance(model, models.AlexNet)\
            or isinstance(model, models.DenseNet)\
            or isinstance(model, models.SqueezeNet)\
            or isinstance(model, models.VGG):
        model.features[0] = mutate_Conv2d(model.features[0], channels=channels)
    elif isinstance(model, models.ConvNeXt)\
            or isinstance(model, models.EfficientNet)\
            or isinstance(model, models.MobileNetV2)\
            or isinstance(model, models.MobileNetV3)\
            or isinstance(model, models.SwinTransformer):
        model.features[0][0] = mutate_Conv2d(model.features[0][0], channels=channels)
    elif isinstance(model, models.MNASNet):
        model.layers[0] = mutate_Conv2d(model.layers[0], channels=channels)
    elif isinstance(model, models.RegNet):
        model.stem[0] = mutate_Conv2d(model.stem[0], channels=channels)
    elif isinstance(model, models.MaxVit):
        model.stem[0][0] = mutate_Conv2d(model.stem[0][0], channels=channels)
    elif isinstance(model, models.ResNet):
        model.conv1 = mutate_Conv2d(model.conv1, channels=channels)
    elif isinstance(model, models.ShuffleNetV2):
        model.conv1[0] = mutate_Conv2d(model.conv1[0], channels=channels)
    elif isinstance(model, models.GoogLeNet):
        model.conv1.conv = mutate_Conv2d(model.conv1.conv, channels=channels)
    elif isinstance(model, models.Inception3):
        model.Conv2d_1a_3x3.conv = mutate_Conv2d(model.Conv2d_1a_3x3.conv, channels=channels)
    elif isinstance(model, models.VisionTransformer):
        if isinstance(model.conv_proj, nn.Conv2d):
            model.conv_proj = mutate_Conv2d(model.conv_proj, channels=channels)
        else:
            model.conv_proj[0] = mutate_Conv2d(model.conv_proj[0], channels=channels)
    # Segmentation Block
    elif isinstance(model, models.segmentation.DeepLabV3)\
            or isinstance(model, models.segmentation.FCN)\
            or isinstance(model, models.segmentation.LRASPP):
        mutate_backbone(model.backbone, channels=channels)
    # Detection Block
    elif isinstance(model, models.detection.FasterRCNN)\
            or isinstance(model, models.detection.FCOS)\
            or isinstance(model, models.detection.RetinaNet):
        mutate_backbone(model.backbone.body, channels=channels)
    elif isinstance(model, models.detection.ssd.SSD):
        if isinstance(model.backbone.features[0], nn.Conv2d):
            model.backbone.features[0] = mutate_Conv2d(model.backbone.features[0], channels=channels)
        elif isinstance(model.backbone.features[0][0][0], nn.Conv2d):
            model.backbone.features[0][0][0] = mutate_Conv2d(model.backbone.features[0][0][0], channels=channels)
    # Video Block
    elif isinstance(model, models.video.MViT):
        model.conv_proj = mutate_Conv3d(model.conv_proj, channels=channels)
    elif isinstance(model, models.video.VideoResNet):
        model.stem[0] = mutate_Conv3d(model.stem[0], channels=channels)
    elif isinstance(model, models.video.S3D):
        model.features[0][0][0] = mutate_Conv3d(model.features[0][0][0], channels=channels)
    elif isinstance(model, models.video.SwinTransformer3d):
        model.patch_embed.proj = mutate_Conv3d(model.patch_embed.proj, channels=channels)
    # Optical Flow Block
    elif isinstance(model, models.optical_flow.RAFT):
        model.feature_encoder.convnormrelu[0] = mutate_Conv2d(model.feature_encoder.convnormrelu[0], channels=channels)
    else:
        raise TypeError(f"Model:{type(model)} not recognised, manual mutation advised.")
    return model
