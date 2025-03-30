modules = test_runners chibi_django chibi_user

style_test: flakes pep8

test:: run_unit_tests run_integration_tests report

middle_test:: run_unit_tests run_integration_tests

full_test:: style_test middle_test run_acceptance_tests

unit:: run_unit_tests report

ignore_test = manage.py,**/test*,venv/*,test_runners/settings/*

run_unit_tests:
	@echo "Running UNIT tests..."
	@coverage run \
		manage.py test -p"*.py" --testrunner test_runners.UnitRunner

run_integration_tests:
	@echo Running INTEGRATION tests...
	@coverage run -a \
		manage.py test -p"*.py" --testrunner test_runners.IntegrationRunner

run_acceptance_tests:
	@echo Running ACCEPTANCE tests...
	@coverage run -a \
		manage.py test -p"*.py" --testrunner test_runners.AcceptanceRunner

report:
	@coverage report

report_html: test
	@coverage html -d .html_coverage
	@nohup firefox .html_coverage/index.html > /dev/null &

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr coverage_html_report/
	rm -fr .pytest_cache

dist: clean ## builds source and wheel package
	python -m build
	ls -l dist

release: dist ## package and upload a release
	twine upload dist/*

pep8:
	@echo "Running pep8 tests..."
	@pep8 --exclude='*/migrations/*' --statistics ${modules}

flakes:
	@echo "Running flakes tests..."
	@pyflakes ${modules}
