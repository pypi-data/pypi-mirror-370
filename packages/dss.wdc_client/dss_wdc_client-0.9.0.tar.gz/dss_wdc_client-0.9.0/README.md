# Description
This project includes a *very* small client to access data form 
the WebDataCollector-API. It is meant to provide a simple means 
of accessing the data in Json or as Panda-DataFrames.

# Usage

```
from dss_wdc_client.client import WDCClient

# Somehow initialize environment variables for 
# "WDC_HOST" and "WDC_TOKEN". 
load_dotenv()

client = WDCClient.fromEnv()
df = client.loadAsDataFrame(
	'api/endpoint...', {'param1', 'value will be encoded'})
```

For more information about the client and usable endpoints, 
see the project homepage of WDC or directly consult the Documentation.

# Changelog
- 0.9.0		Add method WDCClient#put to create PUT-Requests
- 0.8.2		Fix for duplicate parameters when paging.
- 0.8.1		Simplify new methods for loading a DomainGraph.
- 0.8.0		Added new methods for loading DomainGraphs.
- 0.7.3		Fix README
- 0.7.2		Include link for generated documentation
- 0.7.1 	Added generated documentation
- 0.7.0		Added new method WDCClient.loadDomainGraph for loading a DomainGraph as NetworkX-Object
- 0.6.0		WDCClient throws an WDCException if a request to the server fails
- 0.5.0		New signatures and methods taking care of encodings and working on large results
- 0.4.3		Add dependencies pandas["excel, plot"] as they are likely to be used.
- 0.4.2		Enhance README with Changelog and code-example.
- 0.4.1		Include a preferred variant for creating WDCClients from the Environment	

# Internal Notes for the Development Environment

## Initialize

	wdc-rest-api-python> poetry install --extras docs

## Use cases

* Update dependencies: `poetry update`
	 
* Execute Python file: `poetry run python3 src/main.py`
	
* Running tests 
(https://pytest-with-eric.com/getting-started/poetry-run-pytest/)
	
	```
	poetry run pytest 
	poetry run pytest tests/test_module.py::testFunction
	poetry run pytest -s (with output from stdout and stderr)
	```
	
## Create Documentation (Sphinx)

	`poetry run make html` 	
	
## Publish to PyPI
(https://python-poetry.org/docs/repositories/#publishable-repositories)
	
1. Config token (once)
	
	`poetry config pypi-token.pypi <my-token>`

2. Publish

	`poetry publish --build`
