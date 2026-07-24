import vapoursynth as vs
import vsfgs
from vsview import set_output
from vssource import FFMS2
from vstools import depth
from vsdeband import Grainer

core = vs.core
clip = FFMS2.source(
    file=r"C:\Users\r74mi\Downloads\64Gram Desktop\[CR] Crowned in a Hundred Days S01E10.mkv"
)
clip = core.resize.Bicubic(clip, format=vs.YUV420P16)

clip_fgs = vsfgs.apply_fgs(depth(clip, 16), "dynamic_fgs_test.txt")

clip_grain = Grainer.GAUSS(
    clip, strength=(1, 0), static=False, luma_scaling=3, temporal=0.5, planes=0
)

# set_output(clip)
set_output(clip_fgs)
# set_output(clip_grain)
