#!/usr/bin/env bash

# Function to generate random temperature
generate_temp() {
    echo $(( RANDOM % 40 + 10 ))
}

# Main loop
while true; do
    # Get current timestamp in ISO format
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Generate random temperature
    temp=$(generate_temp)
    
    # Write to CSV file
    echo "$timestamp,$temp,robot123" > data.csv
    sleep 0.5
done 