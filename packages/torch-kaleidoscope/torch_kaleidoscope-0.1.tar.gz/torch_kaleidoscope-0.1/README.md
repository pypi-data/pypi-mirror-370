# torch-kaleidoscope
A python library for providing PyTorch compatible colour representation utilities.

# weights
Pretrained weights for PyTorch networks are available from my research group where they are hosted and downloadable from the following format of URL:
`https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/<network>/<colour_space>.pth`

## available weights
- ResNet
  - 50: [RGB](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet50/rgb.pth), [HSV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet50/hsv.pth), [H2SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet50/h2sv.pth), [L\*a\*b\*](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet50/lab.pth), [L\*u\*v\*](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet50/luv.pth), [YUV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet50/yuv.pth)
  - 101: [RGB](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet101/rgb.pth), [H2SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet101/h2sv.pth)
  - 152: [RGB](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet152/rgb.pth), [H2SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnet152/h2sv.pth)
- ResNeXt
  - 50 32x4d: [RGB](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnext50_32x4d/rgb.pth), [H2SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnext50_32x4d/h2sv.pth)
  - 101 32x8d: [RGB](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnext101_32x8d/rgb.pth), [H2SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/resnext101_32x8d/h2sv.pth)
- EfficientNetV2
  - Small: [RGB](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/efficientnet_v2_s/rgb.pth), [H2SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/efficientnet_v2_s/h2sv.pth)
- ConvNext
  - Large: [RGB](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/convnext_large/rgb.pth), [HSV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/convnext_large/hsv.pth), [H2SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/convnext_large/h2sv.pth), [H3SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/convnext_large/h3sv.pth), [YUV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/convnext_large/yuv.pth)
- Swin Transformer V2
  - Tiny: : [RGB](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/swin_v2_t/rgb.pth), [H2SV](https://cvl.cs.nott.ac.uk/resources/kaleidoscope/backbones/swin_v2_t/h2sv.pth)




# acknowledgements
The work that lead to needing this, as well as huge swathes of the conversions code and testing present in this repository owe their existence to the scikit-image library[[1]](#1). In particular Nicolas Pinto, Ralf Gommers, Travis Oliphant, Matt Terry, Alex Izvorski and everyone else who contributed to the color module. 

# references
<a id="1">[1]</a> 
[scikit-image](https://doi.org/10.7717/peerj.453), the scikit-image team (2014) 