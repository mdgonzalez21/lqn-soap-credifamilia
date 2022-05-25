test:
	pytest

PROJECT = .
COVFILE ?= .coverage

coverage-soap-credifamilia:
	export COVERAGE_FILE=$(COVFILE); pytest --cov-branch \
	--cov=$(PROJECT)/ $(PROJECT)/tests \
	--cov-report term-missing -x -s -vv \
	-W ignore::DeprecationWarning