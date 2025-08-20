import sys
from srtify.cli.commands import cli


def main():
    """ Main entry point for the application. """
    try:
        cli()
    except KeyboardInterrupt:
        print("\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()