# Stimulsoft Dashboards.PYTHON

Data visualization in Python applications.

## About the product

Stimulsoft Dashboards.PYTHON is a fast and powerful tool for creating analytical dashboards in services and projects written in Python. The product includes a JavaScript data processing engine, a designer component for creating dashboards, and a fully interactive viewer for viewing ready-made dashboards on the screen of any device.

Stimulsoft Dashboards.PYTHON is a client-server system wherein a JavaScript component operates on the client side, and a Python server is responsible for data processing. These two parts are closely related and represent a single product that greatly simplifies working with dashboards in web applications written in Python.


## Install dashboard components

To install the **Stimulsoft Dashboards.PYTHON**, you can use the specified command:
```
python -m pip install stimulsoft-dashboards
```

## Working with data analysis tool

### Dashboard Engine

The **StiReport** component is designed to work with the dashboard engine in a Web project. Using this component, you can create a dashboard, load a dashboard from a file or string, and call a dashboard export function.

> For simplicity, all code examples in this tutorial use the Flask framework (any other can be used).

The code example shows how you can load a dashboard from a file, and export it to HTML format:

### app.py

```python
from flask import Flask, render_template, url_for, request
from stimulsoft_reports.report import StiReport
from stimulsoft_reports.report.enums import StiExportFormat

app = Flask(__name__)

@app.route('/report', methods = ['GET', 'POST'])
def report():
    report = StiReport()
    if report.processRequest(request):
        return report.getFrameworkResponse()

    report.loadFile(url_for('static', filename='reports/Financial.mrt'))
    report.render()
    report.exportDocument(StiExportFormat.HTML)

    js = report.javascript.getHtml()
    html = report.getHtml()
    return render_template('report.html', reportJavaScript = js, reportHtml = html)
```

### report.html

```html
<!DOCTYPE html>
<html>

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Load and Export a Dashboard</title>

    {{ reportJavaScript|safe }}
</head>

<body>
    {{ reportHtml|safe }}
</body>

</html>
```

More details in [our documentation](https://www.stimulsoft.com/en/documentation/online/programming-manual/index.html?reports_python.htm).


### Report Viewer

The **StiViewer** component is designed for viewing, printing and exporting dashboards in a browser window. Full support for working with interactive dashboards has been implemented. Using this component, you can create a viewer object, set the necessary options, process the request and return the result of its execution, and receive the prepared JavaScript and HTML code of the component.

An example of displaying a viewer on an HTML page:

### app.py

```python
from flask import Flask, render_template, url_for, request
from stimulsoft_reports.viewer import StiViewer

app = Flask(__name__)

@app.route('/viewer', methods = ['GET', 'POST'])
def viewer():
    viewer = StiViewer()
    viewer.options.appearance.fullScreenMode = True

    if viewer.processRequest(request):
        return viewer.getFrameworkResponse()

    report = StiReport()
    report.loadFile(url_for('static', filename='dashboards/Financial.mrt'))
    viewer.report = report

    js = viewer.javascript.getHtml()
    html = viewer.getHtml()
    return render_template('viewer.html', viewerJavaScript = js, viewerHtml = html)
```

### viewer.html

```html
<!DOCTYPE html>
<html>

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Showing a Dashboard in the Viewer</title>

    {{ viewerJavaScript|safe }}
</head>

<body>
    {{ viewerHtml|safe }}
</body>

</html>
```

There is a simplified deployment of the viewer without using an HTML page template. For example, this same example can be implemented using only Python code:

### app.py

```python
from flask import Flask, url_for, request
from stimulsoft_reports.viewer import StiViewer

app = Flask(__name__)

@app.route('/viewer', methods = ['GET', 'POST'])
def viewer():
    viewer = StiViewer()
    viewer.options.appearance.fullScreenMode = True

    if viewer.processRequest(request):
        return viewer.getFrameworkResponse()

    report = StiReport()
    report.loadFile(url_for('static', filename='dashboards/Financial.mrt'))
    viewer.report = report

    return viewer.getFrameworkResponse()
```

More details in [our documentation](https://www.stimulsoft.com/en/documentation/online/programming-manual/index.html?reports_python.htm).


### Reports Designer

The **StiDesigner** component is designed for developing dashboards in a browser window. The designer's interface is built using HTML5, which allows it to be used on almost any modern platform and different operating systems. JavaScript technology used to build reports allows you to use almost any low-performance server side.

An example of displaying a designer on an HTML page:

### app.py

```python
from flask import Flask, render_template, url_for, request
from stimulsoft_reports.designer import StiDesigner

app = Flask(__name__)

@app.route('/designer', methods = ['GET', 'POST'])
def designer():
    designer = StiDesigner()
    designer.options.appearance.fullScreenMode = True

    if designer.processRequest(request):
        return designer.getFrameworkResponse()

    report = StiReport()
    report.loadFile(url_for('static', filename='dashboards/Financial.mrt'))
    designer.report = report

    js = designer.javascript.getHtml()
    html = designer.getHtml()
    return render_template(designer.html', designerJavaScript = js, designerHtml = html)

```

### designer.html

```html
<!DOCTYPE html>
<html>

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Editing a Dashboard Template in the Designer</title>

    {{ designerJavaScript|safe }}
</head>

<body>
    {{ designerHtml|safe }}
</body>

</html>
```

There is a simplified deployment of the designer without using an HTML page template. For example, this same example can be implemented using only Python code:

### app.py

```python
from flask import Flask, url_for, request
from stimulsoft_reports.designer import StiDesigner

app = Flask(__name__)

@app.route('/designer', methods = ['GET', 'POST'])
def designer():
    designer = StiDesigner()
    designer.options.appearance.fullScreenMode = True

    if designer.processRequest(request):
        return designer.getFrameworkResponse()

    report = StiReport()
    report.loadFile(url_for('static', filename='dashboards/Financial.mrt'))
    designer.report = report

    return designer.getFrameworkResponse()
```

More details in [our documentation](https://www.stimulsoft.com/en/documentation/online/programming-manual/index.html?reports_python.htm).

## Useful links

* [Live Demo](http://demo.stimulsoft.com/#Js)
* [Product Page](https://www.stimulsoft.com/en/products/dashboards-python)
* [Free Download](https://www.stimulsoft.com/en/downloads)
* [PyPI](https://pypi.org/project/stimulsoft-dashboards/)
* [Documentation](https://www.stimulsoft.com/en/documentation/online/programming-manual/index.html?reports_python.htm)
* [License](https://www.stimulsoft.com/en/licensing/developers)