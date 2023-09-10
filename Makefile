install:
	pipenv install .

install_dev:
	pipenv install --editable .

shell:
	pipenv shell

which:
	pipenv --venv

remove:
	pipenv --rm

run:
	pipenv run python3 bin/run.py encode

run2:
	pipenv run python3 bin/run.py probe
