PYTHON     ?= python3
PIP        ?= pip3

all: README.rst sdist bdist_wheel

README.rst: README.md
	pandoc --from markdown --to rst $^ -o $@

clean: 
	rm -rf src/py_encase.egg-info dist/* build/* *~ test/*~ src/py_encase/*~ src/py_encase/__pycache__ src/py_encase/share/data/*~

distclean: clean
	rm -rf py_encase.egg-info dist build README.rst

sdist: README.rst
	$(PYTHON) setup.py $@

bdist_wheel: README.rst
	$(PYTHON) setup.py $@

test_upload: sdist bdist_wheel
	twine upload --verbose --repository pypitest dist/*

upload: sdist bdist_wheel
	twine upload --verbose dist/*

