# ansible-role-redis

![CI](https://github.com/miarec/ansible-role-redis/actions/workflows/ci.yml/badge.svg?event=push)

Ansible role to install Redis from source or from package.

## Supported Platforms

- Ubuntu 22.04, 24.04
- Rocky Linux 8, 9
- RHEL 8, 9

## Requirements

- Ansible >= 9.0. To manage RHEL 8 or Rocky Linux 8, use Ansible 9.x (ansible-core 2.16), the last version that supports their Python 3.6 system interpreter on managed nodes. See [Testing on EL8](#testing-on-rhel-8--rocky-linux-8).

## Role Variables

For a full list of variables, see [defaults/main.yml](./defaults/main.yml)

### Installation Variables

- `redis_install_from_source` - when true, Redis will be compiled from source (default: `false`)
- `redis_force_install` - when true, Redis will be installed and configured, even if already installed (default: `false`)
  > **Note:** if redis configuration needs to be updated, set `redis_force_install: true`

### "Compile from Source Code" Variables

- `redis_version` - version of Redis to install (default: `7.0.15`)
- `redis_user` - linux user for redis service to run as (default: `redis`)
- `redis_group` - linux group the user belongs to (default: `redis`)
- `redis_verify_checksum` - when true, redis download will be verified against checksum values defined in [vars/main.yml](./vars/main.yml), only set to false when testing new version (default: `true`)
- `redis_cleanup_downloads` - when true, source download files will be deleted after successful install (default: `true`)

### Connection Settings

- `redis_bind` - redis server will only listen to connections made to the address specified, default will allow listening on all interfaces
- `redis_port` - port the Redis will listen (default: `6379`)

### TLS Settings

Available only for versions >= 6 (requires OpenSSL development libraries)

- `redis_tls_enabled` - when true, Redis serves TLS on `redis_port` instead of plain TCP, using the files below. A source install is compiled with TLS support (default: `false`). The old name `redis_make_tls` still works but is deprecated
- `redis_tls_cert` - path to certificate file
- `redis_tls_key` - path to private key file
- `redis_tls_ca_cert` - path to CA certificate file
- `redis_tls_cert_src`, `redis_tls_key_src`, `redis_tls_ca_cert_src` - local copies of the files above (default: empty). When set, the role uploads the file to the matching path, owned by root with mode 0644 for certificates and 0640 for the key (readable by the Redis group), and restarts Redis when the file changed. A missing parent directory is created as 0755 root:root; an existing directory is left alone. Leave empty when the file is already on the host; the role doesn't change the permissions of a file it didn't upload
- When `redis_tls_enabled` is true, the role fails the play if the Redis user cannot read one of the TLS files, before the configuration is written
- `redis_tls_auth_clients` - when true, clients will be required to present certificate signed by same CA (default: `false`)

### Logging

- `redis_logfile` - path to redis log file (default: `/var/log/redis/redis.log`)
- `redis_syslog_enabled` - `"yes"` or `"no"`, if `"yes"` syslog will be enabled

## Example Playbooks

### Install from package

```yaml
- name: Install Redis from package
  hosts: all
  become: true
  roles:
    - role: ansible-role-redis
      redis_install_from_source: false
```

### Install from source

```yaml
- name: Install Redis from source
  hosts: all
  become: true
  roles:
    - role: ansible-role-redis
      redis_install_from_source: true
      redis_version: 7.0.15
```

### Upgrade Redis version

```yaml
- name: Upgrade Redis to newer version
  hosts: all
  become: true
  roles:
    - role: ansible-role-redis
      redis_install_from_source: true
      redis_force_install: true
      redis_version: 8.0.4
```

### Install Redis with TLS support

```yaml
- name: Install Redis with TLS
  hosts: all
  become: true
  roles:
    - role: ansible-role-redis
      redis_install_from_source: true
      redis_version: 7.2.4
      redis_tls_enabled: true
      redis_tls_cert: /etc/pki/tls/redis.crt
      redis_tls_key: /etc/pki/tls/redis.key
      redis_tls_ca_cert: /etc/pki/tls/redis-ca.crt
```

## Testing

### Prerequisites

Install [uv](https://docs.astral.sh/uv/), then run tests:

```bash
uv run molecule test
```

### Alternative: Manual virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r molecule/requirements.txt
molecule test
```

### Test Scenarios

| Scenario | Description | Command |
|----------|-------------|---------|
| `default` | Install from package | `uv run molecule test` |
| `install-from-source` | Install from source | `uv run molecule test -s install-from-source` |
| `tls` | Install with TLS support | `uv run molecule test -s tls` |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MOLECULE_DISTRO` | OS container to test | `ubuntu2404` |
| `MOLECULE_REDIS_VERSION` | Redis version to install | `7.0.15` |
| `MOLECULE_ANSIBLE_VERBOSITY` | Ansible verbosity (0-3) | `0` |

Supported distros: `ubuntu2204`, `ubuntu2404`, `rockylinux8`, `rockylinux9`, `rhel8`, `rhel9`

Example with custom distro and version:

```bash
MOLECULE_DISTRO=rockylinux9 MOLECULE_REDIS_VERSION=8.2.2 uv run molecule test
```

### Testing on RHEL 8 / Rocky Linux 8

EL8 ships with Python 3.6 as the system Python. ansible-core 2.17 and later require Python 3.7 or later on managed nodes, so they skip the system interpreter and fall back to a newer Python on the target. The `dnf` module needs the `python3-dnf` bindings, which exist only for the system Python, so every package task then fails with "Could not import the dnf python module".

`pyproject.toml` pins Ansible to 9.x (ansible-core 2.16), the last version that supports Python 3.6 on managed nodes, and caps `requires-python` below 3.13, the newest Python that ansible-core 2.16 runs on. Every distro, including EL8, uses the same test command:

```bash
MOLECULE_DISTRO=rockylinux8 uv run molecule test
MOLECULE_DISTRO=rhel8 uv run molecule test -s install-from-source
```

The `tls` scenario isn't run on EL8. It installs Redis from the OS package, and the EL8 package is Redis 5, which has no TLS support. Use the source install for TLS on EL8.

RHEL 8 reaches end of life in 2029. Once EL8 support is dropped, the `<10.0` pin can go and Ansible can be upgraded.

You'll see this warning, which can be ignored. It's metadata validation; the module code is compatible:

```
[WARNING]: Collection community.docker does not support Ansible version 2.16.20
```
