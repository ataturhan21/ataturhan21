import pathlib

readme_path = pathlib.Path("README.md")
lines = readme_path.read_text(encoding="utf-8").splitlines()

# Keep the daily profile update on its dedicated footer as the README evolves.
marker = "<!-- daily-rocket -->"
marker_lines = [index for index, line in enumerate(lines) if line.strip() == marker]
if len(marker_lines) != 1:
    raise ValueError("README.md must contain exactly 1 daily-rocket marker")

target_line = marker_lines[0] + 1
if target_line >= len(lines) or not lines[target_line].startswith("**Always Better.**"):
    raise ValueError("The daily-rocket marker must be followed by the profile footer")

if lines[target_line].endswith("🚀"):
    lines[target_line] = lines[target_line].rstrip("🚀").rstrip()
else:
    lines[target_line] = lines[target_line] + " 🚀"

readme_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
