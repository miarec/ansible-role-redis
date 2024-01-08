import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

def test_directories(host):
    if host.system_info.distribution == "ubuntu":
        dirs = [
            "/etc/redis",
            "/var/run/redis",
            "/var/log/redis"
        ]
    if host.system_info.distribution == "centos":
        dirs = [
            "/var/run/redis",
            "/var/log/redis"
        ]

    for dir in dirs:
        d = host.file(dir)
        assert d.is_directory
        assert d.exists

def test_files(host):
    files = [
        "/etc/redis/6379.conf",
        "/var/run/redis/redis_6379.pid",
        "/var/log/redis/redis_6379.log"
    ]

    for file in files:
        f = host.file(file)
        assert f.exists
        assert f.is_file

def test_service(host):
    s = host.service("redis_6379")

    assert s.is_enabled
    assert s.is_running


def test_socket(host):
    sockets = [
        "tcp://0.0.0.0:6379"
    ]
    for socket in sockets:
        s = host.socket(socket)
        assert s.is_listening