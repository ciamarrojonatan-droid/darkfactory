#!/usr/bin/env python3
"""DarkFactory Cinematic 3D LUT Generator.

Generates an industry-standard 33x33x33 .cube LUT for Historical Documentaries:
- Emulates Kodak 2383 / Bleach-Bypass film print stock.
- Gentle toe and shoulder S-curve roll-off.
- Cold War split-toning: Cold green-cyan bunker shadows, warm muted tungsten highlights.
- Controlled 88% desaturation to eliminate artificial AI oversaturation.
- 100% compatible with FFmpeg lut3d, DaVinci Resolve, Premiere Pro, and Final Cut.
"""
import math
from pathlib import Path


def create_historical_documentary_lut(output_path: Path, size: int = 33) -> None:
    """Generate 33x33x33 .cube LUT file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# DarkFactory Historical Documentary Cinematic 3D LUT\n")
        f.write("# Cold War / Kodak 2383 Bleach-Bypass Emulation\n")
        f.write(f"LUT_3D_SIZE {size}\n")
        f.write("DOMAIN_MIN 0.0 0.0 0.0\n")
        f.write("DOMAIN_MAX 1.0 1.0 1.0\n\n")

        for b_idx in range(size):
            b_in = b_idx / (size - 1)
            for g_idx in range(size):
                g_in = g_idx / (size - 1)
                for r_idx in range(size):
                    r_in = r_idx / (size - 1)

                    # 1. Luminance calculation (Rec.709)
                    lum = 0.2126 * r_in + 0.7152 * g_in + 0.0722 * b_in

                    # 2. Filmic S-Curve on luminance (Kodak 2383 contrast curve)
                    # Contrast push with soft toe and shoulder
                    def s_curve(x: float) -> float:
                        # Smooth sigmoid centered at 0.42
                        k = 4.2
                        mid = 0.42
                        sig = 1.0 / (1.0 + math.exp(-k * (x - mid)))
                        # Normalize 0.0 -> 0.0, 1.0 -> 1.0
                        sig0 = 1.0 / (1.0 + math.exp(-k * (-mid)))
                        sig1 = 1.0 / (1.0 + math.exp(-k * (1.0 - mid)))
                        norm_sig = (sig - sig0) / (sig1 - sig0)
                        # Blend 70% film curve, 30% linear
                        return 0.70 * norm_sig + 0.30 * x

                    lum_graded = s_curve(lum)
                    lum_scale = (lum_graded / lum) if lum > 1e-5 else 1.0

                    r_curved = r_in * lum_scale
                    g_curved = g_in * lum_scale
                    b_curved = b_in * lum_scale

                    # 3. Controlled Bleach-Bypass Desaturation (88% saturation)
                    # Blends RGB towards luminance
                    sat_factor = 0.88
                    r_desat = lum_graded + (r_curved - lum_graded) * sat_factor
                    g_desat = lum_graded + (g_curved - lum_graded) * sat_factor
                    b_desat = lum_graded + (b_curved - lum_graded) * sat_factor

                    # 4. Cold War Split-Toning
                    # Shadows (lum < 0.45): subtle cold green-teal undertone (Soviet CRT/bunker)
                    # Highlights (lum > 0.45): subtle warm amber/tungsten glow
                    shadow_weight = max(0.0, 1.0 - (lum_graded / 0.50))
                    highlight_weight = max(0.0, (lum_graded - 0.40) / 0.60)

                    # Shadow tone: Red -3%, Green +3%, Blue +1%
                    r_shadow = r_desat * (1.0 - 0.04 * shadow_weight)
                    g_shadow = g_desat * (1.0 + 0.03 * shadow_weight)
                    b_shadow = b_desat * (1.0 + 0.01 * shadow_weight)

                    # Highlight tone: Red +3%, Green +1%, Blue -3%
                    r_final = r_shadow * (1.0 + 0.035 * highlight_weight)
                    g_final = g_shadow * (1.0 + 0.010 * highlight_weight)
                    b_final = b_shadow * (1.0 - 0.035 * highlight_weight)

                    # Clamp [0.0, 1.0]
                    r_out = max(0.0, min(1.0, r_final))
                    g_out = max(0.0, min(1.0, g_final))
                    b_out = max(0.0, min(1.0, b_final))

                    f.write(f"{r_out:.6f} {g_out:.6f} {b_out:.6f}\n")


if __name__ == "__main__":
    lut_file = Path(__file__).resolve().parent.parent / "data" / "luts" / "cold_war_documentary.cube"
    create_historical_documentary_lut(lut_file)
    print(f"Generated 3D LUT: {lut_file} ({lut_file.stat().st_size} bytes)")
