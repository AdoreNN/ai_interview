from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_PARTS = {".venv", "__pycache__", ".pytest_cache"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".so", ".dylib"}
SECRET_ASSIGNMENT = re.compile(
    r"^(?:GIGACHAT_CREDENTIALS|GITHUB_TOKEN|JWT_SECRET)=([^\s]+)",
    re.MULTILINE,
)
PLACEHOLDER_MARKERS = ("<", "replace", "change-me", "test-secret", "${")


def unsafe_path(path: str) -> bool:
    item = Path(path)
    return (
        any(part in FORBIDDEN_PARTS for part in item.parts)
        or item.suffix in FORBIDDEN_SUFFIXES
        or (item.name == ".env" and item.name != ".env.example")
        or item.name.endswith(".egg-info")
        or ".egg-info" in item.parts
    )


def contains_secret(content: str) -> bool:
    return any(
        len(value) >= 32 and not any(marker in value.lower() for marker in PLACEHOLDER_MARKERS)
        for value in SECRET_ASSIGNMENT.findall(content)
    )


def main() -> None:
    positive_controls = [
        "pdf_parser_agent/.venv/bin/python",
        "app/__pycache__/main.pyc",
        "pdf_parser_agent/.env",
        "package/native.so",
    ]
    if not all(unsafe_path(path) for path in positive_controls):
        raise SystemExit("source hygiene positive control failed")
    if not contains_secret("GIGACHAT_CREDENTIALS=" + "x" * 100):
        raise SystemExit("secret detection positive control failed")
    if contains_secret("JWT_SECRET=replace-with-at-least-32-random-characters"):
        raise SystemExit("secret placeholder negative control failed")

    result = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    paths = [path for path in result.stdout.decode().split("\0") if path]
    forbidden = [path for path in paths if unsafe_path(path)]
    if forbidden:
        raise SystemExit(f"forbidden generated or secret files: {forbidden}")

    leaked = []
    for path in paths:
        file_path = ROOT / path
        if not file_path.is_file() or file_path.stat().st_size > 1_000_000:
            continue
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if contains_secret(content):
            leaked.append(path)
    if leaked:
        raise SystemExit(f"non-empty secrets found: {leaked}")
    print("source hygiene verified")


if __name__ == "__main__":
    main()
