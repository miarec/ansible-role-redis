# Pull Request Description Template

## Summary

Migrate the project from pip-based dependency management to **uv**, a fast Python package manager. This modernizes the development workflow, simplifies CI configuration, and fixes various lint warnings.

---

## Purpose

- **Faster dependency resolution**: uv is significantly faster than pip for installing dependencies
- **Simplified CI workflow**: Replace multi-step Python/pip setup with a single `uv run` command
- **Better reproducibility**: Lock file (`uv.lock`) ensures consistent environments
- **Code quality**: Fix Ansible lint warnings for octal modes and deprecated `ansible_*` variable syntax

---

## Testing

How did you verify it works?

* [x] Added/updated tests
* [x] Ran `uv run ansible-lint`
* Notes: Added redis-cli PING test to verify Redis is fully functional after installation

---

## Related Issues

N/A - Modernization/improvement PR

---

## Changes

Brief list of main changes:

* **Add uv support**: Added `pyproject.toml` with dev dependencies and generated `uv.lock`
* **Update CI workflow**: Replace pip install with `uv run` in GitHub Actions
* **Consolidate requirements**: Single `molecule/requirements.txt` instead of per-scenario duplicates
* **Fix lint warnings**: Quote octal file modes, use `ansible_facts["key"]` dictionary syntax
* **Add CLAUDE.md**: Documentation for AI coding agents
* **Improve README.md**: Better structure, testing documentation with tables
* **Add molecule test**: redis-cli PING verification test
* **Add molecule config**: `collections.yml` and `requirements.yml` for proper dependency declaration
* **Reduce CI matrix**: Remove RHEL/Rocky 8 (EOL/unsupported Python 3.6), test one version per major release

---

## Notes for Reviewers

- RHEL 8 and Rocky Linux 8 were removed from CI because they ship with Python 3.6, which is incompatible with recent Ansible versions (requires Python 3.7+)
- The CI matrix was reduced to test one Redis version per major release (6.0.20, 7.0.15, 8.2.2) to speed up CI while maintaining coverage
- The `uv.lock` file is intentionally committed to ensure reproducible builds

---

## Docs

* [x] Updated relevant documentation
