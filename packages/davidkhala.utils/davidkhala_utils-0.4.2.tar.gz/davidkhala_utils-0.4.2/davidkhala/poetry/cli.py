import argparse

from davidkhala.poetry import reconfigure_python


def main():
    parser = argparse.ArgumentParser(description="poetry helper")
    subparsers = parser.add_subparsers(dest="command", required=True)
    reconfigure_parser = subparsers.add_parser("reconfigure", help="Rebase underneath Python's version")
    reconfigure_parser.add_argument("version", help="Semantic version", default="3.12.7")
    args = parser.parse_args()

    if args.command == 'reconfigure':
        reconfigure_python(args.version)


if __name__ == "__main__":
    main()
