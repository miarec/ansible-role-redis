# 2026-11-05-rename-tls-enabled

Renames `redis_make_tls` to `redis_tls_enabled`, because the variable switches Redis to TLS, not only the build.

## 🎯 Problem

`redis_make_tls` was introduced to add `BUILD_TLS=yes` to the `make` command of a source install, and the name comes from that flag. Since then it has become the single TLS switch for the role: it also renders `port 0` and `tls-port` with the `tls-*-file` paths into `redis.conf`, gates the upload and the readability check of the TLS files, and adds the OpenSSL development packages to the source dependencies. For the default package install, nothing is compiled at all, and the README line "Redis will be compiled with TLS support" was wrong. The name hid what the variable does.

---

## 👀 What changes for users

Set `redis_tls_enabled: true` instead of `redis_make_tls: true`. The behavior is the same. `redis_make_tls` still works for now: `redis_tls_enabled` defaults to its value, and preflight prints a deprecation message when it is set. The old name will be removed in a later release.

---

## 💥 Impact

* **Who is affected**: playbooks that set `redis_make_tls`, which is ansible-miarec. They keep working and print a deprecation message on every run until they switch to the new name.
* **Who is not affected**: deployments without TLS. The default is unchanged, `false`.
* **Conditions**: none. The rename applies to every install method.

---

## 🔧 Implementation notes

* `redis_tls_enabled` is defined in `defaults/main.yml` as `{{ redis_make_tls | default(false) }}`. A playbook that sets only the old name gets the alias; one that sets the new name overrides the default as usual. `redis_make_tls` itself is no longer defined in the role, so `redis_make_tls is defined` in preflight is true only when the caller set it.
* Every use in the role, the template, the OS variable files, the Molecule `tls` scenario, the README, and CLAUDE.md now reads `redis_tls_enabled`. The PR description of #13 keeps the old name as a record of that PR as merged.
* The preflight version check message was "When Redis version 6.x.x or higher is required for TLS support". The stray "When" is gone.
* The alias was checked by converging the `tls` scenario with a playbook that sets only `redis_make_tls: true`, then running the scenario's verify tests, which passed. That playbook isn't committed.
* The RedHat source dependency lists in `vars/RedHat.yml` and `vars/RedHat-9.yml` built their optional entries as `"{{ 'openssl-devel' if ... else None }}"`. ansible-core 2.19 and later return a real `None` for such a template, and the package module then fails with "argument 'name' is of type NoneType". The install task now loops over `redis_source_dependencies | select | list`, which drops the `None`, and the empty string that older versions produce. The lists keep their readable form. CI didn't catch this because `uv.lock` resolves ansible-core by Python version: the ubuntu-22.04 runner has Python 3.10 and gets 2.17.14, while Python 3.12 gets 2.20.0. The fix is in its own commit and doesn't depend on the rename.
* This PR is stacked on #13, because the upload and verify includes it renames were added there.
