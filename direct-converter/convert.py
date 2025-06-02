import csv
import time
import logging
from prometheus_client import start_http_server, Gauge, Counter
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.info("Starting Direct Prometheus converter service...")

# Create Prometheus metrics
temperature_gauge = Gauge('direct_robot_temperature_celsius', 'Temperature from CSV (Direct)', ['robot_id'])
rows_processed = Counter('direct_csv_rows_processed_total', 'Number of CSV rows processed (Direct)', ['robot_id'])

# Global variables
latest_temperature = 0.0
latest_robot_id = "unknown"

def read_csv():
    """Read the CSV file and update metrics."""
    global latest_temperature, latest_robot_id
    try:
        with open('/data.csv') as f:
            reader = csv.DictReader(f, fieldnames=['timestamp', 'temperature', 'robot_id'])
            row = next(reader)
            latest_temperature = float(row['temperature'])
            latest_robot_id = row['robot_id']
            
            # Update Prometheus metrics
            temperature_gauge.labels(robot_id=latest_robot_id).set(latest_temperature)
            rows_processed.labels(robot_id=latest_robot_id).inc()
            
            logging.info(f"Processed temperature: {latest_temperature}°C for robot {latest_robot_id}")
    except Exception as e:
        logging.error(f"Error reading CSV: {e}")

def main():
    # Start Prometheus metrics server
    start_http_server(8000)
    logging.info("Prometheus metrics server started on port 8000")
    
    # Main loop
    while True:
        read_csv()
        time.sleep(1)

if __name__ == '__main__':
    main() 