"""Verify the shipped omp and Alacritty themes as a pair."""

import json
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path
from urllib.request import urlopen

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = (
    "https://raw.githubusercontent.com/can1357/oh-my-pi/v19.0.0/"
    "packages/tui/src/theme/theme-schema.json"
)
ANSI_NAMES = "black red green yellow blue magenta cyan white".split()
DECORATION = {
    "border",
    "borderAccent",
    "borderMuted",
    "bashMode",
    "btwMode",
    "mdCodeBlockBorder",
    "mdHr",
    "mdQuoteBorder",
    "pythonMode",
}


def luminance(color):
    channels = [int(color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return sum(
        weight
        * (value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
        for weight, value in zip((0.2126, 0.7152, 0.0722), channels, strict=True)
    )


def check_contrast(label, foreground, background):
    low, high = sorted((luminance(foreground), luminance(background)))
    ratio = (high + 0.05) / (low + 0.05)
    if ratio < 4.5:
        raise ValueError(f"{label}: {ratio:.2f}:1 contrast; expected at least 4.5:1")


def check_theme(name, schema):
    omp = json.loads((ROOT / f"dist/omp/themes/{name}.json").read_text())
    error = next(schema.iter_errors(omp), None)
    if error is not None:
        raise ValueError(f"{name}: {error.json_path}: {error.message}")
    alacritty = tomllib.loads((ROOT / f"dist/alacritty/{name}.toml").read_text())[
        "colors"
    ]
    foreground = alacritty["primary"]["foreground"]
    background = alacritty["primary"]["background"]
    ansi = [
        alacritty[group][color]
        for group in ("normal", "bright")
        for color in ANSI_NAMES
    ]
    terminal = omp["terminal"]
    if (terminal["foreground"], terminal["background"], terminal["ansi"]) != (
        foreground,
        background,
        ansi,
    ):
        raise ValueError(f"{name}: omp and Alacritty terminal palettes differ")
    for index, color in enumerate(ansi):
        check_contrast(f"{name} ANSI {index}", color, background)
    for label, surface, fg, bg in (
        ("primary", alacritty["primary"], "foreground", "background"),
        ("cursor", alacritty["cursor"], "text", "cursor"),
        ("vi cursor", alacritty["vi_mode_cursor"], "text", "cursor"),
        ("selection", alacritty["selection"], "text", "background"),
        ("search", alacritty["search"]["matches"], "foreground", "background"),
        (
            "focused search",
            alacritty["search"]["focused_match"],
            "foreground",
            "background",
        ),
        ("hint start", alacritty["hints"]["start"], "foreground", "background"),
        ("hint end", alacritty["hints"]["end"], "foreground", "background"),
        ("footer", alacritty["footer_bar"], "foreground", "background"),
    ):
        check_contrast(f"{name} {label}", surface[fg], surface[bg])

    def color(role):
        value = omp["colors"][role]
        visited = set()
        while value in omp["vars"]:
            if value in visited:
                raise ValueError(f"{name}: circular color reference for {role}")
            visited.add(value)
            value = omp["vars"][value]
        return value

    surfaces = [
        background,
        *(color(role) for role in omp["colors"] if role.endswith("Bg")),
    ]
    for role in omp["colors"]:
        if role.endswith("Bg") or role in DECORATION:
            continue
        if role.startswith("thinking") and role != "thinkingText":
            continue
        for surface in surfaces:
            check_contrast(f"{name} {role} on {surface}", color(role), surface)


def main():
    with urlopen(SCHEMA, timeout=15) as response:
        schema = Draft202012Validator(json.load(response))
    for name in ("nibelung", "nibelung-dark"):
        check_theme(name, schema)
    readme = (ROOT / "README.org").read_text()
    example = readme.split("# alacritty.toml\n", 1)[1].split("#+end_src", 1)[0]
    tomllib.loads(example)
    with tempfile.TemporaryDirectory() as work:
        for target in ("alacritty", "omp"):
            subprocess.run(
                [
                    sys.executable,
                    "export/generate.py",
                    "--emacs",
                    sys.argv[1],
                    "--target",
                    target,
                    "--output-dir",
                    work,
                ],
                cwd=ROOT,
                check=True,
            )
            for generated in (Path(work) / target).rglob("*.*"):
                relative = generated.relative_to(work)
                if generated.read_bytes() != (ROOT / "dist" / relative).read_bytes():
                    raise ValueError(f"dist/{relative} is stale; run make export")
    print(
        "omp and Alacritty exports match the generator and pass schema and contrast checks"
    )


if __name__ == "__main__":
    main()
