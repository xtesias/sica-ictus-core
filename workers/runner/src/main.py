def health() -> dict[str, str]:
    return {"status": "ok"}


def main() -> None:
    print(health())


if __name__ == "__main__":
    main()
