from flask import Flask, request, jsonify, abort
from typing import Callable, Dict, Any, List


# Visit contains the timestamp and values for a visit.
class Visit:
    timestamp: str
    values: Dict[str, Any]

    def __init__(self, timestamp: str, values: Dict[str, Any]):
        self.timestamp = timestamp
        self.values = values


class PredictPayload:
    visits: List[Visit]

    def __init__(self, raw_data: Dict[str, Any]):
        """Validate the JSON payload format."""
        if (
            not isinstance(raw_data, dict)
            or "visits" not in raw_data
            or not isinstance(raw_data["visits"], list)
        ):
            raise ValueError("Invalid payload format. 'visits' must be a list.")

        for visit in raw_data["visits"]:
            if (
                not isinstance(visit, dict)
                or "timestamp" not in visit
                or "values" not in visit
            ):
                raise ValueError("Each visit must contain 'timestamp' and 'values'.")
            if not isinstance(visit["values"], dict):
                raise ValueError("'values' must be a dictionary.")

        # Initialize visits with validated data
        self.visits = [
            Visit(visit["timestamp"], visit["values"]) for visit in raw_data["visits"]
        ]


class Chart:
    # Returns the response in a format that can be serialized to JSON.
    def dump(self):
        raise NotImplementedError("This method should be implemented in subclasses.")


class LineChart(Chart):
    kind: str = "LineChart"
    points: List[List[Any]]

    def __init__(self, points: List[List[Any]]):
        self.points = points

    def dump(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "points": self.points,
        }


class ScatterPlot(Chart):
    kind: str = "ScatterPlot"
    points: List[List[Any]]

    def __init__(self, points: List[List[Any]]):
        self.points = points

    def dump(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "points": self.points,
        }


class MultiChart(Chart):
    kind: str = "MultiChart"
    charts: List[Chart]

    def __init__(self, charts: LineChart | ScatterPlot):
        # Validate that charts is a list of LineChart or ScatterPlot instances
        for chart in charts:
            if not isinstance(chart, (LineChart, ScatterPlot)):
                raise TypeError(
                    "charts must be a list of LineChart or ScatterPlot instances."
                )

        self.kind = "MultiChart"
        self.charts = charts

    def dump(self) -> Dict[str, Any]:
        return {
            "kind": self.kind,
            "charts": [chart.dump() for chart in self.charts],
        }


class PredictResponse:
    charts: Dict[str, Chart]

    def __init__(self, charts: Dict[str, Chart]):
        """Initialize the response with a dictionary of charts."""
        if not isinstance(charts, dict):
            raise TypeError("charts must be a dictionary of Chart instances.")
        for key, chart in charts.items():
            if not isinstance(key, str):
                raise TypeError("Keys in charts must be strings.")
            if not isinstance(chart, Chart):
                raise TypeError(f"'{key}' must be a Chart instance.")

        self.charts = charts

    # Returns the response in a format that can be serialized to JSON.
    def dump(self):
        return {"charts": {key: chart.dump() for key, chart in self.charts.items()}}


def setup_app(
    predict_fn: Callable[[List[PredictPayload]], List[PredictResponse]],
) -> Flask:
    """Initialize the Flask application."""
    app = Flask(__name__)

    @app.route("/")
    def home():
        return "<h1>This is an AHEAD inference server</h1>"

    @app.route("/v1/predict", methods=["POST"])
    def predict():
        # Parse the JSON payload
        raw_data = request.get_json()
        if not isinstance(raw_data, list):
            abort(400, description="Payload must be a list of visits.")

        try:
            data = [PredictPayload(item) for item in raw_data]
        except Exception as e:
            abort(400, description=f"Invalid payload: {str(e)}")

        # Run the prediction
        try:
            response = predict_fn(data)
        except Exception as e:
            abort(500, description=f"Prediction function error: {str(e)}")

        # Validate the response
        if not isinstance(response, list):
            abort(
                500,
                description="Prediction function must return a list of PredictResponse.",
            )
        if not all(isinstance(resp, PredictResponse) for resp in response):
            abort(
                500,
                description="All items in the response must be PredictResponse instances.",
            )

        # Return the response as JSON
        return jsonify([resp.dump() for resp in response])

    return app
