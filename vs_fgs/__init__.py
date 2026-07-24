import ctypes
import os
import vapoursynth as vs

class Dav1dFilmGrainData(ctypes.Structure):
    _fields_ = [
        ("seed", ctypes.c_uint),
        ("num_y_points", ctypes.c_int),
        ("y_points", (ctypes.c_uint8 * 2) * 14),
        ("chroma_scaling_from_luma", ctypes.c_int),
        ("num_uv_points", ctypes.c_int * 2),
        ("uv_points", ((ctypes.c_uint8 * 2) * 10) * 2),
        ("scaling_shift", ctypes.c_int),
        ("ar_coeff_lag", ctypes.c_int),
        ("ar_coeffs_y", ctypes.c_int8 * 24),
        ("ar_coeffs_uv", (ctypes.c_int8 * 28) * 2),
        ("ar_coeff_shift", ctypes.c_uint64),
        ("grain_scale_shift", ctypes.c_int),
        ("uv_mult", ctypes.c_int * 2),
        ("uv_luma_mult", ctypes.c_int * 2),
        ("uv_offset", ctypes.c_int * 2),
        ("overlap_flag", ctypes.c_int),
        ("clip_to_restricted_range", ctypes.c_int),
    ]

# Automatically load the compiled plugin
core = vs.core
plugin_loaded = False
for ext in [".dll", ".so", ".dylib"]:
    plugin_path = os.path.join(os.path.dirname(__file__), "vs_fgs_plugin" + ext)
    if os.path.exists(plugin_path):
        core.std.LoadPlugin(plugin_path)
        plugin_loaded = True
        break
        
# fallback for python extension naming convention like vs_fgs_plugin.cpython-310-x86_64-linux-gnu.so
if not plugin_loaded:
    for f in os.listdir(os.path.dirname(__file__)):
        if f.startswith("vs_fgs_plugin") and (f.endswith(".so") or f.endswith(".pyd") or f.endswith(".dll")):
            core.std.LoadPlugin(os.path.join(os.path.dirname(__file__), f))
            plugin_loaded = True
            break

def apply_fgs(clip: vs.VideoNode, fgs_file_path: str) -> vs.VideoNode:
    if not hasattr(core, "fgs") or not hasattr(core.fgs, "FGS"):
        raise RuntimeError("vs_fgs plugin is not loaded correctly")

    data = Dav1dFilmGrainData()
    
    with open(fgs_file_path, "r") as f:
        lines = f.read().strip().splitlines()
        
    for line in lines:
        parts = line.strip().split()
        if not parts: continue
        
        token = parts[0]
        if token == "E":
            data.seed = int(parts[4])
        elif token == "p":
            data.ar_coeff_lag = int(parts[1])
            data.ar_coeff_shift = int(parts[2])
            data.grain_scale_shift = int(parts[3])
            data.scaling_shift = int(parts[4])
            data.chroma_scaling_from_luma = int(parts[5])
            data.overlap_flag = int(parts[6])
            data.uv_mult[0] = int(parts[7])
            data.uv_luma_mult[0] = int(parts[8])
            data.uv_offset[0] = int(parts[9])
            data.uv_mult[1] = int(parts[10])
            data.uv_luma_mult[1] = int(parts[11])
            data.uv_offset[1] = int(parts[12])
        elif token == "sY":
            data.num_y_points = int(parts[1])
            for i in range(data.num_y_points):
                data.y_points[i][0] = int(parts[2 + i*2])
                data.y_points[i][1] = int(parts[3 + i*2])
        elif token == "sCb":
            data.num_uv_points[0] = int(parts[1])
            for i in range(data.num_uv_points[0]):
                data.uv_points[0][i][0] = int(parts[2 + i*2])
                data.uv_points[0][i][1] = int(parts[3 + i*2])
        elif token == "sCr":
            data.num_uv_points[1] = int(parts[1])
            for i in range(data.num_uv_points[1]):
                data.uv_points[1][i][0] = int(parts[2 + i*2])
                data.uv_points[1][i][1] = int(parts[3 + i*2])
        elif token == "cY":
            for i in range(len(parts) - 1):
                data.ar_coeffs_y[i] = int(parts[1 + i])
        elif token == "cCb":
            for i in range(len(parts) - 1):
                data.ar_coeffs_uv[0][i] = int(parts[1 + i])
        elif token == "cCr":
            for i in range(len(parts) - 1):
                data.ar_coeffs_uv[1][i] = int(parts[1 + i])
                
    data.clip_to_restricted_range = 1 # Usually 1 for FGS
    
    # Serialize to bytes
    fgs_bytes = bytes(data)
    
    return core.fgs.FGS(clip, fgs_bytes)
