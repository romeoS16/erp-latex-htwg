import re
import sys
from pathlib import Path


def remove_latex_commands(text: str) -> str:
    # Remove comments
    text = re.sub(r'%.*', '', text)
    # Remove \command{...} blocks (including nested braces)
    # Iteratively remove \word{...} until nothing changes
    pattern = re.compile(r'\\[a-zA-Z*]+\s*(\[.*?\])?\s*\{[^{}]*\}')
    prev = None
    while prev != text:
        prev = text
        text = pattern.sub(' ', text)
    # Remove remaining \commands (without braces)
    text = re.sub(r'\\[a-zA-Z*]+\*?', ' ', text)
    # Remove leftover braces, brackets, special chars
    text = re.sub(r'[{}\[\]]', ' ', text)
    return text


def count_words_in_file(path: Path) -> int:
    text = path.read_text(encoding='utf-8', errors='ignore')
    cleaned = remove_latex_commands(text)
    words = cleaned.split()
    return len(words)


def collect_tex_files(path: Path) -> list[Path]:
    if path.is_file():
        return [path] if path.suffix == '.tex' else []
    return sorted(path.rglob('*.tex'))


def main():
    if len(sys.argv) < 2:
        print("Usage: python count_words.py <path> [<path> ...]")
        sys.exit(1)

    inputs = [Path(p) for p in sys.argv[1:]]
    for p in inputs:
        if not p.exists():
            print(f"Error: '{p}' does not exist")
            sys.exit(1)

    tex_files: list[Path] = []
    for p in inputs:
        tex_files.extend(collect_tex_files(p))

    # deduplicate while preserving order
    seen: set[Path] = set()
    unique_files = []
    for f in tex_files:
        resolved = f.resolve()
        if resolved not in seen:
            seen.add(resolved)
            unique_files.append(f)

    if not unique_files:
        print("No .tex files found.")
        return

    total = 0
    for f in unique_files:
        count = count_words_in_file(f)
        total += count
        print(f"{count:>6}  {f}")

    print(f"\n{'':->30}")
    print(f"{'Total:':>7} {total} Wörter")


if __name__ == '__main__':
    main()
