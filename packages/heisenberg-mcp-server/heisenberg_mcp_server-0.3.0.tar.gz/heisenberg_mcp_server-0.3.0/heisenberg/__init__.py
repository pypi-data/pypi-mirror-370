from heisenberg import config
from .server import server


def main():
    if not config.HEISENBERG_TOKEN:
        raise ValueError("HEISENBERG_TOKEN environment variable is not set.")
    if not config.HEISENBERG_KEY:
        raise ValueError("HEISENBERG_KEY environment variable is not set.")

    server.run()


if __name__ == "__main__":
    main()
