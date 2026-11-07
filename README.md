# PostScope XTracker connectivity probe

One-time, public, read-only diagnostics from a standard GitHub-hosted runner. GitHub Pages publishes the resulting static report. No API keys, wallet, trading, or production application data are included.

GitHub Pages cannot execute a server-side proxy. The workflow runs Python in GitHub Actions, requests the documented XTracker endpoints and a Gamma control endpoint, then publishes HTTP status, timestamps and selected response metadata.

Run manually using **Actions → Probe and publish → Run workflow**. There is no cron schedule. Standard hosted runners in public repositories use the free GitHub Actions entitlement.

`HTTP 403` is a valid diagnostic outcome: the workflow still publishes the failure report. A green workflow or deployed Pages site does not mean XTracker is accessible. The report explicitly separates those states.

The probe never publishes successful full account/post bodies. It only publishes public endpoint metadata, response shape, and error diagnostics. Test output is not a verified settlement count and must not drive trading.

Local smoke check:

```sh
python3 -m py_compile scripts/probe.py
```

The local PostScope production site and its simulation stay independent of this repository.
