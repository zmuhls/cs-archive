#!/usr/bin/env python3
"""Close unclosed triple backtick code fences in comprehensive markdown files.

For each file in output/comprehensive/:
 - Track occurrences of ``` fences.
 - If a page section ends (line '---') while inside a code fence, insert a closing ``` before it.
 - If EOF is reached while inside a code fence, append a closing ``` at the end.

This is a surgical fix to ensure GitHub renders pages correctly.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
COMP_DIR = PROJECT_ROOT / "output" / "comprehensive"

def fix_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    lines = original.splitlines()
    out_lines: list[str] = []
    code_open = False

    for line in lines:
        # Count backtick fences in the line and toggle accordingly
        ticks = line.count("```")
        if ticks:
            # Toggle code state for odd counts
            if ticks % 2 == 1:
                code_open = not code_open
            out_lines.append(line)
            continue

        # If we hit a section separator while code fence is open, close it first
        if line.strip() == "---" and code_open:
            out_lines.append("```")
            code_open = False
            out_lines.append(line)
            continue

        out_lines.append(line)

    # Close any remaining open fence at EOF
    if code_open:
        out_lines.append("```")
        code_open = False

    fixed = "\n".join(out_lines) + ("\n" if original.endswith("\n") else "")
    if fixed != original:
        path.write_text(fixed, encoding="utf-8")
        return True
    return False

def main():
    changed = []
    for md in sorted(COMP_DIR.glob("*_comprehensive.md")):
        try:
            if fix_file(md):
                changed.append(md.relative_to(PROJECT_ROOT).as_posix())
        except Exception as e:
            print(f"Error fixing {md}: {e}")

    if changed:
        print("Closed unclosed code fences in:")
        for p in changed:
            print(f" - {p}")
    else:
        print("No changes needed.")

if __name__ == "__main__":
    main()

