build:
	docker build -t mono-sast .

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm mono-sast $(ARGS)

save: build
	docker save mono-sast:latest | gzip > mono-sast.tar.gz

up:
	docker compose up

down:
	docker compose down

.PHONY: build dev up down
