from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta

from .config import ensure_data_dir, load_config
from .fitbit_client import get_fitbit_client
from .garmin_client import get_garmin_client
from .state import reset_state
from .sync import run_sync


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync weight data from Fitbit to Garmin Connect."
    )
    parser.add_argument(
        "--days",
        type=int,
        help="Sync the last N days (overrides saved state).",
    )
    parser.add_argument(
        "--start-date",
        type=date.fromisoformat,
        help="Start date (YYYY-MM-DD). Overrides saved state.",
    )
    parser.add_argument(
        "--end-date",
        type=date.fromisoformat,
        help="End date (YYYY-MM-DD). Defaults to today.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be synced without uploading.",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear sync state and exit.",
    )
    parser.add_argument(
        "--log",
        action="store_true",
        help="Append output to sync.log in the data directory (useful for scheduled tasks).",
    )
    return parser.parse_args()


def _setup_logging() -> None:
    """Redirect stdout and stderr to sync.log in the data directory."""
    log_path = ensure_data_dir() / "sync.log"
    fh = open(log_path, "a")
    fh.write(f"\n--- {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    sys.stdout = fh
    sys.stderr = fh


def main() -> None:
    args = parse_args()

    if args.log:
        _setup_logging()

    if args.reset:
        reset_state()
        return

    config = load_config()

    start_date = args.start_date
    end_date = args.end_date

    if args.days:
        end_date = date.today()
        start_date = end_date - timedelta(days=args.days - 1)

    print("Connecting to Fitbit...")
    fitbit_client = get_fitbit_client(
        config["fitbit_client_id"],
        config["fitbit_client_secret"],
    )

    if not args.dry_run:
        print("Connecting to Garmin Connect...")
        garmin_client = get_garmin_client(
            config["garmin_email"],
            config["garmin_password"],
        )
    else:
        garmin_client = None

    run_sync(
        fitbit_client=fitbit_client,
        garmin_client=garmin_client,
        start_date=start_date,
        end_date=end_date,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
