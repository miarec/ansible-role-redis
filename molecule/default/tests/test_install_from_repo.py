import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_directories(host):
    if host.system_info.distribution == "ubuntu":
        dirs = [
            "/etc/redis",
            "/var/run/redis",
            "/var/log/redis",
            "/var/lib/redis"
        ]
    else:
        dirs = [
            "/var/run/redis",
            "/var/log/redis",
            "/var/lib/redis"
        ]
    for dir in dirs:
        d = host.file(dir)
        assert d.is_directory
        assert d.exists


def test_files(host):
    distro = host.system_info.distribution.lower()
    release = host.system_info.release

    if distro == "ubuntu" or release.startswith("9"):
        redis_conf = "/etc/redis/redis.conf"
    else:
        redis_conf = "/etc/redis.conf"

    files = [
        redis_conf,
        "/var/log/redis/redis.log"
    ]

    for file in files:
        f = host.file(file)
        assert f.exists
        assert f.is_file


def test_service(host):
    if host.system_info.distribution == "ubuntu":
        s = host.service("redis-server")
    else:
        s = host.service("redis")

    assert s.is_enabled
    assert s.is_running


def test_socket(host):
    sockets = [
        "tcp://127.0.0.1:6379"
    ]
    for socket in sockets:
        s = host.socket(socket)
        assert s.is_listening


def test_redis_ping(host):
    cmd = host.run("redis-cli PING")
    assert cmd.rc == 0
    assert "PONG" in cmd.stdout