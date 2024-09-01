#!/bin/bash
# These colors were obtained from colorcet's glasbey_dark colormap
cat > colors.py <<- EOF
[
    [0.843137, 0.0, 0.0],
    [0.54902, 0.235294, 1.0],
    [0.007843, 0.533333, 0.0],
    [0.0, 0.67451, 0.780392],
    [0.905882, 0.647059, 0.0],
    [1.0, 0.498039, 0.819608],
    [0.423529, 0.0, 0.309804],
    [0.345098, 0.231373, 0.0],
    [0.0, 0.341176, 0.34902],
    [0.082353, 0.882353, 0.552941],
    [0.0, 0.0, 0.866667],
    [0.635294, 0.462745, 0.415686],
    [0.737255, 0.717647, 1.0],
    [0.752941, 0.015686, 0.72549],
    [0.392157, 0.329412, 0.45098],
    [0.47451, 0.0, 0.0],
    [0.027451, 0.454902, 0.847059],
    [0.45098, 0.607843, 0.490196],
    [1.0, 0.470588, 0.321569],
    [0.0, 0.294118, 0.0],
    [0.560784, 0.482353, 0.003922],
    [0.952941, 0.0, 0.482353],
    [0.560784, 0.729412, 0.0],
    [0.65098, 0.482353, 0.721569],
    [0.352941, 0.007843, 0.639216],
    [0.890196, 0.686275, 0.686275],
    [0.627451, 0.227451, 0.321569],
    [0.635294, 0.784314, 0.784314],
    [0.619608, 0.294118, 0.0],
    [0.329412, 0.403922, 0.270588],
    [0.733333, 0.764706, 0.537255],
    [0.372549, 0.482353, 0.533333],
    [0.376471, 0.219608, 0.235294],
    [0.513725, 0.533333, 1.0],
    [0.223529, 0.0, 0.0],
    [0.890196, 0.32549, 1.0],
    [0.188235, 0.32549, 0.509804],
    [0.498039, 0.792157, 1.0],
    [0.772549, 0.4, 0.560784],
    [0.0, 0.505882, 0.415686],
    [0.572549, 0.619608, 0.717647],
    [0.8, 0.454902, 0.027451],
    [0.498039, 0.168627, 0.556863],
    [0.0, 0.745098, 0.643137],
    [0.176471, 0.694118, 0.321569],
    [0.305882, 0.2, 1.0],
    [0.0, 0.898039, 0.0],
    [1.0, 0.0, 0.807843],
    [0.784314, 0.345098, 0.282353],
    [0.898039, 0.611765, 1.0],
    [0.113725, 0.631373, 1.0],
    [0.431373, 0.439216, 0.670588],
    [0.784314, 0.603922, 0.411765],
    [0.470588, 0.341176, 0.231373],
    [0.015686, 0.854902, 0.901961],
    [0.756863, 0.639216, 0.768627],
    [1.0, 0.415686, 0.541176],
    [0.733333, 0.0, 0.996078],
    [0.572549, 0.32549, 0.501961],
    [0.623529, 0.007843, 0.454902],
    [0.580392, 0.631373, 0.313725],
    [0.215686, 0.266667, 0.145098],
    [0.686275, 0.427451, 1.0],
    [0.34902, 0.427451, 0.0],
    [1.0, 0.192157, 0.278431],
    [0.513725, 0.501961, 0.341176],
    [0.0, 0.427451, 0.180392],
    [0.537255, 0.337255, 0.686275],
    [0.352941, 0.290196, 0.639216],
    [0.466667, 0.207843, 0.086275],
    [0.52549, 0.764706, 0.603922],
    [0.372549, 0.066667, 0.137255],
    [0.835294, 0.521569, 0.505882],
    [0.643137, 0.160784, 0.094118],
    [0.0, 0.533333, 0.694118],
    [0.796078, 0.0, 0.266667],
    [1.0, 0.627451, 0.337255],
    [0.921569, 0.305882, 0.0],
    [0.423529, 0.592157, 0.0],
    [0.32549, 0.52549, 0.286275],
    [0.458824, 0.352941, 0.0],
    [0.784314, 0.768627, 0.25098],
    [0.572549, 0.827451, 0.439216],
    [0.294118, 0.596078, 0.580392],
    [0.301961, 0.137255, 0.05098],
    [0.380392, 0.203922, 0.360784],
    [0.517647, 0.0, 0.811765],
    [0.545098, 0.0, 0.192157],
    [0.623529, 0.431373, 0.196078],
    [0.67451, 0.517647, 0.6],
    [0.776471, 0.192157, 0.537255],
    [0.007843, 0.329412, 0.219608],
    [0.031373, 0.419608, 0.517647],
    [0.529412, 0.658824, 0.92549],
    [0.392157, 0.4, 0.937255],
    [0.768627, 0.364706, 0.729412],
    [0.003922, 0.623529, 0.439216],
    [0.505882, 0.317647, 0.34902],
    [0.513725, 0.435294, 0.54902],
    [0.701961, 0.752941, 0.854902],
    [0.72549, 0.568627, 0.160784],
    [1.0, 0.592157, 0.698039],
    [0.654902, 0.576471, 0.882353],
    [0.411765, 0.552941, 0.745098],
    [0.298039, 0.313725, 0.003922],
    [0.282353, 0.007843, 0.8],
    [0.380392, 0.0, 0.431373],
    [0.270588, 0.415686, 0.4],
    [0.615686, 0.341176, 0.262745],
    [0.482353, 0.67451, 0.709804],
    [0.803922, 0.517647, 0.741176],
    [0.0, 0.329412, 0.756863],
    [0.482353, 0.184314, 0.309804],
    [0.984314, 0.486275, 0.0],
    [0.203922, 0.752941, 0.0],
    [1.0, 0.611765, 0.533333],
    [0.882353, 0.717647, 0.411765],
    [0.32549, 0.380392, 0.466667],
    [0.360784, 0.227451, 0.486275],
    [0.929412, 0.647059, 0.854902],
    [0.941176, 0.32549, 0.639216],
    [0.364706, 0.494118, 0.411765],
    [0.768627, 0.466667, 0.313725],
    [0.819608, 0.282353, 0.407843],
    [0.431373, 0.0, 0.921569],
    [0.121569, 0.203922, 0.0],
    [0.756863, 0.254902, 0.015686],
    [0.427451, 0.835294, 0.760784],
    [0.27451, 0.439216, 0.623529],
    [0.635294, 0.003922, 0.768627],
    [0.039216, 0.509804, 0.537255],
    [0.686275, 0.65098, 0.003922],
    [0.65098, 0.360784, 0.419608],
    [0.996078, 0.466667, 1.0],
    [0.545098, 0.521569, 0.682353],
    [0.780392, 0.498039, 0.913725],
    [0.603922, 0.670588, 0.521569],
    [0.529412, 0.423529, 0.85098],
    [0.003922, 0.729412, 0.968627],
    [0.686275, 0.368627, 0.823529],
    [0.34902, 0.317647, 0.168627],
    [0.713725, 0.0, 0.372549],
    [0.486275, 0.713725, 0.415686],
    [0.286275, 0.521569, 1.0],
    [0.0, 0.760784, 0.509804],
    [0.823529, 0.584314, 0.670588],
    [0.639216, 0.294118, 0.658824],
    [0.890196, 0.023529, 0.890196],
    [0.086275, 0.639216, 0.0],
    [0.223529, 0.180392, 0.0],
    [0.517647, 0.188235, 0.2],
    [0.368627, 0.584314, 0.666667],
    [0.352941, 0.062745, 0.0],
    [0.482353, 0.27451, 0.0],
    [0.435294, 0.435294, 0.192157],
    [0.2, 0.345098, 0.14902],
    [0.301961, 0.376471, 0.713725],
    [0.635294, 0.584314, 0.392157],
    [0.384314, 0.25098, 0.156863],
    [0.270588, 0.831373, 0.345098],
    [0.439216, 0.666667, 0.815686],
    [0.180392, 0.419608, 0.305882],
    [0.45098, 0.686275, 0.619608],
    [0.992157, 0.082353, 0.0],
    [0.847059, 0.705882, 0.572549],
    [0.478431, 0.537255, 0.231373],
    [0.490196, 0.776471, 0.85098],
    [0.862745, 0.568627, 0.215686],
    [0.92549, 0.380392, 0.368627],
    [0.92549, 0.372549, 0.831373],
    [0.898039, 0.482353, 0.654902],
    [0.65098, 0.423529, 0.596078],
    [0.0, 0.592157, 0.266667],
    [0.729412, 0.372549, 0.133333],
    [0.737255, 0.678431, 0.32549],
    [0.533333, 0.847059, 0.188235],
    [0.529412, 0.207843, 0.45098],
    [0.682353, 0.658824, 0.823529],
    [0.890196, 0.54902, 0.388235],
    [0.819608, 0.694118, 0.92549],
    [0.215686, 0.258824, 0.623529],
    [0.227451, 0.745098, 0.760784],
    [0.4, 0.615686, 0.301961],
    [0.619608, 0.011765, 0.6],
    [0.305882, 0.305882, 0.478431],
    [0.482353, 0.298039, 0.52549],
    [0.764706, 0.207843, 0.192157],
    [0.552941, 0.4, 0.466667],
    [0.666667, 0.0, 0.176471],
    [0.498039, 0.003922, 0.458824],
    [0.003922, 0.509804, 0.301961],
    [0.45098, 0.290196, 0.403922],
    [0.447059, 0.466667, 0.568627],
    [0.431373, 0.0, 0.6],
    [0.627451, 0.729412, 0.321569],
    [0.882353, 0.431373, 0.192157],
    [0.772549, 0.415686, 0.443137],
    [0.427451, 0.356863, 0.588235],
    [0.639216, 0.235294, 0.454902],
    [0.196078, 0.384314, 0.0],
    [0.533333, 0.0, 0.313725],
    [0.2, 0.345098, 0.411765],
    [0.729412, 0.552941, 0.486275],
    [0.098039, 0.34902, 1.0],
    [0.568627, 0.572549, 0.007843],
    [0.172549, 0.545098, 0.835294],
    [0.090196, 0.14902, 1.0],
    [0.129412, 0.827451, 1.0],
    [0.643137, 0.564706, 0.686275],
    [0.545098, 0.427451, 0.309804],
    [0.368627, 0.129412, 0.243137],
    [0.862745, 0.011765, 0.701961],
    [0.435294, 0.341176, 0.792157],
    [0.396078, 0.156863, 0.129412],
    [0.678431, 0.466667, 0.0],
    [0.639216, 0.74902, 0.968627],
    [0.709804, 0.517647, 0.27451],
    [0.592157, 0.219608, 0.862745],
    [0.698039, 0.317647, 0.580392],
    [0.447059, 0.258824, 0.639216],
    [0.529412, 0.560784, 0.819608],
    [0.541176, 0.439216, 0.694118],
    [0.419608, 0.686275, 0.211765],
    [0.352941, 0.478431, 0.788235],
    [0.780392, 0.623529, 1.0],
    [0.337255, 0.517647, 0.101961],
    [0.0, 0.839216, 0.654902],
    [0.509804, 0.278431, 0.223529],
    [0.066667, 0.262745, 0.113725],
    [0.352941, 0.670588, 0.458824],
    [0.568627, 0.356863, 0.003922],
    [0.964706, 0.270588, 0.439216],
    [1.0, 0.592157, 0.011765],
    [0.882353, 0.258824, 0.192157],
    [0.729412, 0.572549, 0.811765],
    [0.203922, 0.345098, 0.301961],
    [0.972549, 0.501961, 0.490196],
    [0.568627, 0.203922, 0.0],
    [0.701961, 0.803922, 0.0],
    [0.180392, 0.623529, 0.827451],
    [0.47451, 0.545098, 0.623529],
    [0.317647, 0.505882, 0.490196],
    [0.756863, 0.211765, 0.843137],
    [0.92549, 0.019608, 0.32549],
    [0.72549, 0.67451, 0.494118],
    [0.282353, 0.439216, 0.196078],
    [0.517647, 0.584314, 0.396078],
    [0.85098, 0.615686, 0.537255],
    [0.0, 0.392157, 0.639216],
    [0.298039, 0.564706, 0.470588],
    [0.560784, 0.380392, 0.596078],
    [1.0, 0.32549, 0.219608],
    [0.654902, 0.258824, 0.231373],
    [0.0, 0.431373, 0.439216],
    [0.596078, 0.517647, 0.243137],
    [0.862745, 0.690196, 0.784314]
]
EOF