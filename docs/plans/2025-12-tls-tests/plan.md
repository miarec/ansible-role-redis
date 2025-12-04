# Plan: Molecule TLS Testing for Redis

## Overview

Create a new molecule scenario `tls` that tests Redis deployment with TLS support, including certificate generation, provisioning, and verification of TLS connections.

## Requirements (from initial_prompt.md)

- Generate CA, server, and client certificates in prepare phase
- Set `redis_tls_auth_clients: true` to require client certificates
- Test successful TLS connection with valid CA-signed certificates
- Test that non-TLS connections fail
- Test that connections with certificates not signed by CA fail

## Implementation

### Files Created

```
molecule/tls/
├── molecule.yml          # Molecule configuration (Docker driver, TestInfra)
├── collections.yml       # Required Ansible collections
├── requirements.yml      # Role dependencies (empty)
├── prepare.yml           # Certificate generation
├── converge.yml          # Role provisioning with TLS enabled
└── tests/
    └── test_tls.py       # TestInfra verification tests
```

### Certificate Generation (prepare.yml)

The prepare phase generates the following certificates in `/etc/redis/tls/`:

| File | Description |
|------|-------------|
| `ca.key`, `ca.crt` | CA key (4096-bit) and self-signed certificate |
| `server.key`, `server.crt` | Server key (2048-bit) and CA-signed certificate (CN=localhost) |
| `client.key`, `client.crt` | Client key (2048-bit) and CA-signed certificate (CN=redis-client) |
| `invalid-client.key`, `invalid-client.crt` | Self-signed client cert (NOT CA-signed) for negative testing |

**Important**: The `redis` user and group must be created before certificates, so the server key can have proper group ownership (`0640`, group=redis) to allow Redis to read it.

### Converge Variables (converge.yml)

```yaml
redis_version: "{{ lookup('env', 'REDIS_VERSION') }}"
redis_make_tls: true
redis_tls_cert: /etc/redis/tls/server.crt
redis_tls_key: /etc/redis/tls/server.key
redis_tls_ca_cert: /etc/redis/tls/ca.crt
redis_tls_auth_clients: true
```

### Test Cases (test_tls.py)

1. **test_redis_service_running** - Verify redis_6379 service is enabled and running
2. **test_redis_tls_port_listening** - Verify TLS port 6379 is listening
3. **test_redis_tls_connection_with_valid_certs** - Valid CA-signed client certs work
4. **test_redis_connection_without_tls_fails** - Non-TLS connections rejected
5. **test_redis_tls_connection_with_invalid_cert_fails** - Self-signed certs rejected

## Discoveries During Implementation

### Bug Fix Required

**vars/Debian.yml** was missing the OpenSSL development library dependency for TLS builds.

RedHat.yml had:
```yaml
+ (['openssl-devel'] if redis_make_tls | bool else [])
```

Debian.yml was missing the equivalent. Fixed by adding:
```yaml
+ (['libssl-dev'] if redis_make_tls | bool else [])
```

### Permission Issue

Redis runs as the `redis` user but certificate files were initially created with root ownership and `0600` permissions. The server private key must be readable by the redis user.

**Solution**: In prepare.yml:
1. Create redis user/group before generating certificates
2. Set server.key permissions to `0640` with `group: redis`

## Running Tests

```bash
# Run TLS scenario (default Ubuntu 24.04)
uv run molecule test -s tls

# Run with specific distro
MOLECULE_DISTRO=rockylinux9 uv run molecule test -s tls
MOLECULE_DISTRO=ubuntu2204 uv run molecule test -s tls
```

## Test Results

All 5 tests pass on Ubuntu 24.04:
- ✅ test_redis_service_running
- ✅ test_redis_tls_port_listening
- ✅ test_redis_tls_connection_with_valid_certs
- ✅ test_redis_connection_without_tls_fails
- ✅ test_redis_tls_connection_with_invalid_cert_fails
