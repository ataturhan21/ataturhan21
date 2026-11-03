"""Offline regressions for the profile README and its daily update."""

import importlib.util
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github/scripts/toggle_rocket.py"
SPEC = importlib.util.spec_from_file_location("toggle_rocket", SCRIPT)
toggle = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(toggle)


class ProfileFooterTests(unittest.TestCase):
    def test_toggle_round_trip_preserves_every_other_byte(self):
        for newline in ("\n", "\r\n"):
            for trailing_newline in ("", newline):
                with self.subTest(newline=repr(newline), trailing=bool(trailing_newline)):
                    before = newline.join([
                        "# Profile 🚀", "", "A paragraph with spaces.  ",
                        "<!-- daily-rocket -->", "**Always Better.**",
                    ]) + trailing_newline
                    after = toggle.toggle_footer(before)
                    self.assertEqual(after, before.replace("**Always Better.**", "**Always Better.** 🚀"))
                    self.assertEqual(toggle.toggle_footer(after), before)

    def test_invalid_markers_and_footers_are_rejected(self):
        invalid = (
            "# Profile\n",
            "<!-- daily-rocket -->\n",
            "<!-- daily-rocket -->\nUnrelated text\n",
            "<!-- daily-rocket -->\n**Always Better.** altered\n",
            "<!-- daily-rocket -->\n**Always Better.**\n<!-- daily-rocket -->\n**Always Better.**\n",
        )
        for text in invalid:
            with self.subTest(text=text), self.assertRaises(ValueError):
                toggle.toggle_footer(text)

    def test_current_readme_round_trips(self):
        original = (ROOT / "README.md").read_bytes()
        text = original.decode("utf-8")
        self.assertEqual(toggle.toggle_footer(toggle.toggle_footer(text)).encode("utf-8"), original)

    def test_import_has_no_write_side_effects(self):
        original = (ROOT / "README.md").read_bytes()
        SPEC.loader.exec_module(toggle)
        self.assertEqual((ROOT / "README.md").read_bytes(), original)

    def test_manual_run_uses_repository_readme_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "repo/.github/scripts/toggle_rocket.py"
            script.parent.mkdir(parents=True)
            script.write_bytes(SCRIPT.read_bytes())
            readme = root / "repo/README.md"
            before = b"# Profile\r\n<!-- daily-rocket -->\r\n**Always Better.**\r\n"
            readme.write_bytes(before)
            unrelated = root / "README.md"
            unrelated.write_text("Do not change this file.\n", encoding="utf-8")
            subprocess.run([sys.executable, str(script)], cwd=root, check=True, capture_output=True)
            self.assertIn("**Always Better.** 🚀", readme.read_text(encoding="utf-8"))
            self.assertEqual(unrelated.read_text(encoding="utf-8"), "Do not change this file.\n")
            subprocess.run([sys.executable, str(script)], cwd=root, check=True, capture_output=True)
            self.assertEqual(readme.read_bytes(), before)


class ProfileRenderingTests(unittest.TestCase):
    def test_srcset_urls_keep_their_commas_encoded(self):
        # GitHub splits srcset at commas, so a raw comma cuts a widget URL short.
        for name in ("README.md", "PROJECTS.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for srcset in re.findall(r'srcset="([^"]*)"', text):
                with self.subTest(file=name, srcset=srcset[:60]):
                    self.assertNotIn(",", srcset)

    def test_local_images_exist(self):
        for name in ("README.md", "PROJECTS.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            for src in re.findall(r'src="\./([^"]+)"', text):
                with self.subTest(file=name, src=src):
                    self.assertTrue((ROOT / src).is_file())

    def test_banner_needs_no_fetches_or_fonts(self):
        # GitHub shows the banner as an image, which can't load fonts or other files.
        banner = (ROOT / "assets/profile-banner.svg").read_text(encoding="utf-8")
        self.assertNotIn("<text", banner)
        self.assertNotRegex(banner, r'href="(?!data:|#)')

    def test_links_to_the_personal_sites(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for url in ("https://ataturhan21.github.io/", "https://ataturhan.com/", "https://solarityai.com/"):
            with self.subTest(url=url):
                self.assertIn(f"]({url})", text)

    def test_section_links_target_profile_page_anchors(self):
        # The profile page only scrolls to the user-content- ids GitHub gives headings.
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        headings = {
            "user-content-" + re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
            for heading in re.findall(r"^#{1,6} (.+)$", text, re.MULTILINE)
        }
        links = re.findall(r'\]\(#([^)]*)\)|href="#([^"]*)"', text)
        self.assertTrue(links)
        for link in ("".join(groups) for groups in links):
            with self.subTest(link=link):
                self.assertIn(link, headings)


if __name__ == "__main__":
    unittest.main()
