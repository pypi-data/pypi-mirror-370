Comet
========

.. image:: https://img.shields.io/pypi/v/comet_ml.svg
    :target: https://pypi.python.org/pypi/comet_ml
    :alt: Latest PyPI version


Documentation
-------------

Full documentation and additional training examples are available on
http://www.comet.com/docs/

Installation
------------

-  Sign up (free) on comet.com and obtain an API key at https://www.comet.com


Getting started: 30 seconds to Comet.ml
---------------------------------------

The core class of Comet.ml is an **Experiment**, a specific run of a
script that generated a result such as training a model on a single set
of hyper parameters. An Experiment will automatically log scripts output (stdout/stderr), code, and command
line arguments on **any** script and for the supported libraries will
also log hyper parameters, metrics and model configuration.

Here is the Experiment object:

.. code:: python

    from comet_ml import Experiment
    experiment = Experiment(api_key="YOUR_API_KEY")

    # Your code.

We all strive to be data driven and yet every day valuable experiments
results are just lost and forgotten. Comet.ml provides a dead simple way
of fixing that. Works with any workflow, any ML task, any machine and
any piece of code.

For a more in-depth tutorial about Comet.ml, you can check out or docs http:/www.comet.com/docs/

License
---------------------------------------

MIT License

Copyright 2024 Comet ML, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
