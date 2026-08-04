"""Read recent operations without submitting or cancelling anything."""

import os
from datetime import datetime, timedelta

from pyIol import IOLAPIError, IOLClient, OperationStates


def main() -> None:
    username = os.environ["IOL_USERNAME"]
    password = os.environ["IOL_PASSWORD"]
    today = datetime.now()

    try:
        with IOLClient(username, password) as client:
            operations = client.get_operations(
                estado=OperationStates.ALL,
                fecha_desde=(today - timedelta(days=30)).strftime("%Y-%m-%d"),
                fecha_hasta=today.strftime("%Y-%m-%d"),
            )
            for operation in operations:
                print(f"#{operation.numero}: {operation.estado}")
    except IOLAPIError as exc:
        raise SystemExit(f"IOL request failed: {exc}") from exc


if __name__ == "__main__":
    main()
