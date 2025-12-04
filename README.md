# ansible-role-redis
![CI](https://github.com/miarec/ansible-role-redis/actions/workflows/ci.yml/badge.svg?event=push)
Ansible role to install Redis from source or from package.

# Role Variables

For a full list of variables, see [defaults/main.yml](./defaults/main.yml)

## Installation Variables

 - `redis_install_from_source` when true, Redis will be compilied from source, default `true`
 - `redis_force_install` when true, Redis will be installed and configured, even if redis is already installed. default = `false`
  > **_NOTE:_** if redis configuration needs to be updated, set `redis_force_install` = `true`

### `install from source` variables

 - `redis_version` version of Redis to install, default = `7.0.15`
 - `redis_user` linux user for redis service to be ran ad, default = `redis`
 - `redis_group`linux group linux user belongs to, default = `redis`

 - `redis_verify_checksum` when true, redis download will be verified against checksum values defined in [vars/main.yml](./vars/main.yml), only set to false when testing new version
 - `redis_cleanup_downloads` when true, source download files will be deleted after successful install, default = `true`



##  Configuration Options

### Connection Settings
 - `redis_bind` redis server will only listen to connections made to the address specified, default will allow listening on all interfaces
 - `redis_port` port the Redis will listen, default = `6379`

### TLS Settings
available only for versions >= 6 (require OpenSSL development libraries)
 - `redis_make_tls` When true, Redis will be compiled with TLS support, default = `false``
 - `redis_tls_cert` path to Certificate file
 - `redis_tls_key` path to private key file
 - `redis_tls_ca_cert` path to CA certificate file
 - `redis_tls_auth_clients` when true, clients who connect to redis will be required to present certificate signed by same ca, default = `false`


### Logging
- `redis_logfile` path to redis log file, default = `/var/log/redis/redis.log`
- `redis_syslog_enabled` "yes" or "no" if "yes", syslog will be enabled.




## Example Playbook

### Install from package
```yaml
- name: Install Redis from package
  hosts:
    - all
  pre_tasks:
    - set_fact:
        redis_install_from_source: false
  become: true
  roles:
    - role: 'ansible-role-redis'
  tags: 'redis'
```

### Install from source
```yaml
- name: Install Redis from source.
  hosts:
    - all
  pre_tasks:
    - set_fact:
        redis_install_from_source: true
        redis_version: 7.0.15
  become: true
  roles:
    - role: 'ansible-role-redis'
  tags: 'redis'
```

### Upgrade Redis version when installed from source
```yaml
- name: Upgrade Redis to newer version.
  hosts:
    - all
  pre_tasks:
    - set_fact:
        redis_install_from_source: true
        redis_force_install: true
        redis_version: 8.0.4
  become: true
  roles:
    - role: 'ansible-role-redis'
  tags: 'redis'
```

### Install Redis with TLS support
```yaml
- name: Install Redis with TLS
  hosts:
    - all
  pre_tasks:
    - set_fact:
        redis_install_from_source: true
        redis_version: 7.2.4
        redis_make_tls: true
        redis_tls_cert: /etc/pki/tls/redis.crt
        redis_tls_key: /etc/pki/tls/redis.key
        redis_tls_ca_cert: /etc/pki/tls/redis-ca.crt
  become: true
  roles:
    - role: 'ansible-role-redis'
  tags: 'redis'
```

## Testing

### Prerequisites

#### Option 1: Using uv (recommended)

Install [uv](https://docs.astral.sh/uv/), then run tests:
```bash
uv run ansible-galaxy collection install community.docker ansible.posix
uv run molecule test
```

#### Option 2: Manual virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r molecule/requirements.txt
ansible-galaxy collection install community.docker ansible.posix
molecule test
```

### Scenario - `default`
This will test the role installing a specific version of redis from source

Run Molecule test
```
molecule test
```

Run test with variable example
```
MOLECULE_DISTRO=centos7 MOLECULE_REDIS_VERSION=8.2.2 molecule test
```

#### Variables
 - `MOLECULE_DISTRO` OS of docker container to test, default `ubuntu2404`
    List of tested distros
    - `ubuntu2404`
    - `ubuntu2204`
    - `centos7`
    - `rockylinux8`
    - `rockylinux9`
    - `rhel7`
    - `rhel8`
    - `rhel9`
 - `MOLECULE_REDIS_VERSION` defines variable `redis_version`, default `7.0.15`
 - `MOLECULE_ANSIBLE_VERBOSITY` 0-3 used for troubleshooting, will set verbosity of ansible output, same as `-vvv`, default `0`


### Scenario - `install-package`
This will test installing redis from package

Run Molecule test
```
molecule test -s install-package
```

Run test with variable example
```
MOLECULE_DISTRO=centos7 molecule test -s install-package
```

#### Variables
 - `MOLECULE_DISTRO` OS of docker container to test, default `ubuntu2404`
    List of tested distros
    - `ubuntu2404`
    - `ubuntu2204`
    - `centos7`
