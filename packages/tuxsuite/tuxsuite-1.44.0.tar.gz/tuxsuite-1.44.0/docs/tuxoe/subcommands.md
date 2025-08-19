# Sub-commands

## get

`get` is a subcommand which fetches the details for the oebuild
identified by its `uid`.

```
tuxsuite bake get 1yiHhE3rnithNxBudqxCrWBlWKp
```

!!! info "Optional arguments"

    - **--json:** Output json bake build to stdout
    - **--json-out:** Write json bake build out to a named file path
    - **-l/--list-artifacts:** List the oebuild artifacts
    - **-d/--download-artifacts:** Download the oebuild artifacts

## list

`list` is a subcommand which fetches the latest 50 oebuilds by default.

```
tuxsuite bake list
```

In order to restrict the number of oebuilds fetched, `--limit` is used
as follows:

```
tuxsuite bake list --limit 5
```

To get the output of the above commands in JSON format, use the
following:

```
tuxsuite bake list --json --limit 2
```

## submit

`submit` is a subcommand for submitting bake build request using build definition.

```shell
tuxsuite build submit build-definition
```

## cancel

`cancel` is a subcommand for cancelling submitted build identified by its `uid`.
Cancelling is available for any build state, except `finished`.

```shell
tuxsuite build cancel 1t2giSA1sSKFADKPrl0YI1gjMLb
```
