start:
	docker-compose up web

stop:
	docker-compose stop web
	docker-compose stop celery
	docker-compose stop rabbitmq
	docker-compose stop db

build_web:
	docker-compose build web

run_tests:
	@sh -c "export TEST_ARGS=$(args) && docker-compose up --build tests"
	docker-compose stop firefox
	docker-compose stop selenium-hub

ci_tests: build_web
	docker-compose up -d db
	docker-compose up -d firefox
	docker-compose up --build  --exit-code-from tests

add_fixtures:
	docker-compose exec web python manage.py loaddata fixtures/fixtures.json

create_hits:
	docker-compose exec web python manage.py create_hits

run_selenium:
	docker-compose up -d db
	tests/selenium/explicit_run.sh $(args)
