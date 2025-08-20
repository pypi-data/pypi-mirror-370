export PROJECT := tuxsuite
export TUXPKG_MIN_COVERAGE := 90

include $(shell tuxpkg get-makefile)

.PHONY: htmlcov tags

htmlcov:
	python3 -m pytest --cov=tuxsuite --cov-report=html

doc: docs/index.md
	mkdocs build

docs/index.md: README.md scripts/readme2index.sh
	scripts/readme2index.sh $@

doc-serve:
	mkdocs serve

flit = flit
publish-pypi:
	$(flit) publish

tags:
	ctags -R tuxsuite/ test/

check: style flake8 codespell

codespell:
	codespell \
		--check-filenames \
		--skip '.git,public,dist,*.sw*,*.pyc,tags,*.json,.coverage,htmlcov,*.1,*.log' \
		-L 'ttests,synopsys,busses,hda,emac'

# The purpose of validate-pre-release is to run the complete integration tests
# against prod, before making a release. The developer should take care of
# setting up the necessary config and environment in order to run it against
# prod.
validate-pre-release: scripts/validate-pre-release.sh
	scripts/validate-pre-release.sh

release: validate-pre-release
