# Timeouts

You can customize the timeout of each action and tests with the `--timeouts`
parameter.

This parameter accepts a `KEY=VALUE` parameter. `KEY` is the name of the action
(`deploy` or  `boot`) or the test name (like `ltp-smoke`) while `VALUE` is the
timeout value in minutes.

## Examples

Run the ltp-smoke test on the fvp-aemva model. The ltp-smoke timeout will be set to 10 minutes.

```shell
tuxsuite test --device fvp-aemva --tests ltp-smoke --timeouts ltp-smoke=10
```
