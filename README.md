# FastAPI Project

A simple FastAPI application for managing items with basic CRUD operations.

## Features

- REST API with FastAPI
- CRUD endpoints for items management
- Root endpoint that returns a greeting message

## Endpoints

- `GET /` - Returns a greeting message
- `GET /items` - Retrieve all items
- `POST /items` - Create a new item
- `PUT /items/{item_id}` - Update an item by ID
- `DELETE /items/{item_id}` - Delete an item by ID

## Quick Start

```bash
git clone 
cd fast-api
uv venv
#Mac/Linux
source .venv/bin/activate 
# On Windows: 
source .venv/Scripts/activate
uv pip install -r requirements.txt
uv run fastapi dev main.py
```

Visit `http://127.0.0.1:8000/docs` to interact with the API.

## Installation

### Using pip

1. Create a virtual environment:
```bash
python -m venv venv
# Mac/Linux
source venv/bin/activate 
# On Windows:
source .venv/Scripts/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Using uv (faster)

```bash
uv venv
# Mac/Linux
source .venv/bin/activate  
# On Windows: 
source .venv/Scripts/activate
uv pip install -r requirements.txt
```

## Running the Application

Start the development server:

```bash
fastapi dev main.py
```

Or using uv:

```bash
uv run fastapi dev main.py
```

The server will be available at `http://127.0.0.1:8000`

### Interactive API Documentation

- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Development

This project uses:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
- Python 3.7+

## License

MIT
