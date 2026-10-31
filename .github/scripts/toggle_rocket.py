"""Toggle the dedicated profile footer without changing any other README text."""

from pathlib import Path

MARKER = "<!-- daily-rocket -->"
FOOTER = "**Always Better.**"
README = Path(__file__).resolve().parents[2] / "README.md"


def toggle_footer(text: str) -> str:
    lines = text.splitlines(keepends=True)
    markers = [index for index, line in enumerate(lines) if line.strip() == MARKER]
    if len(markers) != 1:
        raise ValueError("README.md must contain exactly 1 daily-rocket marker")

    index = markers[0] + 1
    if index >= len(lines):
        raise ValueError("The daily-rocket marker must be followed by the profile footer")
    footer = lines[index].rstrip("\r\n")
    ending = lines[index][len(footer):]
    if footer not in (FOOTER, FOOTER + " 🚀"):
        raise ValueError("The daily-rocket marker must be followed by the profile footer")

    lines[index] = (FOOTER if footer.endswith("🚀") else FOOTER + " 🚀") + ending
    return "".join(lines)


def main() -> None:
    # Work from the script's location so manual runs do not edit another README.
    with README.open(encoding="utf-8", newline="") as handle:
        updated = toggle_footer(handle.read())
    with README.open("w", encoding="utf-8", newline="") as handle:
        handle.write(updated)


if __name__ == "__main__":
    main()

