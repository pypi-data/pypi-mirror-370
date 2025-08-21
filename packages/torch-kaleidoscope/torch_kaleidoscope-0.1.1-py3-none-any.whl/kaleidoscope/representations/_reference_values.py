import torch
from enum import Enum, auto
from .representations import ColourRepresentation


class Illuminant(Enum):
    A = auto()
    B = auto()
    C = auto()
    D50 = auto()
    D55 = auto()
    D65 = auto()
    D75 = auto()
    D93 = auto()
    E = auto()
    F1 = auto()
    F2 = auto()
    F3 = auto()
    F4 = auto()
    F5 = auto()
    F6 = auto()
    F7 = auto()
    F8 = auto()
    F9 = auto()
    F10 = auto()
    F11 = auto()
    F12 = auto()
    LED_B1 = auto()
    LED_B2 = auto()
    LED_B3 = auto()
    LED_B4 = auto()
    LED_B5 = auto()
    LED_BH1 = auto()
    LED_RGB1 = auto()
    LED_V1 = auto()
    LED_V2 = auto()


class Observer(Enum):
    _2 = auto()
    _10 = auto()
    _SK_COMPAT = auto()


rgb_to_x_tensors = {
    ColourRepresentation.YUV: torch.Tensor(
        [[0.299, -0.14714119, 0.61497538],
         [0.587, -0.28886916, -0.51496512],
         [0.114, 0.43601035, -0.10001026]]
    ),
    ColourRepresentation.YIQ: torch.Tensor(
        [[0.299, 0.59590059, 0.21153661],
         [0.587, -0.27455667, -0.52273617],
         [0.114, -0.32134392, 0.31119955]]
    ),
    ColourRepresentation.YCBCR: torch.Tensor(
        [[65.481, -37.797, 112.],
         [128.553, -74.203, -93.786],
         [24.966, 112., -18.214]]
    ),
    ColourRepresentation.YPBPR: torch.Tensor(
        [[0.299, -0.168736, 0.5],
         [0.587, -0.331264, -0.418688],
         [0.114, 0.5, -0.081312]]
    ),
    ColourRepresentation.YDBDR: torch.Tensor(
        [[0.299, -0.45, -1.333],
         [0.587, -0.883, 1.116],
         [0.114, 1.333, 0.217]]
    ),
    ColourRepresentation.XYZ: torch.Tensor(
        [[0.412453, 0.212671, 0.019334],
         [0.357580, 0.715160, 0.119193],
         [0.180423, 0.072169, 0.950227]]
    ),
    ColourRepresentation.RGBCIE: torch.Tensor(
        [[0.13725336, 0.01638562, 0.00329059],
         [0.02629378, 0.14980090, 0.01979351],
         [-0.01466154, 0.01669446, 0.16969164]]
    ),
    ColourRepresentation.HED: torch.Tensor(
        [[1.87798285, -1.00767875, -0.55611587],
         [-0.06590806, 1.13473034, -0.13552180],
         [-0.60190743, -0.48041415, 1.57358813]]
    ),
    ColourRepresentation.HDX: torch.Tensor(
        [[1.20013714, -0.68976718, 1.05605400],
         [0.68523347, 0.02360976, -1.17857552],
         [-0.91780901, 1.50953603, 0.50098658]]
    ),
    ColourRepresentation.FGX: torch.Tensor(
        [[-0.42297697, 1.24783111, 0.17179155],
         [1.31456995, -0.68076187, 0.40618104],
         [0.34108582, -0.04595166, -1.35241449]]
    ),
    ColourRepresentation.BEX: torch.Tensor(
        [[1.27238595, -0.70058191, -0.06873151],
         [-0.13335614, 1.03814101, -0.35754561],
         [0.03240120, 0.26316378, 1.22748923]]
    ),
    ColourRepresentation.RBD: torch.Tensor(
        [[-1.32952976, 1.62200642, 0.26012358],
         [2.12970233, -0.15853912, -1.25707638],
         [-1.10517573, -0.44372481, 2.12219119]]
    ),
    ColourRepresentation.GDX: torch.Tensor(
        [[1.07756698, -0.21523400, 0.04528954],
         [-0.13968985, 0.63330972, -0.90942961],
         [-0.26954216, 0.89780420, 0.65236765]]
    ),
    ColourRepresentation.HAX: torch.Tensor(
        [[1.51369309, -1.01440239, 1.03438389],
         [0.45578754, 0.29161620, -1.32219815],
         [-1.06564617, 1.58763492, 0.90376961]]
    ),
    ColourRepresentation.BRO: torch.Tensor(
        [[1.22676885, -0.84839469, 0.30132219],
         [-0.06556827, 1.53612959, -0.80847704],
         [-0.11643951, -0.51280987, 1.36931157]]
    ),
    ColourRepresentation.BPX: torch.Tensor(
        [[1.12901628, -0.56199110, 0.48367947],
         [0.24230690, 0.59531718, -0.79784924],
         [-0.43642077, 0.92391396, 0.80829698]]
    ),
    ColourRepresentation.AHX: torch.Tensor(
        [[1.77936447, -1.02183020, 0.19629006],
         [-0.96840352, 1.61169732, -1.02449894],
         [-0.71417433, 0.98589349, 1.87825310]]
    ),
    ColourRepresentation.HPX: torch.Tensor(
        [[1.79624856, -1.35324311, -0.53960019],
         [-0.40217090, 1.31464148, -0.19159612],
         [0.49097934, -0.26322550, 1.81718802]]
    )
}


