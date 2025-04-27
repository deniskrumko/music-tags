run:
	@PYTHONPATH=. python src/main.py

dev:
	@textual run --dev src/main.py

console:
	@textual console

# Install deps
deps:
	pip install pipenv
	pipenv install --dev

check:
	black .
	isort .
	flake8 .
	mypy .
