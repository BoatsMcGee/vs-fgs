import vapoursynth as vs
import vs_fgs

core = vs.core
# Create a dummy 10-bit YUV420 clip
clip = core.std.BlankClip(width=1920, height=1080, format=vs.YUV420P10, length=100)

# Apply FGS
clip_fgs = vs_fgs.apply_fgs(clip, "static_fgs_test.txt")

# Test if we can fetch a frame
frame = clip_fgs.get_frame(0)
print(
    f"Successfully processed frame 0! Plane 0 shape: {frame[0].width}x{frame[0].height}"
)
