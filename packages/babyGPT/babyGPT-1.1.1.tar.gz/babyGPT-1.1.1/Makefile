# GNU -*- makefile -*-

#VERSION := ${shell python -c "import babyGPT;print babyGPT.__version__"}
VERSION := ${shell python3 -c "import os; os.chdir('babyGPT'); import babyGPT; print(babyGPT.__version__)"}

default:
	@echo
	@echo "  *** Welcome to babyGPT ${VERSION} ***"
	@echo
	@echo "  docs   -  Build documentation (html)"
	@echo "  help   -  Open the documentation"
	@echo
	@echo "  clean  -  Remove temporary files"
	@echo "  test   -  Run the unittests"
	@echo "  check  -  Look for rough spots"
	@echo "  sdist  -  Build a source distribution tar ball"

docs:
	pydoc3 -w babyGPT/babyGPT.py

help:
	open babyGPT-${VERSION}.html

clean:
	rm -f *.pyc *~

real-clean: clean
	rm -f MANIFEST  *.html babyGPT-py.info
	rm -rf build dist

# Run the unittest
test:
	@echo
	@echo Testing...
	@echo
	python3 ./TestBabyGPT/Test.py 

sdist: test
	@echo
	@echo Building a source distribution...
	@echo
	./setup.py sdist --formats=gztar

# Look for rough spots
check:
	@grep -n FIX *.py *.in PKG-INFO Makefile | grep -v grep
	@echo
	pychecker babyGPT


