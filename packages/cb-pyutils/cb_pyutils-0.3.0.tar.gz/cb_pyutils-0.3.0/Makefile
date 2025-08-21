CB_LOGGING_DIR := ./cb_logging
CB_LOGGING_EXAMPLES_DIR := ./examples/cb_logging

CB_TEST_RIG_DIR := ./cb_test_rig
CB_TEST_RIG_EXAMPLES_DIR := ./examples/cb_test_rig

CB_PINGY_DIR := ./cb_pingy


BUILD_DIR := ./dist

PYFILES := $(wildcard $(CB_LOGGING_DIR)/*.py \
                      $(CB_LOGGING_EXAMPLES_DIR)/*.py \
					  $(CB_TEST_RIG_DIR)/*.py \
					  $(CB_TEST_RIG_EXAMPLES_DIR)/*.py \
					  $(CB_PINGY_DIR)/*.py)

# tools
E := @echo
PYCODESTYLE := pycodestyle
PYCODESTYLE_FLAGS := --show-source --show-pep8 #--ignore=E501,E228,E722

AUTOPEP8 := autopep8
AUTOPEP8_FLAGS := --in-place

FLAKE8 := flake8
FLAKE8_FLAGS := --show-source  --ignore=E501,E228,E722

BANDIT := bandit
BANDIT_FLAGS := --format custom --msg-template \
    "{abspath}:{line}: {test_id}[bandit]: {severity}: {msg}"


HATCH := hatch


check: pycodestyle flake8 bandit


pycodestyle: $(patsubst %.py,%.pycodestyle,$(PYFILES))

%.pycodestyle:
	$(E) $(PYCODESTYLE) checking $*.py
	@$(AUTOPEP8) $(AUTOPEP8_FLAGS) $*.py
	@$(PYCODESTYLE) $(PYCODESTYLE_FLAGS) $*.py


flake8: $(patsubst %.py,%.flake8,$(PYFILES))

%.flake8:
	$(E) flake8 checking $*.py
	@$(FLAKE8) $(FLAKE8_FLAGS) $*.py


bandit: $(patsubst %.py,%.bandit,$(PYFILES))

%.bandit:
	$(E) bandit checking $*.py
	@$(BANDIT) $(BANDIT_FLAGS) $*.py



build:
	$(HATCH) build

install: build
	@pip install dist/cb_pyutils*.whl --force-reinstall

clean:
	$(E) Cleaning up...
	@rm -rf ./$(LIB_DIR)/__pycache__
	@rm -rf ./$(EXAMPLES_DIR)/__pycache__

	@rm -rf ./$(BUILD_DIR)


mrpropper: clean
	@rm -rf ./test_rig.conf


deploy: build
	$(E) Uploading package to PyPI...
	twine upload dist/*