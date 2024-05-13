# Molecule test this role

## Scenario - `default`
This will test the role installing a specific version of redis from source

Run Molecule test
```
molecule test
```

Run test with variable example
```
MOLECULE_DISTRO=centos7 MOLECULE_REDIS_VERSION=6.2.13 molecule test
```

### Variables
 - `MOLECULE_DISTRO` OS of docker container to test, default `ubuntu2204`
    List of tested distros
    - `ubuntu2204`
    - `ubuntu2004`
    - `centos7`
    - `rockylinux8`
    - `rockylinux9`
    - `rhel7`
    - `rhel8`
    - `rhel9`
 - `MOLECULE_REDIS_VERSION` defines variable `redis_version`, default `5.0.10`
 - `MOLECULE_ANSIBLE_VERBOSITY` 0-3 used for troubleshooting, will set verbosity of ansible output, same as `-vvv`, default `0`


## Scenario - `install-package`
This will test installing redis from package

Run Molecule test
```
molecule test
```

Run test with variable example
```
MOLECULE_DISTRO=centos7 molecule test -s install-package
```

### Variables
 - `MOLECULE_DISTRO` OS of docker container to test, default `ubuntu2204`
    List of tested distros
    - `ubuntu2204`
    - `ubuntu2004`
    - `centos7`