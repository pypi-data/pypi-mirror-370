LIB_DIR := ./mcd_usb_hub_ctrl
EXAMPLES_DIR := ./examples
BUILD_DIR := ./dist

PYFILES := $(wildcard $(LIB_DIR)/*.py $(EXAMPLES_DIR)/*.py)

# tools
E := @echo
PYCODESTYLE := pycodestyle
PYCODESTYLE_FLAGS := --show-source --show-pep8 #--ignore=E501,E228,E722

AUTOPEP8 := autopep8
AUTOPEP8_FLAGS := --in-place

BANDIT := bandit
BANDIT_FLAGS := --format custom --msg-template \
    "{abspath}:{line}: {test_id}[bandit]: {severity}: {msg}"


HATCH := hatch


check: pycodestyle bandit


pycodestyle: $(patsubst %.py,%.pycodestyle,$(PYFILES))

%.pycodestyle:
	$(E) $(PYCODESTYLE) checking $*.py
	@$(AUTOPEP8) $(AUTOPEP8_FLAGS) $*.py
	@$(PYCODESTYLE) $(PYCODESTYLE_FLAGS) $*.py


bandit: $(patsubst %.py,%.bandit,$(PYFILES))

%.bandit:
	$(E) bandit checking $*.py
	@$(BANDIT) $(BANDIT_FLAGS) $*.py



build:
	$(HATCH) build


clean:
	$(E) Cleaning up...
	@rm -rf ./$(LIB_DIR)/__pycache__
	@rm -rf ./$(EXAMPLES_DIR)/__pycache__

	@rm -rf ./$(BUILD_DIR)


deploy: build
	$(E) Uploading package to PyPI...
	twine upload dist/*