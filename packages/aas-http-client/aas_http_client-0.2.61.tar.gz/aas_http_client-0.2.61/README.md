<!-- TODO: Go through the readme and enter the information here -->

# AAS HTTP Client

<div align="center">
<!-- change this to your projects logo if you have on.
  If you don't have one it might be worth trying chatgpt dall-e to create one for you...
 -->
<img src="docs/assets/fluid_logo.svg" alt="aas_http_client" width=500 />
</div>

---

[![License: em](https://img.shields.io/badge/license-emSL-%23f8a602?label=License&labelColor=%23992b2e)](LICENSE)
[![CI](https://github.com/fluid40/aas-http-client/actions/workflows/CI.yml/badge.svg?branch=main&cache-bust=1)](https://github.com/fluid40/aas-http-client/actions)
[![PyPI version](https://img.shields.io/pypi/v/aas-http-client.svg)](https://pypi.org/project/aas-http-client/)

This is a generic HTTP client that can communicate with various types of AAS and submodel repository servers. It uses Python dictionaries for input and output parameters of functions. It supports the most common endpoints for the [specified AAS server endpoint](https://industrialdigitaltwin.io/aas-specifications/IDTA-01002/v3.1.1/specification/interfaces.html). The client is compatible with various types of AAS repository server.
The client should be compatible with various types of AAS repository server. 

Tested servers include:
- [Eclipse BaSyx .Net SDK server](https://github.com/eclipse-basyx/basyx-dotnet)
- [Eclipse BaSyx .Net SDK server (Fluid4.0 Fork)](https://github.com/fluid40/basyx-dotnet)
- [Eclipse BaSyx Java SDK server](https://github.com/eclipse-basyx/basyx-java-sdk)
- [Eclipse BaSyx Python SDK server](https://github.com/eclipse-basyx/basyx-python-sdk)
- [Eclipse AASX server](https://github.com/eclipse-aaspe)  

The behavior may vary depending on the details of the implementation and compliance with the [AAS specification](https://industrialdigitaltwin.org/en/content-hub/aasspecifications). It also depends on which endpoints are provided by the server.

Additionally, wrappers are provided that work with various AAS frameworks and use the HTTP client as middleware. These wrappers use the SDK-specific data model classes for function input and output parameters.
Wrappers are currently available for the following frameworks:
- [Eclipse BaSyx Python SDK](https://github.com/eclipse-basyx/basyx-python-sdk)

## Links

🚀 [Getting Started](docs/getting_started.md)

💻 [Tutorials](docs/tutorials.md)

👨‍⚕️ [Troubleshooting](docs/troubleshooting.md)

🤖 [Releases](http://github.com/fluid40/aas-http-client/releases)

📝 [Changelog](CHANGELOG.md)

📦 [Pypi Packages](https://pypi.org/project/aas-http-client/)

📜 [em AG Software License](LICENSE)

## ⚡ Quickstart

For a detailed introduction, please read [Getting Started](docs/getting_started.md).

```bash
pip install aas-http-client
````

### Client

```python
from aas_http_client import create_client_by_url

client = create_client_by_url(
    base_url="http://myaasserver:5043/"
)

print(client.get_shells())
```

### BaSyx Python SDK Wrapper

```python
from aas_http_client.wrapper.sdk_wrapper import create_wrapper_by_url

wrapper = create_wrapper_by_url(
    base_url="http://myaasserver:5043/"
)

print(wrapper.get_shells())
```