# Database recovery

1. Restore the latest Cloud SQL backup into an isolated instance.
2. Connect a staging revision using a temporary DATABASE_URL.
3. Run python manage.py migrate --noinput.
4. Compare counts for instruments, daily bars, technical history, snapshots, and screener runs.
5. Call /health/ready and /health/data.
6. Run a historical technical calculation and screener execution.
7. Record the backup identifier, restore duration, counts, and verifier.

Never overwrite production during a restore test.
