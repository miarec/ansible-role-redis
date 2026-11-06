# 2026-11-05-epel-gpg-key-https

Fixes a low-severity bug that broke the Redis package install on RHEL 7, a platform the role no longer lists as supported.

## 🎯 Problem

A playbook that installs Redis from packages on a RHEL 7 host fails at the install step. The role configures the EPEL repository with a GPG key URL that Fedora's mirror redirector no longer serves, so yum can't verify the packages. There's no workaround short of editing the role.

---

## 👀 What changes for users

A package install of Redis on RHEL 7 completes again. Every other distro is unchanged.

---

## 🐛 Bug details

* **Severity**: low. The failing task runs only on RHEL 7, which left Red Hat maintenance support in June 2024. The README lists RHEL 8 and 9 as the supported Enterprise Linux versions, and CI tests only those.
* **Symptom**: the "Install Redis | Package install" task fails on RHEL 7 with a GPG key retrieval error. yum requests `http://download.fedoraproject.org/pub/epel/RPM-GPG-KEY-EPEL-7`, and the redirector answers 404 for every EPEL key path over plain HTTP.
* **Exposure**: the HTTP URL arrived in commit 4c153a1 on 2024-02-08 ("Update EPEL install method for RHEL 7"). The repository has no release tags, so every checkout since then carries it. The failure started when Fedora stopped serving the keys over HTTP, not with any change in this role.

---

## 💥 Impact

* **Who is affected**: playbooks that run the role with `redis_install_from_source: false` against a RHEL 7 host that doesn't already have Redis installed.
* **Who is not affected**: Ubuntu, Rocky Linux, and RHEL 8 and 9 hosts, which never run the RHEL 7 EPEL task. Existing RHEL 7 installs are also safe, because the role skips the install tasks when Redis is already present.
* **Conditions**: a fresh package install on RHEL 7.

---

## 🔧 Implementation notes

* The new URL is the direct `dl.fedoraproject.org` host over HTTPS, the same one the ansible-role-pgbouncer role switched to in its commit "fix(deps): fetch the EPEL GPG key over HTTPS". The repository base URL in the same task already used that host.
* The plain-HTTP fetch wasn't a package-injection risk on its own: the repository base URL is HTTPS, so a tampered key could only make signature checks fail.
* Removing the RHEL 7 task altogether was considered, since the role doesn't claim RHEL 7 support. That's a support decision, so this PR keeps the task and only fixes the URL.
