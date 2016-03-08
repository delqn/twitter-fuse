.DEFAULT_GOAL := all

.PHONY: all
all: install-prepush lint

.PHONY: lint
lint:
	pep8 twitter_fuse/ ./*.py
	pylint --rcfile=.pylintrc twitter_fuse/ ./*.py

.PHONY: install-prepush
install-prepush:
	@-if [ -d .git ] && [ ! -h .git/hooks/pre-push ] ; then \
		ln -s ../../prepush .git/hooks/pre-push; \
	fi

.PHONY: clean
clean:
	find . -name \*.pyc -delete

.PHONY: test
test: clean lint
	nosetests $(find . -name "_test.py")

.PHONY: requirements
requirements:
	pip install -r requirements.txt
