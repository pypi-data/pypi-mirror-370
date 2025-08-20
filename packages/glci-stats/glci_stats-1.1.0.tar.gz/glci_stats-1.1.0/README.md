# glstats

CLI that fetches GitLab jobs in a time window and prints duration stats (overall & per job name).

## Install
```bash
pipx install glstats
# or
pip install glstats
```

## Usage
```bash
glstats \
  --gitlab-url https://gitlab.com \
  --project group/subgroup/repo \
  --start 2025-08-01T00:00:00Z \
  --end   2025-08-14T23:59:59Z \
  --statuses success,failed \
  --time-field finished_at \
  --job-scope both \
  --progress \
  --format table
```