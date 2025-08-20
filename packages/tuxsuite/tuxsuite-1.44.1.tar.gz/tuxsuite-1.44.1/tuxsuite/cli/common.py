# -*- coding: utf-8 -*-

import pathlib
from tuxsuite.cli.utils import is_url


def common_options(sp):
    sp.add_argument(
        "-p",
        "--patch-series",
        default=None,
        help=(
            "Patches to apply before building the kernel. Accepts patch "
            "series that applies directly with 'git am' in case of a mbox "
            "file or directory. 'git quiltimport' will be used in case of a "
            "gzipped tarball (.tar.gz)"
        ),
    )
    sp.add_argument(
        "-s",
        "--show-logs",
        default=False,
        action="store_true",
        help="Prints build logs to stderr in case of warnings or errors",
    )
    sp.add_argument(
        "-n",
        "--no-wait",
        default=False,
        action="store_true",
        help="Don't wait for the builds to finish",
    )
    sp.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Directory where to download artifacts",
    )
    sp.add_argument(
        "-d",
        "--download",
        default=False,
        action="store_true",
        help="Download artifacts after builds finish",
    )
    sp.add_argument(
        "--json-out",
        help="Write json build status out to a named file path",
        type=pathlib.Path,
    )
    sp.add_argument(
        "--git-head",
        default=False,
        action="store_true",
        help="Build the current git HEAD. Overrides --git-repo and --git-ref",
    )
    sp.add_argument("--git-sha", help="Git commit")
    sp.add_argument("--git-ref", help="Git reference")
    sp.add_argument("--git-repo", help="Git repository")
    sp.add_argument(
        "-C",
        "--no-cache",
        default=False,
        action="store_true",
        help="Build without using any compilation cache",
    )
    sp.add_argument(
        "-P",
        "--private",
        default=True,
        action="store_false",
        help="Private build",
    )
    sp.add_argument(
        "--callback",
        default=None,
        help=(
            "Callback URL. Build/Test/Bake backend will send a POST "
            "request to this URL with signed data, when the respective build/test/bake "
            "completes."
        ),
        type=is_url,
    )
    sp.add_argument(
        "--callback-header",
        help=(
            "Extra header to include in the POST request sent to the "
            "build/test/bake callback URL. The header string should be a key "
            "value pair separated by a ':' (colon). This option can be used "
            "multiple times to add multiple headers. "
            "Example: --callback-header 'X-First-Name: Joe'"
        ),
        type=str,
        action="append",
    )
    sp.add_argument(
        "-E",
        "--notify-email",
        help=(
            "Email address to be notified once the respective "
            "build/test/bake/plan completes. This option can be used multiple "
            "times to add multiple notification email addresses."
        ),
        type=str,
        action="append",
    )
