import sys

if sys.platform != "win32":
    raise RuntimeError("This tool only supports Windows platforms.")


def main():
    try:
        try:
            from .main import main as _main
        except ImportError:
            from main import main as _main  # type: ignore
        _main()
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(0)


if __name__ == "__main__":
    main()
