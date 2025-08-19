# Sub-commands

## cancel

`cancel` is a subcommand for cancelling submitted build identified by its `uid`.
Cancelling is available for any build state, except `finished`.

```
tuxsuite build cancel 1t2giSA1sSKFADKPrl0YI1gjMLb
```

## config

`config` is a subcommand which fetches the config for the build
identified by its `uid`.

```
tuxsuite build config 1yiHhE3rnithNxBudqxCrWBlWKp
```

## get

`get` is a subcommand which fetches the details for the build
identified by its `uid`.

```
tuxsuite build get 1yiHhE3rnithNxBudqxCrWBlWKp
```

!!! info "Optional arguments"

    - **--json:** Output json build to stdout
    - **--json-out:** Write json build out to a named file path
    - **-l/--list-artifacts:** List the build artifacts
    - **-d/--download-artifacts:** Download the build artifacts

## list

`list` is a subcommand which fetches the latest 30 builds by default.

```
tuxsuite build list
```

In order to restrict the number of builds fetched, `--limit` is used
as follows:

```
tuxsuite build list --limit 5
```

To get the output of the above commands in JSON format, use the
following:

```
tuxsuite build list --json --limit 2
```

## logs

`logs` is a subcommand which fetches the log for the build identified
by its `uid`.

```
tuxsuite build logs 1yiHhE3rnithNxBudqxCrWBlWKp
```

## wait

`wait` is a subcommand which fetches the details for the build identified
by its `uid`, if the build is in progress, it will update the details
on screen. This will be handy to submit a build and come back at a
later point of time to watch the build's progression.

```
tuxsuite build wait 1yiHhE3rnithNxBudqxCrWBlWKp
```
