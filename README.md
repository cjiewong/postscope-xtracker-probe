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

## Published diagnostic

- [GitHub Pages report](https://chris.uran.vip/postscope-xtracker-probe/)
- [Machine-readable result](https://chris.uran.vip/postscope-xtracker-probe/report.json)
- [First hosted run](https://github.com/cjiewong/postscope-xtracker-probe/actions/runs/42360319499)

The first hosted run on 2026-11-07 completed and published successfully. Gamma returned HTTP 200, but both XTracker endpoints returned HTTP 403 with `x-vercel-mitigated: deny`. The upstream access problem remains unresolved.
