# Pull Request Description Template

## Summary

Add a new molecule testing scenario for Redis TLS support, including certificate generation, provisioning, and verification tests. Also fixes a missing dependency bug on Debian systems.

---

## Purpose

- **Test TLS functionality**: Verify the role's TLS support works correctly with client certificate authentication
- **Fix Debian TLS bug**: `vars/Debian.yml` was missing the `libssl-dev` dependency required for TLS builds (RedHat already had `openssl-devel`)
- **Improve test coverage**: Add comprehensive tests for TLS connections, including positive and negative test cases

---

## Testing

How did you verify it works?

* [x] Added/updated tests
* [x] Ran `uv run ansible-lint`
* Notes: New `molecule/tls` scenario with 5 TestInfra tests covering service status, port listening, valid TLS connections, non-TLS rejection, and invalid certificate rejection

---

## Related Issues

N/A - Feature improvement PR

---

## Changes

Brief list of main changes:

* **New molecule/tls scenario**: Complete TLS testing with certificate generation in prepare.yml
* **Certificate generation**: CA, server, client, and invalid client certificates for comprehensive testing
* **TestInfra tests**: 5 tests verifying TLS functionality and security
* **Bug fix**: Added `libssl-dev` to Debian dependencies when `redis_make_tls: true`
* **Documentation**: Added planning docs in `docs/plans/2025-12-tls-tests/`

---

## Notes for Reviewers

- The prepare.yml creates Redis user/group before certificates so the server key can have proper group ownership (0640) for Redis to read
- Invalid client certificate is self-signed (not CA-signed) to test that only CA-signed certs are accepted
- Tests verify both positive cases (valid certs work) and negative cases (no TLS fails, invalid certs fail)

---

## Docs

* [ ] N/A
* [x] Updated relevant documentation (added `tls` scenario to README test scenarios table)
