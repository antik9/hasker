prod: create_hasker_image
	docker-compose up

create_hasker_image: prepare_database
	docker build -t hasker .

prepare_database:
	bash prepare_database.sh
