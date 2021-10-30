from flask import Flask, render_template, request, json
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app, group_by='endpoint')

metrics.info('app_info', 'Application Info', version='1.0.3')

# Register extra metrics
metrics.register_default(
    metrics.counter(
        'by_path_counter', 'Request count by request paths',
        labels={'path': lambda: request.path}
    )
)

# Apply the same metric to all of the endpoints
endpoint_counter = metrics.counter(
    'endpoint_counter', 'Request count by endpoints',
    labels={'endpoint': lambda: request.endpoint}
)

# Root route
@app.route('/')
@endpoint_counter
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()
