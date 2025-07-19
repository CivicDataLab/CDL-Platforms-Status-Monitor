# Platform Status Monitor

This project uses Python and GitHub Actions to check multiple platforms (named URLs) daily, generate PDF reports, and email results when failures occur.

## Setup

1. **Add secrets in your GitHub repo** (Settings → Secrets and variables → Actions):

   - **URL\_**: One secret per platform, e.g. `URL_GOOGLE=https://google.in`
   - **EMAIL\_HOST**, **EMAIL\_PORT**, **EMAIL\_USER**, **EMAIL\_PASS**, **EMAIL\_TO**: SMTP email credentials

2. **Install dependencies locally**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run script locally**:

   ```bash
   python scripts/main.py
   ```

## GitHub Actions

The workflow (`.github/workflows/platform_monitor.yml`) runs daily at **10 AM IST** (04:30 UTC) and sends email reports automatically, attaching a PDF of any failures.

## Contributing

Feel free to open issues or pull requests to improve functionality.

