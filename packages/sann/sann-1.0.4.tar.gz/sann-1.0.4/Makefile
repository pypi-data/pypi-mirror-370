clean:
	rm -rf build dist *.egg-info
	rm -rf .coverage
	rm -rf .pytest_cache
	rm -rf examples/digit_recognition/nn.json
	rm -rf examples/snaike/fittest_ann.json
	rm -rf examples/tanksalot/ann_evolved.json
	rm -rf examples/tanksalot/ann_supervised.json
	rm -rf examples/tanksalot/web/bot.py
	rm -rf examples/tanksalot/web/sann.py
	rm -rf examples/snaike/nn.json
	rm -rf docs/docs/*
	rm -rf docs/site
	rm -rf sann.min.py
	rm -rf examples/digit_recognition/web/sann.py
	rm -rf examples/snaike/web/sann.py
	rm -rf docs/sann.py
	find . | grep -E "(__pycache__)" | xargs rm -rf

docs: clean
	cp sann.py examples/digit_recognition/web/
	cp sann.py examples/snaike/web/
	cp sann.py examples/tanksalot/web/
	cp sann.py examples/snaike/web/
	cp examples/tanksalot/bot.py examples/tanksalot/web/
	cp sann.py docs/
	mkdir -p docs/docs/assets
	cp assets/*.svg docs/docs/assets/
	cp assets/style.css docs/docs/assets/
	cp assets/api.md docs/docs/
	cp assets/README.md docs/docs/acknowledgements.md
	cp README.md docs/docs/index.md
	cp LICENSE.md docs/docs/license.md
	cp CHANGELOG.md docs/docs/changelog.md
	cp CARE_OF_COMMUNITY.md docs/docs/CARE_OF_COMMUNITY.md
	mkdir -p docs/docs/examples/digit_recognition
	cp -r examples/digit_recognition/* docs/docs/examples/digit_recognition/
	mv docs/docs/examples/digit_recognition/README.md docs/docs/examples/digit_recognition/index.md
	mkdir -p docs/docs/examples/snaike
	cp -r examples/snaike/* docs/docs/examples/snaike/
	mv docs/docs/examples/snaike/README.md docs/docs/examples/snaike/index.md
	mkdir -p docs/docs/examples/tanksalot
	cp -r examples/tanksalot/* docs/docs/examples/tanksalot/
	mv docs/docs/examples/tanksalot/README.md docs/docs/examples/tanksalot/index.md
	cd docs && mkdocs build --clean

tidy:
	black -l 79 *.py
	black -l 79 examples/digit_recognition/*.py
	black -l 79 examples/snaike/*.py
	black -l 79 examples/tanksalot/*.py
	black -l 79 examples/tanksalot/web/*.py

test:
	pytest --cov=sann --cov-report=term-missing

check: clean tidy test

dist: check
	python3 -m build

publish-test: dist
	twine upload -r test --sign dist/*

publish: dist
	twine upload --sign dist/*

minify: check
	pyminify --remove-literal-statements sann.py --output sann.min.py