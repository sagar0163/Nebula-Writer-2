.PHONY: install run test docker-build docker-run clean

# Install dependencies
install:
	pip install -r requirements.txt

# Run the API server
run:
	cd backend && uvicorn main:app --reload --port 8000

# Run the interactive REPL
repl:
	python repl.py

# Run tests
test:
	pytest tests/ -v

# Docker build
docker-build:
	docker build -t nebula-writer .

# Docker run
docker-run:
	docker-compose up -d

# Docker stop
docker-stop:
	docker-compose down

# Clean up
clean:
	rm -rf data/
	rm -rf __pycache__/
	rm -rf backend/__pycache__/
	rm -rf tests/__pycache__/
	find . -name "*.pyc" -delete
