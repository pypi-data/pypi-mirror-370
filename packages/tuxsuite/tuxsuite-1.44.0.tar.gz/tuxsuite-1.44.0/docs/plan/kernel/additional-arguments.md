
# callback

`--callback` is an optional argument to plan `submit` subcommand which POSTs JSON data that has
the status of the respective plan `build` or `test`, at the end of the respective `build` or `test` to the given URL. The
URL should be a valid http(s) link that accepts POST data.

# callback header

`--callback-header` is an optional argument to plan `submit`
subcommand through which the user can supply extra header to include
in the POST request sent to the callback URL. The header string
should be a key value pair separated by a ':' (colon). This option can
be used multiple times to add multiple headers. This option depends on
the `--callback` option.

Example:

```sh
tuxsuite plan submit \
--callback https://tuxapi.tuxsuite.com/v1/test_callback \
--callback-header "X-First-Name: Senthil" \
--callback-header "X-Last-Name: Kumaran" \
--callback-header "X-Initial: S" \
planv1.yaml
```

# plan callback

`--plan-callback` is an optional argument to plan `submit` subcommand
which POSTs JSON data that has the status of the plan, at the end of
the plan completion (when all the builds and tests that are part of
the plan completes) to the given URL. The URL should be a valid
http(s) link that accepts POST data.

[See Callbacks Reference, for more details](../../callbacks.md)

# plan callback header

`--plan-callback-header` is an optional argument to plan `submit`
subcommand through which the user can supply extra header to include
in the POST request sent to the plan callback URL. The header string
should be a key value pair separated by a ':' (colon). This option can
be used multiple times to add multiple headers. This option depends on
the `--plan-callback` option.

Example:

```sh
tuxsuite plan submit \
--plan-callback https://tuxapi.tuxsuite.com/v1/test_callback \
--plan-callback-header "X-First-Name: Senthil" \
--plan-callback-header "X-Last-Name: Kumaran" \
--plan-callback-header "X-Initial: S" \
planv1.yaml
```

## notify-email

`--notify-email` or `-E` is an optional argument which sends the
status of the plan, at the end of the plan completion to the given
email address. This option can be used multiple times to add multiple
email addresses to notify.

```sh
tuxsuite plan submit \
--git-repo https://github.com/torvalds/linux.git \
--git-ref master \
--notify-email test-1@linaro.org \
-E test-2@linaro.org \
planv1.yaml
```
