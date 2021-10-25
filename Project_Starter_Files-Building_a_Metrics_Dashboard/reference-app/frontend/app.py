from flask import Flask, render_template, request, json
from prometheus_flask_exporter.multiprocess import GunicornInternalPrometheusMetrics

app = Flask(__name__)
metrics = GunicornInternalPrometheusMetrics(app)

# Healthcheck status
@app.route('/status')
def healthcheck():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    app.logger.info('Status request successfull')
    return response

# Root route
@app.route('/')
def homepage():
    return render_template("main.html")


if __name__ == "__main__":
    app.run()
