start:
	docker-compose up web

stop:
	docker-compose stop web

run_tests:
	docker-compose up -d firefox
	docker-compose up -d db
	docker-compose up --build tests
	docker-compose stop firefox
	docker-compose stop selenium-hub
	docker-compose stop db

ci_tests:
	prospector