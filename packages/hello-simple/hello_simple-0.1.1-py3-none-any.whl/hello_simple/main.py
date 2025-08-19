import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Say hello to someone on the command line.",
    )

    parser.add_argument(
        "name",
        nargs="?",
        default="Annonymous",
        help="Set the name of the person you want to say hello to.",
    )
    parser.add_argument(
        "-s", "--shout", action="store_true", help="Shout the greeting."
    )
    args = parser.parse_args()

    message = f"Hello {args.name}"

    if args.shout:
        message = message.upper()

    print(message)


if __name__ == "__main__":
    main()
