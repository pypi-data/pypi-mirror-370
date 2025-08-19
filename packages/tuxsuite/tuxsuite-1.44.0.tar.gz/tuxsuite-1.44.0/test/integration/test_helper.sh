TEST_DIRNAME=$(readlink -f ${0%/*})

export TUXSUITE_DELAY_STATUS_UPDATE=0

run() {
  status=0
  output="$("$@" 2>&1)" || status=$?
  if [ -n "${TUXSUITE_TEST_VERBOSE:-}" ]; then
    echo "${output}"
  fi
  export output status
}


setUp() {
    ########################################################################
    # mimic pytest tmpdir
    ########################################################################
    BASETMPDIR=${TMPDIR:-/tmp}/tests-of-$(id -un)
    mkdir -p "${BASETMPDIR}"
    last=$(ls -1 "${BASETMPDIR}"/ | grep '^[0-9]*$' | sort -n | tail -1)
    if [ -z "$last" ]; then
        last=0
    fi
    next=$((last + 1))
    newtmpdir=$(mktemp --directory --tmpdir=$BASETMPDIR)
    while ! mv "${newtmpdir}" "${BASETMPDIR}/${next}"; do
        next=$((next + 1))
    done
    export tmpdir="${BASETMPDIR}/${next}"
    ########################################################################

    mkdir -p "${tmpdir}/.config/tuxsuite"
    local config="${tmpdir}/.config/tuxsuite/config.ini"
    echo "[default]" > "${config}"
    echo "token=0123456789" >> ${config}
    echo "api_url=http://localhost:5001/v1" >> "${config}"
    echo "tuxapi_url=http://localhost:5001" >> "${config}"
    echo "group=tuxsuite" >> "${config}"
    echo "project=integration-test" >> "${config}"
    export TUXSUITE_CONFIG="${config}"

    cat > "${tmpdir}/builds.yaml" <<EOF
sets:
  - name: basic
    builds:
      - {target_arch: arm64, toolchain: gcc-9, kconfig: defconfig}
      - {target_arch: arm64, toolchain: gcc-9, kconfig: allmodconfig}
      - {target_arch: arm64, toolchain: gcc-9, kconfig: allyesconfig}
      - {target_arch: arm, toolchain: gcc-9, kconfig: allmodconfig}
      - {target_arch: x86_64, toolchain: gcc-9, kconfig: allmodconfig}
      - {target_arch: x86_64, toolchain: clang-9, kconfig: allmodconfig}
      - {target_arch: x86_64, toolchain: gcc-9, kconfig: allyesconfig}
      - {target_arch: i386, toolchain: gcc-9, kconfig: allmodconfig}
      - {target_arch: riscv, toolchain: gcc-9, kconfig: allyesconfig}
EOF

    cd "${tmpdir}"
}

api_v1() {
    HOME="${tmpdir}" nohup python3 "${TEST_DIRNAME}/../api_v1.py" --port=5001 "$@" > "${tmpdir}/api.log" 3>&- &
    echo "$!" > "${tmpdir}/api.pid"
    # wait for api server to be available
    while ! curl --fail --silent --output /dev/null 'http://localhost:5001/'; do
      sleep 0.1
    done
}

tearDown() {
    if [ -f "${tmpdir}"/api.pid ]; then
        pid="$(cat "${tmpdir}"/api.pid)"
        rm -f "${tmpdir}/api.pid"
        kill -9 "${pid}" >/dev/null 2>&1
    fi
    rm -f "${tmpdir}/api.log"
}

if [ $# -gt 0 ]; then
  export TESTCASES="$(echo "$@")"
  set --
  suite() {
    for t in $TESTCASES; do
      suite_addTest "$t"
    done
  }
fi
