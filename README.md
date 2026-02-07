# FitbitGarminWeightSync

Sync weight and body composition data from Fitbit to Garmin Connect.

## Prerequisites

- Python 3.11+
- A Fitbit account with a registered app at [dev.fitbit.com](https://dev.fitbit.com/)
- A Garmin Connect account

## Installation

```bash
pip install .
# or for development:
pip install -e ".[dev]"
```

## Configuration

```bash
cp .env.example .env
# Edit .env with your credentials
```

### Fitbit Setup

1. Go to [dev.fitbit.com](https://dev.fitbit.com/apps/new), register an app (type: **Personal**)
2. Set OAuth 2.0 redirect URI to `http://127.0.0.1:8080/`
3. Copy your Client ID and Client Secret into `.env`

### Garmin Setup

1. Add your Garmin Connect email and password to `.env`

## Usage

```bash
# Sync new entries since last run:
fitbit-garmin-sync

# Sync last 7 days:
fitbit-garmin-sync --days 7

# Sync a specific date range:
fitbit-garmin-sync --start-date 2025-01-01 --end-date 2025-01-31

# Preview without uploading:
fitbit-garmin-sync --dry-run

# Clear sync state:
fitbit-garmin-sync --reset
```

On the first run, a browser window will open for Fitbit OAuth authorization. Subsequent runs use saved tokens.

## Scheduling (cron)

```cron
# Run daily at 8am:
0 8 * * * /path/to/venv/bin/fitbit-garmin-sync
```

## License

MIT
