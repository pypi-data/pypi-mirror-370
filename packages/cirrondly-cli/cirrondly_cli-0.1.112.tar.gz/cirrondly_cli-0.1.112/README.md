## Usage Instructions

Users can easily install and use the Cirrondly CLI with these simple steps:
Install the package:

```bash
pip install cirrondly-cli
```

1. Initialize in their application (main.py, app.py, or Django's manage.py):

```python
from cirrondly import Cirrondly
cirrondly(api_key="your-api-key-here")
```

2. For web frameworks, add the appropriate middleware:
For Flask:

```python
from cirrondly import Cirrondly
from cirrondly_cli import cirrondly, flask_middleware

app = Flask(__name__)
cirrondly(api_key="your-api-key-here")
flask_middleware(app)
```

for FastAPI:

```python
from cirrondly import Cirrondly
from cirrondly_cli import cirrondly, CirrondlyFastAPIMiddleware

app = FastAPI()
cirrondly(api_key="your-api-key-here")
app.add_middleware(CirrondlyFastAPIMiddleware)
```
for Django:
Django: Add to your settings.py:

```python
MIDDLEWARE = [
    # ... other middleware
    'cirrondly_cli.CirrondlyDjangoMiddleware',
    # ... other middleware
]
```


