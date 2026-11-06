# 2026-11-05-pin-ansible-core-2.16

Pins Ansible to 9.x (ansible-core 2.16) so the role can be tested on RHEL 8 and Rocky Linux 8, and adds those distros to CI.

## 🎯 Problem

The README lists RHEL 8 and Rocky Linux 8 as supported, but nothing tested them. `pyproject.toml` allowed any `ansible>=9.0`, and `uv.lock` resolved a different ansible-core per Python version: 2.17 on Python 3.10, which the ubuntu-22.04 CI runner has, and 2.20 on Python 3.12, which a developer machine has. ansible-core 2.17 and later require Python 3.7 or later on managed nodes. EL8 ships with Python 3.6 as its system Python, so Ansible skips it, falls back to a newer Python in the image, and every package task fails because the `dnf` bindings exist only for the system Python.

The version split also let a bug through: ansible-core 2.19 and later return a real `None` for a template such as `"{{ 'openssl-devel' if ... else None }}"`, which the package module rejects. The source install on RedHat failed on every Python 3.12 machine while CI stayed green. That bug is fixed in #14; this PR removes the split that hid it.

---

## 👀 What changes for users

On RHEL 8 and Rocky Linux 8, a package install with `redis_tls_enabled` enabled now gets Redis 6.2 from the `redis:6` AppStream stream instead of Redis 5, which couldn't serve TLS. Package installs without TLS, and every other distro, are unchanged. For development, `uv run` now installs ansible 9.x (ansible-core 2.16.20) on every Python from 3.10 to 3.12, and the same `molecule test` command works for every distro, including EL8. Python 3.13 is no longer accepted, because ansible-core 2.16 doesn't run on it.

---

## 💥 Impact

* **Who is affected**: developers running the Molecule tests, and CI, which now also runs the package, source, and tls scenarios on `rhel8`.
* **Who is affected, role side**: new EL8 package installs with `redis_tls_enabled: true`. An existing install isn't touched, because the role skips the install tasks when Redis is already present.
* **Who is not affected**: every other playbook that uses the role. The pin lives in the development dependencies only.
* **Conditions**: the stream task runs only on EL8 with TLS enabled.

---

## 🔧 Implementation notes

* `pyproject.toml` pins `ansible>=9.0,<10.0` and caps `requires-python` at `<3.13`, with the same comments as ansible-role-miarecweb, which made this change first.
* `uv.lock` is regenerated. It now holds one resolution, with ansible 9.13.0 and ansible-core 2.16.20, instead of three.
* CI adds `rhel8` to the package, source, and tls matrices. Rocky Linux 8 isn't in CI: customers run either RHEL 8 or Rocky Linux 9. The `rockylinux8` image still works for local runs.
* The default `redis` package on EL8 is Redis 5, which has no TLS support, so a package install with `redis_tls_enabled` enabled used to produce a Redis that refused the `tls-port` directive at startup. `tasks/install-package.yml` now enables the `redis:6` module stream from AppStream, the official Red Hat repository, before installing the package on EL8 when TLS is enabled. The `redis` package then resolves to Redis 6.2, which is built with TLS. The `dnf` module handles the `@redis:6` spec and reports no change on later runs. Without TLS, nothing changes: the default stream stays and Redis 5 is installed as before.
* The README gains a section on testing EL8 and a note under Requirements. CLAUDE.md mentions the pin.
* ansible-core 2.16 prints a warning that `community.docker` doesn't support it. It's metadata validation, and the README says it can be ignored.
