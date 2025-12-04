Create molecule testing for deploying Redis with TLS support.

This ansible role supports the following TLS-related variables:

- `redis_make_tls` - when true, Redis will be compiled with TLS support (default: `false`)
- `redis_tls_cert` - path to certificate file
- `redis_tls_key` - path to private key file
- `redis_tls_ca_cert` - path to CA certificate file
- `redis_tls_auth_clients` - when true, clients will be required to present certificate signed by same CA (default: `false`)

In the molecule testing, we should first prepare the necessary TLS certificates and keys. 

During the preparation step, call openssl command to generate:

- CA key and certificate
- Server key and certificate signed by the CA
- Client key and certificate signed by the CA

During provisioning, pass the generated server cettificate/key and CA certificate to the ansible role via the appropriate variables.
`redis_tls_auth_clients` should be set to True.

Once provisioned, verify the following:

- We can run `redis-cli PING` command with the client's certificate/key and CA certificate to successfully connect to the Redis server over TLS.
- Attempting to connect without TLS or with invalid certificates should fail.
- Attemtpting to connect with client certificates that were not signed by the CA should also fail.

