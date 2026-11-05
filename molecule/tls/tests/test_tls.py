import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

# The role creates this directory and uploads the server files into it
# during converge (see converge.yml).
SERVER_TLS_DIR = "/etc/redis/tls"

# prepare.yml uploads the client files here, outside the role's directory.
CLIENT_TLS_DIR = "/root/redis-tls-client"

REDIS_USER = "redis"
REDIS_GROUP = "redis"


def test_redis_service_running(host):
    """Verify Redis service is enabled and running."""
    if host.system_info.distribution == "ubuntu":
        s = host.service("redis-server")
    else:
        s = host.service("redis")
    assert s.is_enabled
    assert s.is_running


def test_redis_runs_as_redis_user(host):
    """Redis runs as the redis user, not as root."""
    servers = [p for p in host.process.filter(user=REDIS_USER)
               if p.comm == "redis-server"]
    assert servers, f"No redis-server process runs as user {REDIS_USER}"
    root_servers = [p for p in host.process.filter(user="root")
                    if p.comm == "redis-server"]
    assert not root_servers, "A redis-server process runs as root"


def test_tls_files_uploaded(host):
    """The role uploaded the server certificate, the key, and the CA certificate."""
    for name in ("server.crt", "server.key", "ca.crt"):
        f = host.file(f"{SERVER_TLS_DIR}/{name}")
        assert f.exists, f"TLS file not found: {SERVER_TLS_DIR}/{name}"
        assert f.is_file, f"Not a file: {SERVER_TLS_DIR}/{name}"


def test_ca_key_not_on_host(host):
    """The CA private key stays on the control machine."""
    assert not host.file(f"{SERVER_TLS_DIR}/ca.key").exists


def test_tls_file_permissions(host):
    """The role uploads the private key readable by the Redis group only."""
    key = host.file(f"{SERVER_TLS_DIR}/server.key")
    assert key.user == "root", "server.key is not owned by root"
    assert key.group == REDIS_GROUP, f"server.key is not group {REDIS_GROUP}"
    assert key.mode == 0o640, "server.key is not 0640"
    for name in ("server.crt", "ca.crt"):
        cert = host.file(f"{SERVER_TLS_DIR}/{name}")
        assert cert.user == "root", f"{name} is not owned by root"
        assert cert.mode == 0o644, f"{name} is not 0644"
    # The role created the directory, so it has the fixed mode, not the umask.
    tls_dir = host.file(SERVER_TLS_DIR)
    assert tls_dir.user == "root", f"{SERVER_TLS_DIR} is not owned by root"
    assert tls_dir.group == "root", f"{SERVER_TLS_DIR} is not group root"
    assert tls_dir.mode == 0o755, f"{SERVER_TLS_DIR} is not 0755"


def test_redis_user_can_read_tls_key(host):
    """The Redis user reads the private key through the Redis group."""
    result = host.run(f"runuser -u {REDIS_USER} -- cat {SERVER_TLS_DIR}/server.key")
    assert result.rc == 0, f"{REDIS_USER} cannot read server.key: {result.stderr}"


def test_redis_tls_port_listening(host):
    """Verify Redis is listening on TLS port."""
    s = host.socket("tcp://127.0.0.1:6379")
    assert s.is_listening


def test_redis_tls_connection_with_valid_certs(host):
    """Verify Redis accepts TLS connections with valid CA-signed certificates."""
    cmd = host.run(
        "redis-cli --tls "
        f"--cert {CLIENT_TLS_DIR}/client.crt "
        f"--key {CLIENT_TLS_DIR}/client.key "
        f"--cacert {CLIENT_TLS_DIR}/ca.crt "
        "PING"
    )
    assert cmd.rc == 0, f"Expected rc=0, got rc={cmd.rc}, stderr={cmd.stderr}"
    assert "PONG" in cmd.stdout


def test_redis_connection_without_tls_fails(host):
    """Verify Redis rejects non-TLS connections."""
    cmd = host.run("redis-cli PING")
    # Connection should fail when TLS is required
    assert cmd.rc != 0 or "PONG" not in cmd.stdout


def test_redis_tls_connection_with_invalid_cert_fails(host):
    """Verify Redis rejects TLS connections with certificates not signed by CA."""
    cmd = host.run(
        "redis-cli --tls "
        f"--cert {CLIENT_TLS_DIR}/invalid-client.crt "
        f"--key {CLIENT_TLS_DIR}/invalid-client.key "
        f"--cacert {CLIENT_TLS_DIR}/ca.crt "
        "PING"
    )
    # Connection should fail with invalid certificate
    assert cmd.rc != 0 or "PONG" not in cmd.stdout
