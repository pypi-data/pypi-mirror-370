# Keys

The `keys` sub-command provides a way to manage per project credentials
/ keys in TuxSuite. These keys will be used in order to access private
repositories during a build/oebuild whenever requested or will be used
to manage other TuxSuite services which requires keys. The keys
feature is not available for community users. This sub-command
supports the following key types:

* Personal Access Token (pat)
* variables:(env|file)
* Secure Shell (ssh)

!!! info
    This command only allows viewing the public key of the stored
    ssh key for the given group. The ssh key is generated per group by the
    TuxSuite team.

## add

The `add` sub-sub-command is used to add a new key to a specific
project. The current support provides adding personal access tokens
(pat) or http username/passwords for any git server domain with
supported protocols, for example github or gitlab or variables type of
keys. To add the specified type of keys using `add` sub-sub-command,
 `--type` option is mandatory.
The `--type` option can have the following values.

* pat
* variables:env
* variables:file

The following options are mandatory for the `add` sub-sub-command for available types:

=== "pat"

    * --domain
    * --username
    * --token

=== "variables:(env|file)"

    * keys provided in `KEY=VALUE` format

!!! example "Usage"

    * Add key of type `pat`

    ```shell
    tuxsuite keys add --type pat --domain gitlab.com --username test-user-1 --token your-secret-token
    ```

    * Add key of type `variables:env`

    ```shell
    tuxsuite keys add --type variables:env KEY=VALUE
    ```

    * Add key of type `variables:file`

    ```shell
    tuxsuite keys add --type variables:file KEY=VALUE
    ```

In the above command, for type `pat` a new key of kind `pat` is being added whose
domain is provided with the `--domain` option, username is provided with
`--username` option and token is provided with the `--token` option.
Similarly for type `variables:env` key is treated as environment variable
and `variables:file` is treated as variable of type file. The group and
project is not explicitly mentioned in this command, which is obtained from
the config file `~/.config/tuxsuite/config.ini` or the `GROUP` and `PROJECT`
environment variables.

## delete

The `delete` sub-sub-command is used to delete an already added key
from a project with a specific domain and username.

The following options are mandatory for the `delete` sub-sub-command:

=== "pat"

    * --domain
    * --username

=== "variables:(env|file)"

    * Keyname

!!! example "Usage"

    * Delete key of type `pat`

    ```shell
    tuxsuite keys delete --type pat --domain gitlab.com --username test-user-1
    ```

    * Delete key of type `variables:env`

    ```shell
    tuxsuite keys delete --type variables:env KEYNAME
    ```

    * Delete key of type `variables:file`

    ```shell
    tuxsuite keys delete --type variables:file KEYNAME
    ```

In the above command, an existing key of kind `pat` for the domain
`gitlab.com` with username `test-user-1` is deleted for the project
which is obtained from the config file `~/.config/tuxsuite/config.ini`
or the `GROUP` and `PROJECT` environment variables.

## get

The `get` sub-sub-command is used to list all the available keys for a
project.

```shell
tuxsuite keys get
```

<details>
<summary>Click to see output</summary>

```

ssh public key:

ecdsa-sha2-nistp256 AAAAE2Vjanw=

pat keys:

s.no    domain        username        token

1.      github.com    test-user-1     ****
2.      gitlab.com    test-user-1     ****
3.      gitlab.com    test-user-2     ****
4.      github.com    test-user-2     ****

variables keys:

S.no       keyname                   type                      value

1          TEST                      variables:env             ****
2          FILE                      variables:file            ****

```

</details>

Use `--json` option to get the list of keys in JSON format printed to
stdout.

```shell
tuxsuite keys get --json
```

<details>
<summary>Click to see JSON output</summary>

```json
{
 "ssh": {
  "pub": "ecdsa-sha2-nistp256 AAAAE2Vjanw="
 },
 "pat": [
  {
   "token": "****",
   "username": "test-user-1",
   "domain": "gitlab.com"
  },
  {
   "token": "****",
   "username": "test-user-3",
   "domain": "gitlab.com"
  },
  {
   "token": "****",
   "username": "test-user-1",
   "domain": "github.com"
  },
  {
   "token": "****",
   "username": "test-user-2",
   "domain": "github.com"
  },
  {
   "token": "****",
   "username": "test-user-4",
   "domain": "gitlab.com"
  }
 ],
 "variables": [
  {
   "value": "****",
   "keyname": "TEST",
   "type": "variables:env"
  },
  {
   "value": "****",
   "keyname": "FILE",
   "type": "variables:file"
  }
 ]
}
```

</details>

## update

The `update` sub-sub-command is used to update an existing key already
added to a specific project. This sub-sub-command takes arguments similar to
`add` sub-sub-command.

The following options are mandatory for the `update` sub-sub-command for available types:

=== "pat"

    * --domain
    * --username
    * --token

=== "variables:(env|file)"

    * keys provided in `KEY=VALUE` format

!!! example "Usage"

    * Update key of type `pat`

    ```shell
    tuxsuite keys update --type pat --domain gitlab.com --username test-user-1 --token your-new-secret-token
    ```

    * Update key of type `variables:env`

    ```shell
    tuxsuite keys add --type variables:env KEY=VALUE
    ```

    * Update key of type `variables:file`

    ```shell
    tuxsuite keys add --type variables:file KEY=VALUE
    ```

In the above command, the existing key of kind `pat` is being updated
with a new token whose domain is provided with the `--domain` option,
username is provided with `--username` option and the new token is
provided with the `--token` option. The group and project is not
explicitly mentioned in this command, which is obtained from the
config file `~/.config/tuxsuite/config.ini` or the `GROUP` and
`PROJECT` environment variables.
