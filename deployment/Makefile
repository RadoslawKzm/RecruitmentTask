.PHONY: up-dev
up-build:
	docker compose -f docker-compose.yaml build

.PHONY: up-dev
up-dev:
	#docker compose -f docker-compose.yaml down
	@${MAKE} down-dev
	@${MAKE} up-build
	docker compose -f docker-compose.yaml up -d

.PHONY: up-db
up-db:
	#docker compose -f docker-compose.yaml down
	@${MAKE} down-dev
	@${MAKE} up-build
	docker compose -f docker-compose.yaml up -d postgres-db

.PHONY: down-dev
down-dev:
	docker compose -f docker-compose.yaml down

.PHONY: down-dev-volumes
down-dev-volumes:
	docker compose -f docker-compose.yaml down -v

.PHONY: up-backend
up-backend:
	docker compose -f docker-compose.yaml down backend
	docker compose -f docker-compose.yaml build backend
	docker compose -f docker-compose.yaml up -d backend

.PHONY: up-locust
up-locust:
	docker compose -f locust-compose.yaml down
	docker compose -f locust-compose.yaml up -d --scale locust-worker=4

.PHONY: down-locust
down-locust:
	docker compose -f locust-compose.yaml down



#.PHONY: up-db
#up-frontend:
#	docker compose -f docker-compose.yaml down postgres-db
#	docker compose -f docker-compose.yaml build postgres-db
#	docker compose -f docker-compose.yaml up -d postgres-db
