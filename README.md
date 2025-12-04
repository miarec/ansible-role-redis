# ansible-role-redis

![CI](https://github.com/miarec/ansible-role-redis/actions/workflows/ci.yml/badge.svg?event=push)

Ansible role to install Redis from source or from package.

## Supported Platforms

- Ubuntu 22.04, 24.04
- Rocky Linux 8, 9
- RHEL 8, 9

## Requirements

- Ansible >= 9.0

## Role Variables

For a full list of variables, see [defaults/main.yml](./defaults/main.yml)

### Installation Variables

- `redis_install_from_source` - when true, Redis will be compiled from source (default: `true`)
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

- `redis_make_tls` - when true, Redis will be compiled with TLS support (default: `false`)
- `redis_tls_cert` - path to certificate file
- `redis_tls_key` - path to private key file
- `redis_tls_ca_cert` - path to CA certificate file
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
      redis_make_tls: true
      redis_tls_cert: /etc/pki/tls/redis.crt
      redis_tls_key: /etc/pki/tls/redis.key
      redis_tls_ca_cert: /etc/pki/tls/redis-ca.crt
```

## Testing

### Prerequisites

Install [uv](https://docs.astral.sh/uv/), then run tests:

```bash
uv run ansible-galaxy collection install community.docker ansible.posix
uv run molecule test
```

### Alternative: Manual virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r molecule/requirements.txt
ansible-galaxy collection install community.docker ansible.posix
molecule test
```

### Test Scenarios

| Scenario | Description | Command |
|----------|-------------|---------|
| `default` | Install from source | `uv run molecule test` |
| `install-package` | Install from package | `uv run molecule test -s install-package` |

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
