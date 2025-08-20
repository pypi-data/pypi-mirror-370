# Results

The `results` sub-command provide a way to get the status of a
build/test/plan that has been previously submitted.

## fetch

The `results` sub-command when invoked with `fetch` sub-command shows
the latest builds, tests and plans that has been previously submitted
by the user.

```shell
tuxsuite results fetch
```

## Build

The `build` option fetches the `results` of the `build` based on the
given `uid`

```shell
tuxsuite results --build 1t26TJROt6zoxIw3YS2OlMXMGzK
```

## Test

The `test` option fetches the `results` of the `test` based on the
given `uid`

```shell
tuxsuite results --test 1s20dnMkE94e3BHW8pEbOWuyL6z
```

## Plan

The `plan` option fetches the `results` of the `plan` based on the
given `uid`

```shell
tuxsuite results --plan 1t2UxTeU15WDwvhloPFUqjmr3CX
```
