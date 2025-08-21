import sys
import shutil
import subprocess

OLLAMA_INSTALL_URL = "https://ollama.com/"


def _ollama_installed() -> bool:
    """Return True if the 'ollama' executable is available on PATH."""
    return shutil.which("ollama") is not None


def _print_install_message():
    print("Error: 'ollama' is not installed or not in PATH.")
    print()
    print("Install Ollama:")
    print("  - Windows (recommended): follow the instructions at:")
    print(f"    {OLLAMA_INSTALL_URL}")
    print()
    print("After installing, re-open your terminal or ensure the installation directory is on PATH.")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: aadishlocalai <command> [options]")
        sys.exit(1)

    if not _ollama_installed():
        _print_install_message()
        sys.exit(2)

    cmd = ["ollama"] + args
    try:
        # Use subprocess.run to forward exit code and wait for completion
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        # Allow Ctrl-C to interrupt and return non-zero
        sys.exit(130)
    except Exception as exc:
        print(f"Failed to run 'ollama': {exc}")
        sys.exit(3)
