import ctypes
import vapoursynth as vs

core = vs.core


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


def apply_fgs(
    clip: vs.VideoNode,
    fgs_file_path: str,
    ignore_chroma: bool = False,
    static: bool = False,
) -> vs.VideoNode:
    """
    Applies Film Grain Synthesis (FGS) to a video clip using dav1d's FGS engine implementation.

    This function parses a standard FGS text file format and applies the film grain to the input clip.

    The FGS engine strictly operates on 8-bit, 10-bit, or 12-bit YUV data (4:2:0, 4:2:2, or 4:4:4).
    If the input clip has an unsupported bit depth or is float, it will be temporarily converted to 12-bit (using void dither if > 12-bit). After processing, it will be restored to its original format.

    Args:
        clip (vs.VideoNode): The input VapourSynth clip.
        fgs_file_path (str): The path to the text file containing the FGS parameters.
        ignore_chroma (bool): If True, grain is only applied to Luma (Chroma is copied).
        static (bool): If True, the seed from the FGS table is used for all frames (if the FGS is dynamic, this behaviour is per Event). If False, the seed rotates using a curated list for each frame.

    Returns:
        vs.VideoNode: The clip with film grain applied (always returned in the same bit depth as the input).
    """
    if not hasattr(core, "fgs") or not hasattr(core.fgs, "FGS"):
        raise RuntimeError("vs_fgs plugin is not loaded correctly")

    if clip.format.color_family != vs.YUV:
        raise ValueError(
            "vsfgs: only YUV color family is supported. Please convert your clip to YUV first."
        )

    original_format = clip.format

    if (
        original_format.bits_per_sample not in (8, 10, 12)
        or original_format.sample_type != vs.INTEGER
    ):
        target_bits = 12
        target_fmt = original_format.replace(
            bits_per_sample=target_bits, sample_type=vs.INTEGER
        ).id

        if (
            original_format.bits_per_sample > 12
            or original_format.sample_type == vs.FLOAT
        ):
            clip = clip.resize.Bicubic(format=target_fmt, dither_type="none")
        else:
            clip = clip.resize.Bicubic(format=target_fmt)

    blocks = []
    current_block = None
    bare_lines = []

    with open(fgs_file_path, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts:
                continue

            if parts[0] == "E":
                current_block = {
                    "lines": [parts],
                    "start_time": int(parts[1]),
                    "end_time": int(parts[2]),
                }
                blocks.append(current_block)
            elif current_block is not None:
                current_block["lines"].append(parts)
            elif parts[0] not in ("filmgrn1",):
                bare_lines.append(parts)

    if not blocks:
        blocks.append({"lines": bare_lines, "start_time": 0, "end_time": float("inf")})

    parsed_blocks = []
    required_tokens = {"p", "sY", "sCb", "sCr", "cY", "cCb", "cCr"}

    for b_idx, b in enumerate(blocks):
        data = Dav1dFilmGrainData()
        found_tokens = set()

        try:
            for parts in b["lines"]:
                token = parts[0]
                found_tokens.add(token)
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
                        data.y_points[i][0] = int(parts[2 + i * 2])
                        data.y_points[i][1] = int(parts[3 + i * 2])
                elif token == "sCb":
                    data.num_uv_points[0] = int(parts[1])
                    for i in range(data.num_uv_points[0]):
                        data.uv_points[0][i][0] = int(parts[2 + i * 2])
                        data.uv_points[0][i][1] = int(parts[3 + i * 2])
                elif token == "sCr":
                    data.num_uv_points[1] = int(parts[1])
                    for i in range(data.num_uv_points[1]):
                        data.uv_points[1][i][0] = int(parts[2 + i * 2])
                        data.uv_points[1][i][1] = int(parts[3 + i * 2])
                elif token == "cY":
                    for i in range(len(parts) - 1):
                        data.ar_coeffs_y[i] = int(parts[1 + i])
                elif token == "cCb":
                    for i in range(len(parts) - 1):
                        data.ar_coeffs_uv[0][i] = int(parts[1 + i])
                elif token == "cCr":
                    for i in range(len(parts) - 1):
                        data.ar_coeffs_uv[1][i] = int(parts[1 + i])
        except (IndexError, ValueError) as e:
            raise ValueError(
                f"vsfgs: malformed parameters in FGS file at Event {b_idx + 1}, line: {' '.join(parts)}"
            ) from e

        missing_tokens = required_tokens - found_tokens
        if missing_tokens:
            raise ValueError(
                f"vsfgs: missing required FGS fields {missing_tokens} in Event {b_idx + 1}"
            )

        data.clip_to_restricted_range = (
            1  # Could be exposed in the signature in the future
        )

        parsed_blocks.append(
            {
                "data_bytes": bytes(data),
                "start_time": b["start_time"],
                "end_time": b["end_time"],
            }
        )

    fps_num = clip.fps.numerator
    fps_den = clip.fps.denominator
    if fps_num == 0:
        raise ValueError(
            "vs_fgs requires a constant framerate clip for dynamic FGS parsing. Please set clip fps."
        )

    timebase_scale = 10000000.0
    fgs_structs_bytes = bytearray()

    import bisect

    start_times = [b["start_time"] for b in parsed_blocks]

    for n in range(clip.num_frames):
        frame_time = (n * fps_den * timebase_scale) / fps_num

        idx = bisect.bisect_right(start_times, frame_time) - 1
        if idx >= 0:
            if frame_time < parsed_blocks[idx]["end_time"]:
                active_bytes = parsed_blocks[idx]["data_bytes"]
            else:
                active_bytes = parsed_blocks[-1]["data_bytes"]
        else:
            active_bytes = parsed_blocks[0]["data_bytes"]

        fgs_structs_bytes.extend(active_bytes)

    fgs_bytes = bytes(fgs_structs_bytes)

    dynamic_seed = 0 if static else 1
    fgs_clip = core.fgs.FGS(clip, fgs_data=fgs_bytes, dynamic_seed=dynamic_seed)

    if original_format.id != clip.format.id:
        fgs_clip = fgs_clip.resize.Bicubic(format=original_format.id)
    if original_format.id != clip.format.id:
        fgs_clip = fgs_clip.resize.Bicubic(format=original_format.id)

    if ignore_chroma:
        return core.std.ShufflePlanes(
            clips=[fgs_clip, clip, clip], planes=[0, 1, 2], colorfamily=vs.YUV
        )
    return fgs_clip
