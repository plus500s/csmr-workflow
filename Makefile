start:
	docker-compose up web

stop:
	docker-compose stop web

tests:
	docker-compose up tests

ci_tests:
	prospector