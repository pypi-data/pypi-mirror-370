import argparse
import sys
import ffmpeg
from pathlib import Path
from typing import Optional


def slowdown(
        in_file: str = "input.mp4",
        out_file: str = "output_slow1.wav",
        speed: float = 0.95,
) -> None:
    out_path = Path(out_file).expanduser()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    (
        ffmpeg
        .input(str(in_file))
        .audio
        .filter("atempo", speed)
        .output(
            str(out_path),
            acodec="pcm_s16le",
            ar=44100,
            ac=2,
        )
        .overwrite_output()
        .run(quiet=True)
    )
    print(f"Done: {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="把音频/视频变速并输出 wav"
    )
    parser.add_argument(
        "input",
        nargs="?",
        default="input.mp4",
        help="输入文件（默认 input.mp4）",
    )
    parser.add_argument(
        "-o", "--output",
        default="output_slow1.wav",
        help="输出 wav 路径（默认 output_slow1.wav）",
    )
    parser.add_argument(
        "-s", "--speed",
        type=float,
        default=0.95,
        help="倍速，<1 放慢，>1 加快（默认 0.95）",
    )
    args = parser.parse_args()
    slowdown(args.input, args.output, args.speed)


if __name__ == "__main__":
    main()
