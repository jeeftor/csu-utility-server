docker:
	docker build -t csu .
dev: docker
	docker run --env-file=.env -p 8000:8000 --rm --user root -v $(shell pwd):/devel --entrypoint bash -it csu
dev-no-build:
	docker run --env-file=.env -p 8000:8000 --rm --user root -v $(shell pwd):/devel --entrypoint bash -it csu
