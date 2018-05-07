prod: create_hasker_image
	docker-compose up

create_hasker_image:
	docker build -t hasker .