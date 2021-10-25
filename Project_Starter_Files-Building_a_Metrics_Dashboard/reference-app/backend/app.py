from flask import Flask, render_template, request, jsonify, json
import pymongo
import os
from flask_pymongo import PyMongo
# Add these so that prometheus will be able to read from this data
from prometheus_flask_exporter import PrometheusMetrics
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
# This is for flask requests
from opentelemetry.instrumentation.flask import FlaskInstrumentor
# This is for Gunicorn multiprocessing
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

# set the tracer and define the tracer provider
trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: "backend-service"})))
# Create the exporter for jaeger
jaeger_exporter = JaegerExporter()

# Add the exporter to the spanner
spanner = BatchSpanProcessor(jaeger_exporter)

# Make sure it is added here
trace.get_tracer_provider().add_span_processor(spanner)

# make sure to define the tracer here
tracer = trace.get_tracer(__name__)

# Define the app, the Prometheus Metrics and the instrumentor for Flask, also determine the server used

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app, excluded_urls="metrics")
gunicorn_app = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
if gunicorn_app:
    metrics = GunicornInternalPrometheusMetrics(app)
else:
    metrics = PrometheusMetrics(app)

# Define the database and the URI for MongoDB
app.config['MONGO_DBNAME'] = 'example-mongodb'
app.config['MONGO_URI'] = 'mongodb://example-mongodb-svc.default.svc.cluster.local:27017/example-mongodb'

mongo = PyMongo(app)

# Home route
@app.route('/')
def homepage():
    with tracer.start_as_current_span('hello-world'):
        message = "Hello world"
    return message

# API route
@app.route('/api')
def my_api():
    with tracer.start_as_current_span('api'):
        answer = "something"
    return jsonify(repsonse=answer)

# Star route
@app.route('/star', methods=['POST'])
def add_star():
  star = mongo.db.stars
  name = request.json['name']
  distance = request.json['distance']
  star_id = star.insert({'name': name, 'distance': distance})
  new_star = star.find_one({'_id': star_id })
  output = {'name' : new_star['name'], 'distance' : new_star['distance']}
  return jsonify({'result' : output})

# health check
@app.route('/status')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Status request successfull')
    return response


if __name__ == "__main__":
    app.run()
