# Stimulsoft Reports.PYTHON

A powerful and modern reporting tool for Python services.

## About the product

Stimulsoft Reports.PYTHON comprises a set of components for creating, viewing, exporting, and printing reports in applications and projects written in Python. The product supports connections of multiple data types, allowing you to work with reports on the server- and client-sides, and also offers extensive capabilities for data visualization and analysis.

Stimulsoft Reports.PYTHON is based on client-server technology: a Python application on the server-side and a JavaScript reporting engine on the client-side. These two parts are closely related and represent a single product that greatly simplifies working with reports in web applications written in Python.


## Install reporting components

To install the **Stimulsoft Reports.PYTHON**, you can use the specified command:
```
python -m pip install stimulsoft-reports
```

## Working with report generator

### Report Engine

The **StiReport** component is designed to work with the report generator in a Web project. Using this component, you can create a report, load a report from a file or string, render a report, and call a report export function.

> For simplicity, all code examples in this tutorial use the Flask framework (any other can be used).

The code example shows how you can load a report from a file, render it, and export it to HTML format:

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

    report.loadFile(url_for('static', filename='reports/SimpleList.mrt'))
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
    <title>Render and Export a Report</title>

    {{ reportJavaScript|safe }}
</head>

<body>
    {{ reportHtml|safe }}
</body>

</html>
```

More details in [our documentation](https://www.stimulsoft.com/en/documentation/online/programming-manual/index.html?reports_python.htm).


### Report Viewer

The **StiViewer** component is designed for viewing, printing and exporting reports in a browser window. The viewer can display it as a report template, as an already built report. Using this component, you can create a viewer object, set the necessary options, process the request and return the result of its execution, and receive the prepared JavaScript and HTML code of the component.

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
    report.loadFile(url_for('static', filename='reports/SimpleList.mrt'))
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
    <title>Showing a Report in the Viewer</title>

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
    report.loadFile(url_for('static', filename='reports/SimpleList.mrt'))
    viewer.report = report

    return viewer.getFrameworkResponse()
```

More details in [our documentation](https://www.stimulsoft.com/en/documentation/online/programming-manual/index.html?reports_python.htm).


### Reports Designer

The **StiDesigner** component is designed for developing reports in a browser window. The designer's interface is built using HTML5, which allows it to be used on almost any modern platform and different operating systems. JavaScript technology used to build reports allows you to use almost any low-performance server side.

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
    report.loadFile(url_for('static', filename='reports/SimpleList.mrt'))
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
    <title>Editing a Report Template in the Designer</title>

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
    report.loadFile(url_for('static', filename='reports/SimpleList.mrt'))
    designer.report = report

    return designer.getFrameworkResponse()
```

More details in [our documentation](https://www.stimulsoft.com/en/documentation/online/programming-manual/index.html?reports_python.htm).

## Useful links

* [Live Demo](http://demo.stimulsoft.com/#Js)
* [Product Page](https://www.stimulsoft.com/en/products/reports-python)
* [Free Download](https://www.stimulsoft.com/en/downloads)
* [PyPI](https://pypi.org/project/stimulsoft-reports/)
* [Documentation](https://www.stimulsoft.com/en/documentation/online/programming-manual/index.html?reports_python.htm)
* [License](https://www.stimulsoft.com/en/licensing/developers)