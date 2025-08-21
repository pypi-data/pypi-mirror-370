.PHONY: build test upload clean

build:
	python -m build

test:
	hatch env run test

upload:
	python -m twine upload dist/*

clean:
	rm -rf dist/ build/ *.egg-info/

# Upload to test PyPI
upload-test:
	python -m twine upload --repository testpypi dist/*