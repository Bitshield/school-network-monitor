Make all scripts executable:
bashchmod +x setup_dev.sh run.sh stop.sh logs.sh clean.sh
Usage Examples:
bash# Setup development environment
./setup_dev.sh

# Run in development mode
./run.sh -m dev -r

# Run in production mode with 8 workers
./run.sh -m prod -w 8

# Run with Docker
./run.sh -m docker

# Run tests
./run.sh -m test

# View logs
./logs.sh app

# Stop all services
./stop.sh

# Clean up
./clean.sh