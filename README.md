# Platform Status Monitor

This project uses Python and GitHub Actions to check multiple platforms (named URLs) twice daily, generate PDF reports, and email results when failures occur.

## Setup

1. **Add secrets in your GitHub repo** (Settings → Secrets and variables → Actions):

   - **URL\_**: One secret per platform, e.g. `URL_GOOGLE=https://google.in`
   - **EMAIL\_HOST**, **EMAIL\_PORT**, **EMAIL\_USER**, **EMAIL\_PASS**, **EMAIL\_TO**: SMTP email credentials
   - **EMAIL\_TO** accepts one or more recipients separated by commas or semicolons, e.g. `ops@example.org,alerts@example.org`
   - **ALLOW\_403\_FOR**: Optional comma-separated domains where HTTP 403 should be treated as expected
   - **DISABLED\_GROUPS**: Optional comma-separated URL groups to skip, e.g. `OBI,JH`

2. **Install dependencies locally**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run script locally**:

   ```bash
   python scripts/main.py
   ```

4. **Run tests locally**:

   ```bash
   python -m unittest discover -s tests
   ```

## GitHub Actions

The workflow (`.github/workflows/platform_monitor.yml`) runs daily at **10 AM IST** (04:30 UTC) and **10 PM IST** (16:30 UTC). It sends email reports automatically, attaching a PDF of any failures.

## Contributing

Feel free to open issues or pull requests to improve functionality.
