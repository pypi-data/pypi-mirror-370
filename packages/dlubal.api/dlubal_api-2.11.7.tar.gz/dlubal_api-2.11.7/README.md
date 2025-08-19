# Dlubal API

![PyPI](https://img.shields.io/pypi/v/dlubal.api)
![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![License](https://img.shields.io/badge/License-Proprietary-red)

## Compatibility

This package version is fully compatible with the following **Dlubal App version**:

✅ **X.11.0007.169.7854af2be4f**

## Overview
The `dlubal.api` package is the next-generation Python client library for interacting with Dlubal Software APIs, leveraging modern **gRPC technology** to deliver high-speed communication, scalability, and improved performance. This API enables **seamless automation** and **remote access** to Dlubal software **RFEM 6** and **RSTAB 9**, with plans for near-future support for additional products in the Dlubal portfolio.

---

## Installation

Ensure you have **Python 3.10+** installed. Then, install the package via **pip**:

```sh
pip install dlubal.api
```

For additional installation options, refer to the **official documentation**.

---

## Quick Start

### Authentication & Authorization
To use the API, you need:
- **API Key**: Obtainable via your **Extranet | API & Cloud** dashboard.
- **API Subscription**: [Dlubal API Subscriptions](https://www.dlubal.com/en/webshop/online-service)

---

### Example Usage
```python
from dlubal.api import rfem

with rfem.Application(api_key="your_api_key") as rfem_app:
    # Example API call
    rfem_app.create_model("MyModel")
    rfem_app.create_object(
        rfem.structure_core.Node(coordinate_1=2)
    )
```

## Documentation & Support
- 📖 **API Documentation**: [API Docs](https://www.dlubal.com/en/solutions/dlubal-api/api-documentation/index)
- 💬 **Support**: Contact [Dlubal Support](https://www.dlubal.com/en/support-and-learning)
- 🔑 **Extranet**: [API & Cloud Dashboard](https://www.dlubal.com/en/extranet/my-account)

---

## License
This package is proprietary software and requires an **active API Service subscription**. Unauthorized use is prohibited.

