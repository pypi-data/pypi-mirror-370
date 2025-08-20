# Sub-commands

## cancel

`cancel` is a subcommand for cancelling submitted plan identified by its `uid`.
Cancelling is available for any build/oebuild/test state, except `finished`.

```
tuxsuite plan cancel 1t2giSA1sSKFADKPrl0YI1gjMLb
```

## get

`get` is a subcommand which fetches the details for the plan
identified by its `uid`.

```
tuxsuite plan get 1t2gzLqkWHi2ldxDETNMVHPYBYo
```

## list

`list` is a subcommand which fetches the latest 30 plans by default.

```
tuxsuite plan list
```

In order to restrict the number of plans fetched, `--limit` is used
as follows:

```
tuxsuite plan list --limit 5
```

To get the output of the above commands in JSON format, use the
following:

```
tuxsuite plan list --json --limit 2
```

## submit

`submit` is a subcommand for submitting plan files.

```
tuxsuite plan submit plan.yaml
```

## wait

`wait` is a subcommand which fetches the details for the plan identified
by its `uid`, if the plan is in progress, it will update the details
on screen. This will be handy to submit a plan and come back at a
later point of time to watch the plan's progression.

```
tuxsuite plan wait 1yiHhE3rnithNxBudqxCrWBlWKp
```
