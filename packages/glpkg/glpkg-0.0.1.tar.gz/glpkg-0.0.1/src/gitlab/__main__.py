import sys

from gitlab.cli_handler import CLIHandler


def cli() -> int:
    handler = CLIHandler()
    return handler.do_it()


if __name__ == "__main__":
    sys.exit(cli())
