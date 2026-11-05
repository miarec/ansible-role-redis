# 2026-10-04-upload-tls-files

Moves the TLS file upload into the role, so a renewed certificate restarts only the service that reads it.

## 🎯 Problem

The ansible-miarec playbooks deploy several services, often on one host, and upload the TLS files of each service with a shared task in `pre_tasks`. Each play then restarts its service from `post_tasks` when a variable registered by that task reports a change. Registered variables survive across plays, so one changed certificate restarts every service deployed later on the same host, including services that never read the file. The playbooks also depend on a variable name internal to the shared task file.

---

## 👀 What changes for users

Before, the role expected the TLS files to exist on the host. After, setting `redis_tls_cert_src`, `redis_tls_key_src`, and `redis_tls_ca_cert_src` makes the role copy the files from the Ansible control machine, set root ownership with mode 0644 for certificates and 0640 for private keys readable by the Redis group, and restarts Redis when a file changed. Leaving the variables empty, the default, keeps the previous behavior.

---

## 💥 Impact

* **Who is affected**: deployments that set the new `*_src` variables, starting with ansible-miarec.
* **Who is not affected**: existing deployments. The defaults are empty, so no new task runs and no restart is added.
* **Conditions**: `redis_make_tls` enabled and at least one `*_src` variable set.

---

## 🔧 Implementation notes

* The upload runs on every play, not only on the install run that configures Redis, so a renewed certificate reaches a host where Redis is already installed.
* The role sets permissions only on the files it uploads, in `tasks/tls_upload.yml`. A missing parent directory is created as `0755 root:root`, regardless of the host's umask, so the Redis user can traverse it. An existing directory is left alone. The defaults point at `/etc/pki/tls`, a directory shared with every other service on a RedHat host, so the first version of this PR, which set `root:redis` and mode 0750 on the parent directory of every uploaded file, would have locked other users out of it.
* `tasks/tls_verify.yml` runs `test -r` on each of the three TLS files as `redis_user`, through `runuser`, which applies the user's supplementary groups the way systemd does. The check covers directory traversal, the file mode, and the group membership, for files the role uploaded and files that arrived by other means. It runs after the install tasks, which create the Redis user, and before `configure.yml` writes the configuration, so a failure leaves the host untouched. Before, an unreadable file surfaced only when Redis restarted.
* The `tls` Molecule scenario generates the test certificates on the control machine, in a play on `localhost`, and lets the role upload the server files. Nothing in prepare writes to `/etc/redis/tls`, so the test also covers the role creating the directory. The CA private key never reaches the target, and verify asserts that. Prepare uploads the client files that the verify tests connect with into `/root/redis-tls-client`, outside the role's directory. The scenarios load the role by path, like ansible-role-miarecweb does, so they also work when the repository is checked out under another directory name.
* `.yamllint` mirrors the skips in `.ansible-lint` and ignores `.venv/`, so `uv run yamllint .` passes. `.gitattributes` normalizes line endings to LF.
* This mirrors miarec/ansible-role-miarec#13 and miarec/ansible-role-miarecweb#20.
