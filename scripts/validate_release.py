import argparse
import io
import re
import tokenize
from pathlib import Path


EXCLUDED = {".git", ".venv", "__pycache__"}
PATH_PATTERN = re.compile(chr(47) + r"(?:Users|home|scratch|export/home[0-9]*)(?:" + chr(47) + r"|$)", re.I)
SECRET_PATTERN = re.compile(r"hf_[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9]{20,}|BEGIN [A-Z ]+PRIVATE KEY")
CODE_SUFFIXES = {".py", ".sh", ".bash", ".slurm"}
TEXT_SUFFIXES = CODE_SUFFIXES | {".md", ".json", ".jsonl", ".yaml", ".yml", ".toml", ".txt", ".cfg", ".ini", ".svg"}


def files(root: Path):
    for path in root.rglob("*"):
        if any(part in EXCLUDED for part in path.parts) or not path.is_file():
            continue
        yield path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=Path(__file__).resolve().parents[1], type=Path)
    arguments = parser.parse_args()
    findings = []
    for path in files(arguments.root):
        if "third_party" in path.parts or path == Path(__file__).resolve():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"LICENSE", "NOTICE", ".gitignore"}:
            continue
        try:
            content = path.read_text()
        except UnicodeDecodeError:
            continue
        if PATH_PATTERN.search(content):
            findings.append(f"private path or identity: {path.relative_to(arguments.root)}")
        if SECRET_PATTERN.search(content):
            findings.append(f"credential-shaped text: {path.relative_to(arguments.root)}")
        if path.suffix.lower() == ".py":
            comments = [token for token in tokenize.generate_tokens(io.StringIO(content).readline) if token.type == tokenize.COMMENT]
            if any(not token.string.startswith(chr(35) + chr(33)) for token in comments):
                findings.append(f"comment found: {path.relative_to(arguments.root)}")
        elif path.suffix.lower() in CODE_SUFFIXES:
            body = [line for line in content.splitlines() if not line.startswith(chr(35) + chr(33))]
            if any(line.lstrip().startswith(chr(35)) for line in body):
                findings.append(f"comment found: {path.relative_to(arguments.root)}")
    if findings:
        raise SystemExit("\n".join(findings))
    print("release validation passed")


if __name__ == "__main__":
    main()
