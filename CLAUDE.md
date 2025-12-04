This file provides guidance to coding agent when working with code in this repository.

## Project Overview

Ansible role for installing and configuring Redis on Linux systems. Supports two installation methods:
- **Source installation** (default): Compiles Redis from source with optional TLS support
- **Package installation**: Installs from OS package repositories

Supports Ubuntu (22.04, 24.04), Rocky Linux (8, 9), and RHEL (8, 9).

## Testing Commands

Run molecule tests (uses uv for dependency management):
```bash
uv run molecule test                          # source installation (default scenario)
uv run molecule test -s install-package       # package installation scenario
```

First-time setup requires installing Ansible collections:
```bash
uv run ansible-galaxy collection install community.docker ansible.posix --force
```

Run tests with specific OS/version:
```bash
MOLECULE_DISTRO=rockylinux9 MOLECULE_REDIS_VERSION=8.0.4 uv run molecule test
```

Environment variables:
- `MOLECULE_DISTRO`: Target OS container (ubuntu2204, ubuntu2404, rockylinux8, rockylinux9, rhel8, rhel9)
- `MOLECULE_REDIS_VERSION`: Redis version to install (default: 7.0.15)
- `MOLECULE_ANSIBLE_VERBOSITY`: 0-3 for ansible output verbosity

Run ansible-lint:
```bash
uv run ansible-lint
```

## Role Architecture

**Entry point**: `tasks/main.yml` orchestrates:
1. `preflight.yml` - OS detection, variable validation
2. `install-source.yml` or `install-package.yml` - based on `redis_install_from_source`
3. `configure.yml` - generates config, starts service

**Key variables** (in `defaults/main.yml`):
- `redis_install_from_source`: true/false for installation method
- `redis_force_install`: reinstall even if Redis exists
- `redis_version`: version to compile from source
- `redis_make_tls`: enable TLS support (requires OpenSSL dev libs)

**OS-specific variables**: `vars/Debian.yml`, `vars/RedHat.yml` define package names and dependencies

**Checksums**: `vars/main.yml` contains SHA1/SHA256 checksums for Redis versions (required for source installs)

**Templates**:
- `templates/redis.conf.j2` - Redis configuration
- `templates/redis-server.service.j2` - systemd service unit

## Adding New Redis Versions

When adding support for a new Redis version:
1. Get the checksum from https://github.com/antirez/redis-hashes
2. Add entry to `redis_checksums` in `vars/main.yml`
3. Add version to CI matrix in `.github/workflows/ci.yml`
