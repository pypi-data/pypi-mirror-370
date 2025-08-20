# Positional arguments

* `build-definition`: YAML file/URL containing the build definition for OE build.

## Optional arguments

* `-l / local-manifest`: Path/URL to a local manifest file which will be used during repo sync. This input is ignored if sources used is git_trees in the build definition. Should be a valid XML.

* `-pm / pinned-manifest`: Path/URL to a pinned manifest file which will be used during repo sync. This input is ignored if sources used is git_trees in the build definition. Should be a valid XML.

* `-k / kas-override`: Path/URL to a kas config yml/yaml file which is appended to kas_yaml parameter. This can be used to override the kas yaml file that is passed. This option is specific to kas builds.

* `-n / --no-wait`: Don't wait for the builds to finish

* `-d / --download`: Download artifacts after builds finish. Can't be used with no-wait

* `-o / --output-dir`: Directory where to download artifacts

* `-C / --no-cache`: Build without using any compilation cache

* `-P / --private`: Private build

* `--callback`: Callback URL. The bake backend will send a POST request to this URL with signed data, when bake completes.

* `--callback-header`: It is an optional argument to bake `submit` subcommand through which the user can supply extra header to include in the POST request sent to the callback URL. The header string should be a key value pair separated by a ':' (colon). This option can be used multiple times to add multiple headers. This option depends on the `--callback` option.

* `-E / --notify-email`: Sends the result of the bake build, at the end of the bake build to the given email address. This option can be used multiple times to add multiple email addresses to notify.
