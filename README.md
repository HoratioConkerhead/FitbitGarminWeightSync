# FitbitGarminWeightSync

Sync weight and body composition data from Fitbit to Garmin Connect.

## Prerequisites

- Python 3.11+
- A Fitbit account with a registered app at [dev.fitbit.com](https://dev.fitbit.com/)
- A Garmin Connect account

## Installation

```bash
# From the project root, create and activate a virtual environment
python -m venv .venv

# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (cmd):
.venv\Scripts\activate.bat

# Linux/macOS:
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt when the environment is active.

```bash
# Install with dev dependencies (includes pytest and ruff)
pip install -e ".[dev]"
```

This installs the `fitbit-garmin-sync` command into your virtual environment.

## Configuration

### Fitbit API Credentials

1. Go to <https://dev.fitbit.com/apps/new> and log in with your Fitbit account.
2. Register a new app with these settings:
   - **Application Name**: anything (e.g. "Weight Sync")
   - **OAuth 2.0 Application Type**: **Personal**
   - **Redirect URL**: `http://127.0.0.1:8080/`
   - **Default Access Type**: **Read Only**
3. After registration, note your **OAuth 2.0 Client ID** and **Client Secret**.

### Garmin Connect Credentials

You need your Garmin Connect login email and password.

### Configure the `.env` File

```bash
cp .env.example .env
```

Edit `.env` and fill in your values:

```
FITBIT_CLIENT_ID=your_fitbit_client_id
FITBIT_CLIENT_SECRET=your_fitbit_client_secret
GARMIN_EMAIL=your_garmin_email@example.com
GARMIN_PASSWORD=your_garmin_password
```

**Important:** The `.env` file is in `.gitignore` and will not be committed.

## Testing

```bash
pytest
```

To run with verbose output:

```bash
pytest -v
```

To run a specific test file:

```bash
pytest tests/test_models.py
pytest tests/test_sync.py
```

## Usage

Before syncing for real, do a dry run to verify your Fitbit credentials work:

```bash
fitbit-garmin-sync --dry-run --days 7
```

On the **first run**, a browser window will open asking you to authorize the app with Fitbit. After authorizing, tokens are saved to `~/.fitbit_garmin_sync/fitbit_tokens.json` and reused on subsequent runs.

Once the dry run looks good:

```bash
# Sync new entries since last run (incremental):
fitbit-garmin-sync

# Sync last 7 days:
fitbit-garmin-sync --days 7

# Sync a specific date range:
fitbit-garmin-sync --start-date 2025-01-01 --end-date 2025-01-31

# Clear sync state:
fitbit-garmin-sync --reset
```

## Scheduling (cron)

```cron
# Run daily at 8am:
0 8 * * * /path/to/venv/bin/fitbit-garmin-sync
```

## Deactivate the Virtual Environment

When you're done:

```bash
deactivate
```

## License

MIT
