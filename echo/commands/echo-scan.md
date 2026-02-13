---
description: Scan this repo to bootstrap Echo's knowledge (one-off setup)
---

Run the Echo repo scanner to pre-populate code structure knowledge. This is a one-off setup step for existing repos — after this, Echo learns incrementally from your edits.

Run the scan:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/scan_repo.py
```

Then regenerate the consolidated structure:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/consolidate_structure.py
```

After scanning, report what was found:
- How many structures were indexed
- How many directories are covered
- Suggest the user starts working — Echo will refine its knowledge from here

If the user wants a deeper scan (more structures), run with `--full`:
```bash
python ${CLAUDE_PLUGIN_ROOT}/scripts/scan_repo.py --full
```
