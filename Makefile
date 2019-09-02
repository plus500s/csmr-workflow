start:
	docker-compose up web

stop:
	docker-compose stop web
	docker-compose stop db

build_web:
	docker-compose build web

run_tests:
	docker-compose up -d firefox
	docker-compose up --build tests
	docker-compose stop firefox
	docker-compose stop selenium-hub

ci_tests: build_web
	docker-compose up -d db
	docker-compose up -d firefox
	docker-compose up --build  --exit-code-from tests
