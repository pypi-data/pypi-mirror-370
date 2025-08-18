# `vessl`

This package serves as both CLI for your terminal and SDK for your projects.

Documentation is provided at https://docs.vessl.ai/api-reference/what-is-the-vessl-cli-sdk. 

## Install

Currently VESSL CLI/SDK is available through PyPI only. 
```shell
pip install vessl
```

## VESSL CLI

VESSL Command Line Interface is a convenient tool to access VESSL resources from your terminals.

Refer to [VESSL CLI Docs](https://docs.vessl.ai/api-reference/cli) for details.


### Configure VESSL CLI

First, configure VESSL CLI with your account and set default organization / project.

```shell
> vessl configure
Please grant CLI access from the URL below.
https://vessl.ai/cli/grant-access?token=abcdxyz
Waiting...
[?] Default project: ...
Welcome, VESSL!
```

### Check configuration

Below command will display current configuration for VESSL CLI. 
```shell
> vessl whoami
Username: VESSL
Email: vessl@vessl.ai
Default organization: my-default-organization
Default project: my-default-project
```


## VESSL SDK

VESSL Software Development Kit is a python library that allows easy access to VESSL resources in your python programs and scripts. 

Refer to  [VESSL SDK Docs](https://docs.vessl.ai/api-reference/python-sdk) for details.
