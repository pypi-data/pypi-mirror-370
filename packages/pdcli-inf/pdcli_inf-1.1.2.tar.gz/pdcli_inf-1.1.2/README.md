## Presequisites:
- saml2aws
- aws

## Preinstall

Recommendation: You should have installed and configured saml2aws and awscli before running the following steps.

## Install


```bash
pip install pdcli-inf
```

After that you should run (Push Notification as default MFA):
```bash
pdcli-inf login
```
You also can run the following command to set the MFA Option as Passcode:
```bash
pdcli-inf login --duo-mfa-option Passcode
```

Then you can run:
```bash
pdcli-inf config
```
to set all the connections. You must input the AWS Secret Manager ARN.


Congrats! you are ready to use pdcli-inf connect. Happy coding!


## Use

#### pdcli-inf login

pdcli-inf login command trigger a `saml2aws login` with the mfa option setup

usage:
```bash
pdcli-inf login
```

#### pdcli-inf connect

pdcli-inf connect allow you access to the services you have configured.

usage:
```bash
pdcli-inf connect
```

