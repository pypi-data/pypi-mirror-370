# Badgie

<!-- BADGIE TIME -->

[![pipeline status](https://img.shields.io/gitlab/pipeline-status/saferatday0/badgie?branch=main)](https://gitlab.com/saferatday0/badgie/-/commits/main)
[![coverage report](https://img.shields.io/gitlab/pipeline-coverage/saferatday0/badgie?branch=main)](https://gitlab.com/saferatday0/badgie/-/commits/main)
[![latest release](https://img.shields.io/gitlab/v/release/saferatday0/badgie)](https://gitlab.com/saferatday0/badgie/-/releases)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![cici enabled](https://img.shields.io/badge/%E2%9A%A1_cici-enabled-c0ff33)](https://gitlab.com/saferatday0/cici)
[![code style: prettier](https://img.shields.io/badge/code_style-prettier-ff69b4.svg)](https://github.com/prettier/prettier)

<!-- END BADGIE TIME -->

Badgie scans the contents of your repository and adds badges based on what it
finds.

## Using Badgie

Install Badgie:

```bash
python3 -m pip install badgie
```

Add Badgie tags to your README:

```md
<!-- BADGIE TIME -->
<!-- END BADGIE TIME -->
```

Run Badgie:

```bash
badgie -w README.md
```

And enjoy magic badges:

```md
<!-- BADGIE TIME -->
<!-- END BADGIE TIME -->
```

### Use as a pre-commit hook

Badgie can be used as a pre-commit hook, so you can get fresh badges on every
commit.

Add the following to a `.pre-commit-config.yaml` file. Note the empty
`rev` tag:

```yaml
repos:
  - repo: https://gitlab.com/saferatday0/badgie
    rev: ""
    hooks:
      - id: badgie
```

Run `pre-commit autoupdate` to pin to the latest version:

```bash
pre-commit autoupdate
```

Run `pre-commit` directly or install as a hook:

```bash
# directly
pre-commit

# as a Git hook
pre-commit install
git commit -m "..."
```
