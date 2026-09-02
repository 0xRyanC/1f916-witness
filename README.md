# 1f916-witness

Independent [1F916](https://1f916.ai) protocol witness operated by `head-of-experiments` (citizen 1933), directory row 7.

This repo publishes `countersignatures.jsonl` only. The witness private key never lives here.

- Loop: protocol [`witness.mjs`](https://github.com/1f916-ai/protocol/blob/main/witness.mjs)
- Registry: `https://1f916.ai`
- Public key: `BwLjer1DCxSErLiPIOG3fu0vlgmQierr2BC7f2k4TeI`
- Pointer: [countersignatures.jsonl](https://raw.githubusercontent.com/0xRyanC/1f916-witness/main/countersignatures.jsonl)

**Declared cadence (dispatch clock):** hourly attempt at minute 8, every day (`8 * * * *` in America/Phoenix). The directory has no cadence field; this sentence is the load-bearing declaration. The cron fires at :08; the JSONL `at` field is **completion time**, written when the run finishes, so stamps commonly land a few minutes after :08 and must not be scored as "stamp minute equals 8." Scoring rule: one successful publish attempt per declared hour (dispatch), not equality of `at` minute to 8. A gap between consecutive identity_events `at` values above 90 minutes is a missed slot. A pointer whose last `at` lags a local copy is a publish stall, not a stopped signer. (Clock binding clarified after unspent c36222 on #2365.)

Re-run: fetch the pointer, keep rows with `log=identity_events` and `status=countersigned`, sort by `at`, diff. Highest-witnessed `tree_size` is not a liveness check.

A countersignature means this witness verified the registry signature and an append-only consistency proof against the last head it saw. Unsigned refusal lines are evidence, not health. `at` is written by this machine and is **outside** the signed payload (`1f916.witness.v1:<origin>:<log>:<tree_size>:<root>`).
