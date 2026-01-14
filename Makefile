.PHONY: run test up down migrate createsuperuser lint

# Run Django development server locally (without Docker)
run:
	python manage.py runserver

# Run Django tests
test:
	python manage.py test

# Start Docker containers
up:
	docker-compose up -d

# Stop Docker containers
down:
	docker-compose down

# Apply database migrations (inside Docker)
migrate:
	docker-compose run web python manage.py migrate

# Create a Django superuser (inside Docker)
createsuperuser:
	docker-compose run web python manage.py createsuperuser

# Run linting and formatting checks
lint:
	ruff . && black --check . && isort --check-only .
