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

clean:
	@echo "Running clean..."
	@find . -name ".*.sw*" -exec rm {} +
	@rm -r .coverage .html_coverage

pep8:
	@echo "Running pep8 tests..."
	@pep8 --statistics ${modules}

flakes:
	@echo "Running flakes tests..."
	@pyflakes ${modules}
