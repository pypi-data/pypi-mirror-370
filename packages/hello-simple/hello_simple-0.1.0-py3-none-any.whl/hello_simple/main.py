import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Say hello to someone on the command line.",
    )

    parser.add_argument("name", nargs="?", default="Annonymous")
    parser.add_argument("--shout", "-s", action="store_true", default="Annonymous")
    args = parser.parse_args()

    message = f"Hello {args.name}"

    if args.shout:
        message = message.upper()

    print(message)


if __name__ == "__main__":
    main()
