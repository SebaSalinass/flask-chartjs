# Flask-ChartJS-Manager

Flask-ChartJS-Manager *(from now on **FCM**)* provides a simple interface to use ChartJS javascript library with Flask.

```{warning}
🚧 This package is under heavy development..
```
## Installation

Install the extension with pip:

```bash
pip install flask-chartjs-manager
```

Install with poetry:
```bash
poetry add flask-chartjs-manager
```

## Usage

Once installed the **FCM** is easy to use. Let's walk through setting up a basic application. Also please note that this is a very basic guide: we will be taking shortcuts here that you should never take in a real application.

To begin we'll set up a Flask app:

```python
from flask import Flask

app = Flask(__name__)
```

### Setting up extension
**FCM** works via a ChartJSManager object. To kick things off, we'll set up the `chartjs_manager` by instantiating it and telling it about our Flask app:

```python
from flask_chartjs import ChartJSManager

chartjs_manager = ChartJSManager()
chartjs_manager.init_app(app)
```
### Load resources
Once the extension is set up, this will make available the `load_chartjs` function into the templates context so you could load the javascript package easily, like this.

```html
<head>
  {{ load_chartjs() }}
</head>
```
### Creating a chart
Now we will construct a basic chart. For this you have to import `Chart` and `DataSet` objects in order to create a new chart.

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
### Rendering the chart
Once created you can pass the `Chart` object to render_template and use it likewise.

```html
<!-- load_chartjs() must be called before this line -->
<div class="my-classes">{{ render_chart(my_chart) }}</div>
```
