# Dentrix Service

Service for handling Dentrix processes.
Contains methods that integrate operations inside the Dentrix platform with any automations that require it.
It does this by utilizing API requests and UI operations automated by Selenium.

## Main Objects
- DentrixServiceRequests: Contains logic for requests of endpoints taken from the Dentrix website.
- AscendRequests: Contains logic that makes requests to the endpoints of the official Ascend API (Not yet available).
- DentrixService: Contains easy to use logic that receives, processes and returns information from the Dentrix website, and it's endpoints, in a more pythonic way (models and exceptions instead of jsons and status codes).

## Usage
```python
from t_dentrix_service import DentrixService

ds = DentrixService("username": "foobar", "password": "12345")
ds.login_to_dentrix()
# you can now execute any operation you'd like
```