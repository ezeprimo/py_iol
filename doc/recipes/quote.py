"""Read one quote using credentials from the environment."""

import os

from pyIol import IOLAPIError, IOLClient


def main() -> None:
    symbol = os.getenv("IOL_SYMBOL", "GGAL")
    username = os.environ["IOL_USERNAME"]
    password = os.environ["IOL_PASSWORD"]

    try:
        with IOLClient(username, password) as client:
            quote = client.get_stock_quote(symbol)
            print(f"{symbol}: {quote.ultimo_precio} ({quote.variacion}%)")
    except IOLAPIError as exc:
        raise SystemExit(f"IOL request failed: {exc}") from exc


if __name__ == "__main__":
    main()
