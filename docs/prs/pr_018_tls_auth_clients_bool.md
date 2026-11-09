# 2026-11-09-tls-auth-clients-bool

Fixes a medium-severity bug that requires client certificates in Redis even when `redis_tls_auth_clients` is set to `"false"` as a string.

## 🎯 Problem

A deployment that turns off client certificate checks by passing `redis_tls_auth_clients` as a string, such as `-e redis_tls_auth_clients=false` or an INI inventory entry, still gets a Redis server that requires a client certificate. Clients without one can't connect.

---

## 👀 What changes for users

With TLS enabled, the string values `"false"` and `"no"` in `redis_tls_auth_clients` now turn off client certificate checks, the same as the boolean `false`. Boolean values behave as before.

---

## 🐛 Bug details

* **Severity**: medium. Clients without a certificate are rejected, and passing a real boolean (YAML vars file or `-e '{"redis_tls_auth_clients": false}'`) works around it.
* **Symptom**: the Redis configuration has `tls-auth-clients yes` although the variable says `false`, and TLS clients without a certificate fail the handshake.
* **Exposure**: the template has tested the raw value since commit e615e90 on 2024-01-09. The repository has no release tags, so every checkout since then has the bug.

---

## 💥 Impact

* **Who is affected**: playbooks that set `redis_tls_enabled: true` and pass `redis_tls_auth_clients` as a string.
* **Who is not affected**: deployments without TLS, which never write the setting, and deployments that set the variable as a YAML boolean. The ansible-miarec playbooks cast the value themselves today, so they aren't affected either.
* **Conditions**: TLS enabled, and `redis_tls_auth_clients` set to a string that means false.

---

## 🔧 Implementation notes

* The fix is in the role so every consumer gets it. ansible-miarec can then drop the `set_fact` that cast the value before calling the role.
