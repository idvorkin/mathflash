# List available commands
default:
    @just --list

# Run the debug server
run:
    python3 main.py

# Deploy the server
deploy:
    modal deploy modal_server.py

# Run local testing of deployment environment
serve:
    modal serve modal_server.py

# Fetch user stats
stats:
    curl https://idvorkin--mathflash-fastapi-app.modal.run/attempts > user_stats.csv

# Open the local server (addition with max number 15)
open-add:
    open http://localhost:8888/+/15

# Open the local server (multiplication with max number 15)
open-multiply:
    open http://localhost:8888/*/15
