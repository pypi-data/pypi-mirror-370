<p align="center">
  <img src="https://i.ibb.co/M5Pv76X0/slushlogo.png" alt="Slush Logo" width="480" />
</p>

# Slush

**Slush** is a lightweight Python web framework designed for clarity, extensibility, and performance.

---

## 🚀 Introduction

**Slush** is a lightweight and efficient Python web framework designed for building modern APIs with speed and simplicity.

Slush gives you full control over routing, requests, responses, middleware, and cookies—without locking you into a rigid structure or heavy dependencies.

Whether you're building microservices, internal tools, or full-fledged backend systems, Slush helps you move fast with clean, readable code and a powerful core that just works.

Perfect for:

- Rapid API development without boilerplate.
- Minimalist backend systems with full control.
- Developers who want a lean, customizable foundation.

---

## 📦 Installation

```bash
$ pip install slush
```


## A Simple Example

```python
# save this as main.py
from slush.app import Slush
from slush.core.response import Response

app = Slush()

@app.route("/hello", methods=["GET"])
def hello(request):
    return {"message": "Hello from Slush!"}
```

```python
# save this as run.py
from main import app
from slush.server import run

run(app, port=8000, debug=True)
```

## ▶️ Run the Server
### ✅ Using built-in CLI command
```bash
$ python3 run.py
```

### ✅ Using built-in CLI
```bash
$ slush runserver main:app
```
> Set `DEBUG=TRUE` for

### ✅ Or use gunicorn
```bash
$ gunicorn main:app
```

## 📄 License
This project is licensed under the BSD 3-Clause License.

## 🌐 Links

### 📘 Documentation: Coming soon
### 🐙 GitHub: https://github.com/farazkhanfk7/slush
### 📦 PyPI: https://pypi.org/project/slush
