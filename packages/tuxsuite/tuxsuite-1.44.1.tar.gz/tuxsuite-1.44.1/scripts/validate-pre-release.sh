#!/bin/sh

set -eux

echo "Running pre release, validation ... \n\n"

git checkout master  # Run from master since the release will be made from it
pip install .        # install the master code
export TUXSUITE_ENV=prod
rm -rf /tmp/integration_tests
git clone git@gitlab.com:LinaroLtd/tuxsuite.com/integration_tests.git /tmp/integration_tests
cd /tmp/integration_tests
make -j4 builds oebuilds tests plans

echo "Pre release, validation complete."
