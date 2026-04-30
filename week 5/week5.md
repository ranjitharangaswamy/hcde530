# Week 5

## Class Insight — externally managed Python (PEP 668)

I did not know my machine’s Homebrew Python counts as an **externally managed environment**. That is why plain `pip install pandas` failed with “externally-managed-environment”: the OS / Homebrew Python is protected so user packages do not overwrite or conflict with what the distributor installed.

**What I learned:** installs belong in a **virtual environment** (`python3 -m venv .venv`, then `source .venv/bin/activate` and `pip install -r requirements.txt`), not on the system interpreter. That matches how this repo’s week 5 setup works and avoids `--break-system-packages`, which is risky on a shared Homebrew Python.