reference_white_tensors = {
    Illuminant.A: {
        Observer._2: torch.Tensor([1.098490612345073, 1.0, 0.35579825745490257]),
        Observer._10: torch.Tensor([1.111420406956693, 1.0, 0.3519978321919493]),
    },
    Illuminant.B: {
        Observer._2: torch.Tensor([0.9909274480248003, 1.0, 0.8531327322886154]),
        Observer._10: torch.Tensor([0.9917777147717607, 1.0, 0.8434930535866175]),
    },
    Illuminant.C: {
        Observer._2: torch.Tensor([0.980705971659919, 1.0, 1.1822494939271255]),
        Observer._10: torch.Tensor([0.9728569189782166, 1.0, 1.1614480488951577]),
    },
    Illuminant.D50: {
        Observer._2: torch.Tensor([0.9642119944211994, 1.0, 0.8251882845188288]),
        Observer._10: torch.Tensor([0.9672062750333777, 1.0, 0.8142801513128616]),
    },
    Illuminant.D55: {
        Observer._2: torch.Tensor([0.956797052643698, 1.0, 0.9214805860173273]),
        Observer._10: torch.Tensor([0.957966568225478, 1.0, 0.9092525159847461]),
    },
    Illuminant.D65: {
        Observer._2: torch.Tensor([0.9504300519709449, 1.0, 1.0888064918092575]),
        Observer._10: torch.Tensor([0.94809667673716, 1.0, 1.0730513595166162]),
        Observer._SK_COMPAT: torch.Tensor([0.95047, 1.0, 1.08883]),
    },
    Illuminant.D75: {
        Observer._2: torch.Tensor([0.9497220898840718, 1.0, 1.226393520724154]),
        Observer._10: torch.Tensor([0.9441713925645873, 1.0, 1.2064272211720228]),
    },
    Illuminant.D93: {
        Observer._2: torch.Tensor([0.9530140352058162, 1.0, 1.4127427552085088]),
        Observer._10: torch.Tensor([0.9428818693206406, 1.0, 1.3856805245814334]),
    },
    Illuminant.E: {
        Observer._2: torch.Tensor([1.0, 1.0, 1.0000300003000029]),
        Observer._10: torch.Tensor([1.0, 1.0, 1.0000300003000029]),
    },
    Illuminant.F1: {
        Observer._2: torch.Tensor([0.92833634773327, 1.0, 1.0366471966080588]),
        Observer._10: torch.Tensor([0.9479126314848475, 1.0, 1.0319139426085402]),
    },
    Illuminant.F2: {
        Observer._2: torch.Tensor([0.9914466146180286, 1.0, 0.6731594233792534]),
        Observer._10: torch.Tensor([1.032450385212207, 1.0, 0.6898973674897232]),
    },
    Illuminant.F3: {
        Observer._2: torch.Tensor([1.0375348719249304, 1.0, 0.49860512300278975]),
        Observer._10: torch.Tensor([1.0896827053543472, 1.0, 0.5196482621855755]),
    },
    Illuminant.F4: {
        Observer._2: torch.Tensor([1.091472637556101, 1.0, 0.38813260928860127]),
        Observer._10: torch.Tensor([1.1496135537697703, 1.0, 0.4096330040436095]),
    },
    Illuminant.F5: {
        Observer._2: torch.Tensor([0.9087197011381077, 1.0, 0.9872288668153252]),
        Observer._10: torch.Tensor([0.9336856859195235, 1.0, 0.9863633709046313]),
    },
    Illuminant.F6: {
        Observer._2: torch.Tensor([0.9730912836358956, 1.0, 0.6019054976181281]),
        Observer._10: torch.Tensor([1.0214812270457367, 1.0, 0.6207361217533753]),
    },
    Illuminant.F7: {
        Observer._2: torch.Tensor([0.950171560440895, 1.0, 1.086296420004251]),
        Observer._10: torch.Tensor([0.9577973300970873, 1.0, 1.0761832524271844]),
    },
    Illuminant.F8: {
        Observer._2: torch.Tensor([0.9641254355400697, 1.0, 0.8233310104529616]),
        Observer._10: torch.Tensor([0.9711455521856479, 1.0, 0.8113470046467626]),
    },
    Illuminant.F9: {
        Observer._2: torch.Tensor([1.0036479708162336, 1.0, 0.678683511708377]),
        Observer._10: torch.Tensor([1.0211634498582807, 1.0, 0.6782561749223917]),
    },
    Illuminant.F10: {
        Observer._2: torch.Tensor([0.9617351192130272, 1.0, 0.8171233257377868]),
        Observer._10: torch.Tensor([0.9900124139487643, 1.0, 0.8313395779257422]),
    },
    Illuminant.F11: {
        Observer._2: torch.Tensor([1.0089889428048684, 1.0, 0.6426166043539363]),
        Observer._10: torch.Tensor([1.038197343964658, 1.0, 0.6555504673652451]),
    },
    Illuminant.F12: {
        Observer._2: torch.Tensor([1.0804628965653669, 1.0, 0.39227516629163484]),
        Observer._10: torch.Tensor([1.1142835561598308, 1.0, 0.4035299745700831]),
    },
    Illuminant.LED_B1: {
        Observer._2: torch.Tensor([1.1181951937224128, 1.0, 0.33398724865129975]),
    },
    Illuminant.LED_B2: {
        Observer._2: torch.Tensor([1.0859920239282153, 1.0, 0.406530408773679]),
    },
    Illuminant.LED_B3: {
        Observer._2: torch.Tensor([1.008863819500403, 1.0, 0.6771420897125975]),
    },
    Illuminant.LED_B4: {
        Observer._2: torch.Tensor([0.9771559109080524, 1.0, 0.8783552255853795]),
    },
    Illuminant.LED_B5: {
        Observer._2: torch.Tensor([0.9635352286773796, 1.0, 1.126699629171817]),
    },
    Illuminant.LED_BH1: {
        Observer._2: torch.Tensor([1.1003443187407773, 1.0, 0.3590752582390555]),
    },
    Illuminant.LED_RGB1: {
        Observer._2: torch.Tensor([1.0821657563524103, 1.0, 0.29256708620280225]),
    },
    Illuminant.LED_V1: {
        Observer._2: torch.Tensor([1.1246290801186942, 1.0, 0.34817012858555896]),
    },
    Illuminant.LED_V2: {
        Observer._2: torch.Tensor([1.00158940397351, 1.0, 0.6474172185430465]),
    },
}


