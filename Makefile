HOST_PYTHON=$(shell which python3)
VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

pyc=$(shell find . -name '*.pyc')
srcs+=*.py
srcs+=lmcore/*.py

doc_srcs+=doc/manual.md
doc_target=doc/manual.html

test_srcs+=unittests/*.py
test_srcs+=lmcore/unittests/*.py
test_srcs+=db_utils/*.py

OK_TEST=.ok_test
OK_PIP=.ok_pip
OK_PACKAGES=.ok_packages
OKS+=$(OK_VENV)
OKS+=$(OK_PACKAGES)

all: $(OK_TEST) doc

doc: $(doc_target)

$(doc_target): $(doc_srcs)
	@multimarkdown $(doc_srcs) > $(doc_target)
	@echo "Make documentation"

md5:
	find . -name '*.py' -exec md5sum \{\} \; > md5.txt

$(OK_TEST): $(srcs) $(test_srcs) $(OK_PACKAGES)
	@PYTHONPATH=$$(pwd)/lmcore $(PYTHON) -m unittest discover
	touch $@

$(VENV):
	$(HOST_PYTHON) -m venv $(VENV) && touch $@

$(OK_PIP): $(OK_VENV)
	$(PIP) install --upgrade pip && touch $@

$(OK_PACKAGES): $(VENV) requirements.txt
	$(PIP) install -r requirements.txt && touch $@

clean:
	@rm -f $(pyc)
	@rm -f $(doc_target) $(OK_TEST)
	@rm -rf dist/*

envclean:
	@rm -rf $(VENV)
	@rm -f $(OK_PACKAGES)
