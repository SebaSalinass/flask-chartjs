# Flask-ChartJS

Flask-ChartJS provides a simple interface to use ChartJS javascript library with Flask.

## Installation

Install the extension with pip:

```bash
pip install flask-chartjs-manager
```

## Usage

Once installed the Flask-ChartJS-Manager is easy to use.Let's walk through setting up a basic application. Also please note that this is a very basic guide: we will be taking shortcuts here that you should never take in a real application.

To begin we'll set up a Flask app:

```python
import flask

app = flask.Flask(__name__)
```

Flask-ChartJS works via a ChartJS object. To kick things off, we'll set up the chartjs manager by instantiating it and telling it about our Flask app:

```python
from flask_chartjs import ChartJSManager

chartjs_manager = ChartJSManager()
chartjs_manager.init_app(app)
```

This will make available the `load_chartjs` function into the templates context so you could load the javascript package easily, like this.

```html
<head>
  {{ load_chartjs() }}
</head>
```

Now we will construct a basic chart.

```python
from flask_chartjs import Chart, DataSet
from flask import render_template

@app.get('/chart-example')
def chart_example():
    
    chart = Chart('income-outcome', 'bar') # Requires at least an ID and a chart type.
    
    dataset_income = DataSet('Income', [100,200,300])
    dataset_outcome = DataSet('OutCome', [50,100,150])
    
    chart.data.add_labels('jan', 'feb', 'mar')
    chart.data.add_dataset(dataset_income)
    chart.data.add_dataset(dataset_outcome)

    return render_template('path/to/template.html', my_chart=chart)

```

Once created you can pass it to a render_template and use it likewise.

```html
<!-- load_chartjs() must be called before this line -->
<div class="my-classes">{{ render_chart(my_chart) }}</div>
```
