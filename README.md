# ClickUp Python Library

A Python library for the ClickUp API

## Install
```python
pip install clickup
```

## Basic Usage

```python
from clickup import Client
click_client = Client(EMAIL, PASS, PERSONAL_API_KEY)
for team_id, team_name in click_client.teams.items():
    print(team_id, team_name)
```