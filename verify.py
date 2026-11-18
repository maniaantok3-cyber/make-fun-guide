#!/usr/bin/env python3
"""Local checks for the bring-the-humans-02 guide entry (stdlib only).

Checks: README.md + screenshot.png at root, referral code present (bare,
/r/<code> or ?ref=<code>), the three make.fun badge lines as live images
(no placeholders), no .github/README.md, README <= 2 MB, screenshot a
PNG/JPEG/WebP <= 8 MB and <= 16,000,000 pixels.
"""
import os
import re
import struct
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
CODE = "ck8gwbg6"
OWNER = "maniaantok3-cyber"
REPO = "make-fun-guide"
fails = []


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ((" — " + detail) if detail else ""))
    if not ok:
        fails.append(name)


readme_p = os.path.join(ROOT, "README.md")
shot_p = os.path.join(ROOT, "screenshot.png")
check("readme_exists", os.path.isfile(readme_p))
check("screenshot_exists", os.path.isfile(shot_p))
check("no_github_readme", not os.path.isfile(os.path.join(ROOT, ".github", "README.md")))

readme = open(readme_p, encoding="utf-8").read() if os.path.isfile(readme_p) else ""
check("readme_size", len(readme.encode("utf-8")) <= 2_000_000,
      f"{len(readme.encode('utf-8'))} bytes")
check("referral_code_bare", CODE in readme)
check("referral_link", "https://make.fun/r/ck8gwbg6" in readme)
check("no_placeholders", "{{REFERRAL_LINK}}" not in readme
      and "{{REFERRAL_CODE}}" not in readme
      and "{{GITHUB_OWNER}}" not in readme
      and "{{REPOSITORY}}" not in readme)
badges = [
    "https://make.fun/badge/bring-the-humans-02.svg",
    f"https://make.fun/badge/bring-the-humans-02/{OWNER}/{REPO}/rank.svg",
    f"https://make.fun/badge/bring-the-humans-02/{OWNER}/{REPO}/reward.svg",
]
for b in badges:
    check(f"badge:{b.split('/')[-1]}", b in readme and f"]({b})" in readme
          or f"({b})" in readme)
check("badge_not_in_comment_or_codeblock",
      not re.search(r"<!--[^>]*make\.fun/badge[^>]*-->", readme)
      and not re.search(r"```[^`]*make\.fun/badge[^`]*```", readme, re.S))
check("license_mit", os.path.isfile(os.path.join(ROOT, "LICENSE"))
      and "MIT License" in open(os.path.join(ROOT, "LICENSE"), encoding="utf-8").read())

if os.path.isfile(shot_p):
    data = open(shot_p, "rb").read()
    check("screenshot_size", len(data) <= 8_000_000, f"{len(data)} bytes")
    ok_png = data[:8] == b"\x89PNG\r\n\x1a\n"
    ok_jpg = data[:2] == b"\xff\xd8"
    ok_webp = data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    check("screenshot_format", ok_png or ok_jpg or ok_webp)
    px = None
    if ok_png:
        w, h = struct.unpack(">II", data[16:24])
        px = w * h
    elif ok_jpg:
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            m = data[i + 1]
            if m in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                px = w * h
                break
            i += 2 + struct.unpack(">H", data[i + 2:i + 4])[0]
    check("screenshot_pixels", px is not None and px <= 16_000_000, f"{px} px")

print(f"\n{len(fails)} failed" if fails else "\nALL CHECKS PASSED")
sys.exit(1 if fails else 0)
