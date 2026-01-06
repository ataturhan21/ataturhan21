import pathlib

readme_path = pathlib.Path("README.md")

lines = readme_path.read_text(encoding="utf-8").splitlines()

target_line = 44  # Python is 0-indexed; line 16 is index 15
if target_line < len(lines):
    if lines[target_line].endswith("🚀"):
        # Remove rocket
        lines[target_line] = lines[target_line].rstrip("🚀").rstrip()
    else:
        # Add rocket
        lines[target_line] = lines[target_line] + " 🚀"

readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
