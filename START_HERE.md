# Phase 06 first — GitHub update guide

This package includes the full Phase 06 source and documentation under their exact VS Code repository paths. The program has passed a local syntax check and offline self-test only. It has not been run against your live SSB tables 12364 or 12143 in this session.

Repository: https://github.com/marsman1976/norway-municipal-financial-performance

## Install in your project

From the project root:

  unzip -n ~/Downloads/Phase06_GitHub_Update_Ready.zip
  source .venv/bin/activate
  python scripts/phase1a_06_discover_financial_accounts.py --self-test
  python scripts/phase1a_06_discover_financial_accounts.py --tables 12364 12143

Review generated reports under reports/phase1a/financial_account_discovery/ and keep original metadata under data/raw/metadata/phase1a7/. These are ignored by Git and must not be added.

## GitHub: only after checking results

  git add scripts/phase1a_06_discover_financial_accounts.py docs/PHASE1A7_ACCOUNT_METADATA_DISCOVERY_GUIDE.md research/records/PHASE1A7_PRECOLLECTION_MILESTONE.md
  git diff --cached --check
  git diff --cached --stat
  git commit -m "Add Phase 06 financial account metadata discovery"
  git push origin main

Then upload the phase1a7_account_concept_candidates and phase1a7_coverage_and_scope CSV reports here for scientific review. Phase 07 must remain on hold until Phase 06 results and findings are verified.
