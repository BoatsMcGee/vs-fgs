import vapoursynth as vs
import vsfgs
from vsview import set_output
from vssource import FFMS2
from vsdenoise import bm3d
from vstools import depth

core = vs.core
clip = FFMS2.source(
    file=r"C:\Users\r74mi\Downloads\64Gram Desktop\[CR] Crowned in a Hundred Days S01E10.mkv"
)
clip = core.resize.Bicubic(clip, format=vs.YUV420P16)

clip_d = bm3d(depth(clip, 32), sigma=3, backend=bm3d.Backend.CUDA_RTC)

clip_fgs = vsfgs.apply_fgs(depth(clip_d, 10), "dynamic_fgs_test.txt")

set_output(clip)
set_output(clip_d)
set_output(clip_fgs)