reference_uv_tensors = {
    Illuminant.A: {
        Observer._2: torch.Tensor([0.25597062725900166, 0.5242957061810861]),
        Observer._10: torch.Tensor([0.2589604731853051, 0.5242490249593196]),
    },
    Illuminant.B: {
        Observer._2: torch.Tensor([0.21367332671008574, 0.48516668506457666]),
        Observer._10: torch.Tensor([0.21418074944893462, 0.4859019103600294]),
    },
    Illuminant.C: {
        Observer._2: torch.Tensor([0.20088762188603454, 0.4608895655835952]),
        Observer._10: torch.Tensor([0.1999993556514203, 0.46255368229104576]),
    },
    Illuminant.D50: {
        Observer._2: torch.Tensor([0.20915914598542354, 0.488075320769787]),
        Observer._10: torch.Tensor([0.21014748941647854, 0.4888635065676756]),
    },
    Illuminant.D55: {
        Observer._2: torch.Tensor([0.20443028633277577, 0.4807374175932304]),
        Observer._10: torch.Tensor([0.20506918806448346, 0.48165112275242367]),
    },
    Illuminant.D65: {
        Observer._2: torch.Tensor([0.19783264694160294, 0.46833899527433526]),
        Observer._10: torch.Tensor([0.19785762472495255, 0.46955090820823536]),
        Observer._SK_COMPAT: torch.Tensor([0.19783982482140777, 0.4683363029324097]),
    },
    Illuminant.D75: {
        Observer._2: torch.Tensor([0.19353544244809195, 0.45850754673018174]),
        Observer._10: torch.Tensor([0.19304800432889277, 0.46004148522249994]),
    },
    Illuminant.D93: {
        Observer._2: torch.Tensor([0.18879750359225342, 0.4457378038412941]),
        Observer._10: torch.Tensor([0.1876388976289285, 0.44776289947040876]),
    },
    Illuminant.E: {
        Observer._2: torch.Tensor([0.21052531855430817, 0.47368196674719343]),
        Observer._10: torch.Tensor([0.21052531855430817, 0.47368196674719343]),
    },
    Illuminant.F1: {
        Observer._2: torch.Tensor([0.19504628533695473, 0.47273183160360316]),
        Observer._10: torch.Tensor([0.19910309410627053, 0.4725983670429332]),
    },
    Illuminant.F2: {
        Observer._2: torch.Tensor([0.22018782954498384, 0.4996967150541771]),
        Observer._10: torch.Tensor([0.22813882631070792, 0.4971787182718596]),
    },
    Illuminant.F3: {
        Observer._2: torch.Tensor([0.23669974252900167, 0.5133074898024127]),
        Observer._10: torch.Tensor([0.2469727928370143, 0.5099546695132517]),
    },
    Illuminant.F4: {
        Observer._2: torch.Tensor([0.2530090011380749, 0.5215616342296152]),
        Observer._10: torch.Tensor([0.26460574215666643, 0.5178809156348301]),
    },
    Illuminant.F5: {
        Observer._2: torch.Tensor([0.19262324013910076, 0.47693726654123453]),
        Observer._10: torch.Tensor([0.19768099634931577, 0.47637256144494144]),
    },
    Illuminant.F6: {
        Observer._2: torch.Tensor([0.21893285441167953, 0.5062206708765424]),
        Observer._10: torch.Tensor([0.22847214424594148, 0.503251857148767]),
    },
    Illuminant.F7: {
        Observer._2: torch.Tensor([0.19785903523802897, 0.468528892907501]),
        Observer._10: torch.Tensor([0.19968310293461866, 0.4690835602531382]),
    },
    Illuminant.F8: {
        Observer._2: torch.Tensor([0.20920456538701154, 0.4882251362418422]),
        Observer._10: torch.Tensor([0.21105910525742896, 0.48899259823663865]),
    },
    Illuminant.F9: {
        Observer._2: torch.Tensor([0.22254207197214135, 0.49889969042641447]),
        Observer._10: torch.Tensor([0.2262222634186598, 0.49845114683905384]),
    },
    Illuminant.F10: {
        Observer._2: torch.Tensor([0.20892404929566838, 0.4887823076481934]),
        Observer._10: torch.Tensor([0.21424166753161117, 0.486906775262994]),
    },
    Illuminant.F11: {
        Observer._2: torch.Tensor([0.2250093132993915, 0.5017606570754466]),
        Observer._10: torch.Tensor([0.2306483900214544, 0.4998653488810493]),
    },
    Illuminant.F12: {
        Observer._2: torch.Tensor([0.25043630767643593, 0.5215187805737768]),
        Observer._10: torch.Tensor([0.25726792347534927, 0.5194843131441726]),
    },
    Illuminant.LED_B1: {
        Observer._2: torch.Tensor([0.26125816431763493, 0.5256961155036095]),
    },
    Illuminant.LED_B2: {
        Observer._2: torch.Tensor([0.2510154112055307, 0.5200633731816219]),
    },
    Illuminant.LED_B3: {
        Observer._2: torch.Tensor([0.2236912631767018, 0.49888333035554766]),
    },
    Illuminant.LED_B4: {
        Observer._2: torch.Tensor([0.21000306842589753, 0.4835532371893219]),
    },
    Illuminant.LED_B5: {
        Observer._2: torch.Tensor([0.19924595820819224, 0.4652693462841076]),
    },
    Illuminant.LED_BH1: {
        Observer._2: torch.Tensor([0.2562281656262528, 0.5239390642002176]),
    },
    Illuminant.LED_RGB1: {
        Observer._2: torch.Tensor([0.25522977400655295, 0.530664538351676]),
    },
    Illuminant.LED_V1: {
        Observer._2: torch.Tensor([0.2620117525060491, 0.5241963359834082]),
    },
    Illuminant.LED_V2: {
        Observer._2: torch.Tensor([0.22327201866013166, 0.5015648528152588]),
    },
}
