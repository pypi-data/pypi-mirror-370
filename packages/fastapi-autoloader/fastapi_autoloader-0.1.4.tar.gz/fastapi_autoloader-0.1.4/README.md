# fastapi-autoloader

A Python package for dynamic routing in FastAPI.

## Features

- Automatically loads and registers routers from your controllers directory.
- Supports multilevel directory structures (HMVC-style modules).
- Minimal configuration required.

## Installation

```sh
pip install fastapi-autoloader
```

## Usage

Suppose your project structure is:

```
example/
	main.py
	controllers/
		users/
			users.py
		orders/
			orders.py
```

Each controller module should define a FastAPI `APIRouter` named `router`:

**example/controllers/users/users.py**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
def list_users():
	return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
```

**example/controllers/orders/orders.py**
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/orders")
def list_orders():
	return [{"id": 1, "item": "Book"}, {"id": 2, "item": "Pen"}]
```

**example/main.py**
```python
from fastapi import FastAPI
from fastapi_dynamic_router import DynamicRouter

app = FastAPI()

# Automatically loads all routers from controllers/ and subdirectories
controllers = DynamicRouter("controllers")
controllers.load(app)

@app.get("/")
def root():
	return {"message": "Hello"}
```

## Running

Start your app with Uvicorn:

```sh
uvicorn example.main:app --reload
```

## How it works

- The package recursively scans the target directory (`controllers/` by default).
- For each `.py` file (excluding `__init__.py`), it imports the module and looks for a variable named `router` of type `APIRouter`.
- All found routers are automatically registered with your FastAPI app.
