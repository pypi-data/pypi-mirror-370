# Powered by TuxMake

The actual build implementation that TuxBuild uses comes directly from
[TuxMake](https://tuxmake.org).

TuxMake is an open source command line tool and Python library that provides
portable and repeatable Linux kernel builds across a variety of architectures,
toolchains, kernel configurations, and make targets.

Each TuxBuild build provides a `tuxmake_reproducer.sh` file which shows how to
reproduce the build locally, using TuxMake.

Because TuxMake uses curated build environments via containers, the exact same
build performed by TuxBuild can also be reproduced locally.

Read more about TuxMake at [tuxmake.org](https://tuxmake.org) or at
[LWN](https://lwn.net/Articles/841624/).
