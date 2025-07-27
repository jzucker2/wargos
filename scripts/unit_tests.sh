#!/bin/sh

# Set up environment variables for testing
export FLASK_APP=app

# https://stackoverflow.com/questions/4437573/bash-assign-default-value
: ${PROMETHEUS_MULTIPROC_DIR:=/tmp}
export PROMETHEUS_MULTIPROC_DIR
: ${prometheus_multiproc_dir:=/tmp}
export prometheus_multiproc_dir
# intended for local running on pi
: ${METRICS_PORT:=9395}
export METRICS_PORT

# Set test environment
export DEBUG=false
export DEFAULT_WLED_IP=192.168.1.100
export DEFAULT_WLED_INSTANCE_SCRAPE_INTERVAL_SECONDS=60
export DEFAULT_WLED_FIRST_WAIT_SECONDS=30

# Check if a specific test module was provided
if [ $# -eq 1 ]; then
    echo "Running specific test module: $1"
    python tests/run_tests.py "$1"
else
    echo "Running all tests..."
    python tests/run_tests.py
fi
