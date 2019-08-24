start:
	docker-compose up web

stop:
	docker-compose stop web
	docker-compose stop db

run_tests:
	docker-compose up -d firefox

	@if [ ! -z $(docker images -q web_image:latest) ] ; then \
		docker-compose build web; \
	fi

	docker-compose up --build tests
	docker-compose stop firefox
	docker-compose stop selenium-hub

ci_tests:
	prospector