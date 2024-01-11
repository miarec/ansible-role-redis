import os
import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

redis_version = os.environ.get('REDIS_VERSION')

def test_directories(host):
    dirs = [
        "/var/log/redis",
        "/opt/redis-{}".format(redis_version),
        "/opt/redis-{}/data".format(redis_version)
    ]

    # if host.system_info.distribution == "ubuntu":
    #     dirs = [
    #         "/etc/redis",
    #         "/var/log/redis",
    #         "/var/lib/redis",
    #         "/opt/redis-{}".format(redis_version)
    #     ]
    # if host.system_info.distribution == "centos":
    #     dirs = [
    #         "/var/log/redis",
    #         "/var/lib/redis",
    #         "/opt/redis-{}".format(redis_version)
    #     ]

    for dir in dirs:
        d = host.file(dir)
        assert d.is_directory
        assert d.exists

def test_files(host):

    files = [
    "/opt/redis-{}/redis.conf".format(redis_version),
    "/var/log/redis/redis.log"
    ]
    # if host.system_info.distribution == "ubuntu":
    #     files = [
    #         "/opt/redis-{}/redis.conf".format(redis_version),
    #         "/var/log/redis/redis.log"
    #     ]
    # if host.system_info.distribution == "centos":
    #     files = [
    #         "/opt/redis-{}/redis.conf".format(redis_version),
    #         "/var/log/redis/redis.log"
    #     ]

    for file in files:
        f = host.file(file)
        assert f.exists
        assert f.is_file

def test_service(host):
    if host.system_info.distribution == "ubuntu":
        s = host.service("redis-server")
    if host.system_info.distribution == "centos":
        s = host.service("redis")

    assert s.is_enabled
    assert s.is_running


def test_socket(host):
    sockets = [
        "tcp://0.0.0.0:6379"
    ]
    for socket in sockets:
        s = host.socket(socket)
        assert s.is_listening