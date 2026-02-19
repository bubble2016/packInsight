# -*- coding: utf-8 -*-
"""快速刷新仪表板 HTML 的样式和脚本，无需重跑数据分析。"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from report.dashboard_builder import (
    get_dashboard_script_bundle,
    get_dashboard_style_bundle,
)


STYLE_START = "/* DASHBOARD_DYNAMIC_STYLES_START */"
STYLE_END = "/* DASHBOARD_DYNAMIC_STYLES_END */"
SCRIPT_START = "/* DASHBOARD_DYNAMIC_SCRIPTS_START */"
SCRIPT_END = "/* DASHBOARD_DYNAMIC_SCRIPTS_END */"


def _replace_between_markers(text: str, start: str, end: str, content: str) -> tuple[str, bool]:
    pattern = re.compile(rf"({re.escape(start)})(.*)({re.escape(end)})", re.DOTALL)
    new_text, count = pattern.subn(
        lambda m: f"{m.group(1)}\n{content}\n        {m.group(3)}",
        text,
        count=1,
    )
    return new_text, count > 0


def _replace_first_style_block(text: str, style_content: str) -> tuple[str, bool]:
    pattern = re.compile(r"(<style[^>]*>)(.*?)(</style>)", re.DOTALL | re.IGNORECASE)
    new_text, count = pattern.subn(lambda m: (
        f"{m.group(1)}\n"
        f"        {STYLE_START}\n"
        f"{style_content}\n"
        f"        {STYLE_END}\n"
        f"    {m.group(3)}"
    ), text, count=1)
    return new_text, count > 0


def _replace_last_inline_script_block(text: str, script_content: str) -> tuple[str, bool]:
    pattern = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>.*?</script>", re.DOTALL | re.IGNORECASE)
    matches = list(pattern.finditer(text))
    if not matches:
        return text, False

    last = matches[-1]
    replacement = (
        "<script>\n"
        f"        {SCRIPT_START}\n"
        f"{script_content}\n"
        f"        {SCRIPT_END}\n"
        "    </script>"
    )
    new_text = text[: last.start()] + replacement + text[last.end() :]
    return new_text, True


def refresh_dashboard_html(html_path: Path) -> None:
    raw = html_path.read_text(encoding="utf-8")
    style_content = get_dashboard_style_bundle()
    script_content = get_dashboard_script_bundle()

    updated = raw
    updated, style_ok = _replace_between_markers(updated, STYLE_START, STYLE_END, style_content)
    if not style_ok:
        updated, style_ok = _replace_first_style_block(updated, style_content)

    updated, script_ok = _replace_between_markers(updated, SCRIPT_START, SCRIPT_END, script_content)
    if not script_ok:
        updated, script_ok = _replace_last_inline_script_block(updated, script_content)

    if not style_ok or not script_ok:
        missing = []
        if not style_ok:
            missing.append("样式块")
        if not script_ok:
            missing.append("脚本块")
        raise RuntimeError(f"刷新失败，未找到可替换的{'/'.join(missing)}。")

    html_path.write_text(updated, encoding="utf-8")


def _find_latest_dashboard_html(root: Path) -> Path:
    candidates = list(root.rglob("*仪表板*.html"))
    if not candidates:
        candidates = list(root.rglob("*dashboard*.html"))
    if not candidates:
        raise FileNotFoundError("未找到仪表板 HTML 文件，请手动传入文件路径。")
    return max(candidates, key=lambda p: p.stat().st_mtime)


def main() -> None:
    parser = argparse.ArgumentParser(description="刷新已生成仪表板 HTML 的样式和脚本。")
    parser.add_argument("html", nargs="?", help="目标 HTML 路径；不传则自动选择最近修改的仪表板 HTML")
    args = parser.parse_args()

    target = Path(args.html).expanduser().resolve() if args.html else _find_latest_dashboard_html(Path.cwd())
    if not target.exists():
        raise FileNotFoundError(f"文件不存在: {target}")

    refresh_dashboard_html(target)
    print(f"已刷新: {target}")


if __name__ == "__main__":
    main()
