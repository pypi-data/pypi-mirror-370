# AHEAD engine

You can use this package to implement an AI engine compatible with the AHEAD platform.

To install the package, you can use pip:

```bash
pip install aheadengine
```

The package provides a `setup_app` function that creates a Flask application. You can use this function to set up a Flask app that handles predictions based on the AHEAD platform's requirements. The `setup_app` function takes a prediction function as an argument, which should accept a `PredictPayload` and return a `PredictResponse`.

`PredictResponse` can be initialized with a dictionary where keys are strings and values are instances of `MultiChart`, `LineChart`, or `ScatterPlot`. These classes represent different types of charts that can be returned in the response.

## Getting started

A trivial engine can be implemented as follows:

```python
from aheadengine import (
    setup_app,
    PredictPayload,
    PredictResponse,
    MultiChart,
    LineChart,
    ScatterPlot,
)
from typing import List
from datetime import datetime


def predict(data: List[PredictPayload]) -> List[PredictResponse]:
    return [
        PredictResponse(
            {
                "example": MultiChart(
                    [
                        LineChart(
                            points=[[datetime.now(), 1.0], [datetime.now(), 2.0]]
                        ),
                        ScatterPlot(
                            points=[[datetime.now(), 2.0], [datetime.now(), 3.0]]
                        ),
                    ]
                )
            }
        )
        for _ in data
    ]


app = setup_app(predict_fn=predict)
if __name__ == "__main__":
    app.run(debug=True)
```

Then you can run the application with:

```bash
python example.py
```

## Development

You can use the `publish.sh` script to build and publish the package to PyPI.
