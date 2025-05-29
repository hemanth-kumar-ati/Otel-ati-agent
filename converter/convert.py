import csv
import time
from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
import sys
import logging

# Global variable to hold the latest temperature and robot_id
latest_temperature = 0.0
latest_robot_id = "unknown"

# Setup OTel metrics
exporter = OTLPMetricExporter(endpoint="http://otel-collector:4317", insecure=True)
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1000)
provider = MeterProvider(resource=Resource.create({"service.name": "csv-converter"}), metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter("converter")

# Create metrics
counter = meter.create_counter("csv_rows_processed_total")

# Create observable gauge
def temperature_callback(options):
    """Callback function to get the current temperature."""
    try:
        logging.info(f"Callback triggered - Current temperature: {latest_temperature}, robot_id: {latest_robot_id}")
        return [metrics.Observation(value=float(latest_temperature), attributes={"robot_id": latest_robot_id})]
    except Exception as e:
        logging.error(f"Error in callback: {str(e)}")
        return [metrics.Observation(value=0.0, attributes={"robot_id": "unknown"})]

gauge = meter.create_observable_gauge(
    name="robot_temperature_celsius",
    callbacks=[temperature_callback],
    description="Temperature from CSV",
    unit="celsius"
)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logging.info("Starting converter service...")

# Main loop
while True:
    try:
        with open('/data.csv') as f:
            reader = csv.DictReader(f, fieldnames=['timestamp', 'temperature', 'robot_id'])
            row = next(reader)
            latest_temperature = float(row['temperature'])
            latest_robot_id = row['robot_id']
            
            # Update counter
            counter.add(1, {"robot_id": latest_robot_id})
            logging.info(f"Processed temperature: {latest_temperature}°C for robot {latest_robot_id}")
    except Exception as e:
        logging.error(f"Error reading CSV: {e}")
    time.sleep(1)
