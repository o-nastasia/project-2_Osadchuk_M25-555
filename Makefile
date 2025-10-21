install:
	poetry install
 
project:
	poetry run project

database:
	poetry run database

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

make lint:
	 poetry run ruff check .