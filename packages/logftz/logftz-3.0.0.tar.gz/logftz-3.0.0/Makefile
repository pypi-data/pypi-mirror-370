.PHONY: dist upload

dist:
	rm -f dist/*
	python setup.py sdist build

upload:
	twine upload dist/*
