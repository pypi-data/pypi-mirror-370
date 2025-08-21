"""Hello module for uv-demo."""

from loguru import logger as log

LIB_NAME: str = "uv_demo"
log.disable(LIB_NAME)


def say_hello() -> None:
    """Entrypoint for uv-demo."""
    log.info("This message should not be seen by most users.")
    print("Hello from uv-demo!")


def say_goodbye() -> None:
    """Another entrypoint for uv-demo."""
    log.info("This message should not be seen by most users.")
    print("Goodbye from uv-demo!")


def main() -> None:  # pragma: no cover
    """Main entrypoint and usage example for uv-demo."""
    log.enable(LIB_NAME)


if __name__ == "__main__":  # pragma: no cover
    main()
