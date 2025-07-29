#!/bin/bash

# Script to check if metrics are persisting correctly

HOST=${HOST:-localhost}
PORT=${PORT:-9395}

echo "Checking metrics persistence on $HOST:$PORT"

# Get metrics
echo "Fetching metrics..."
curl -s "http://$HOST:$PORT/metrics" > /tmp/metrics.txt

if [ $? -eq 0 ]; then
    echo "✅ Successfully fetched metrics"

    # Check for key metrics
    echo "Checking for key metrics:"

    if grep -q "wargos_instance_info" /tmp/metrics.txt; then
        echo "✅ wargos_instance_info found"
    else
        echo "❌ wargos_instance_info not found"
    fi

    if grep -q "wled_releases_info" /tmp/metrics.txt; then
        echo "✅ wled_releases_info found"
    else
        echo "❌ wled_releases_info not found"
    fi

    if grep -q "wargos_wled_instance_info" /tmp/metrics.txt; then
        echo "✅ wargos_wled_instance_info found"
    else
        echo "❌ wargos_wled_instance_info not found"
    fi

    # Count total metrics
    total_metrics=$(grep -c "^[^#]" /tmp/metrics.txt)
    echo "Total metrics found: $total_metrics"

    # Show a few sample metrics
    echo "Sample metrics:"
    grep "^[^#]" /tmp/metrics.txt | head -10

else
    echo "❌ Failed to fetch metrics"
    exit 1
fi

# Clean up
rm -f /tmp/metrics.txt
