# Simple Report Engine

## Overview

Simple Report Engine is a FastAPI-based service for generating PDF reports from templates. It supports loading templates from both folders and zip files, rendering them with Jinja2, and generating PDFs using WeasyPrint.

## Features

- Load templates from folders or zip files
- Render templates with Jinja2
- Generate PDFs with WeasyPrint
- Queue-based report generation
- Retrieve generated reports
- Monitor queue status

## Installation

1. Clone the repository:

```sh
git clone https://github.com/yourusername/simple-report-engine.git
cd simple-report-engine
```

2. Create a virtual environment and activate it:

```sh
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the dependencies:

```sh
pip install -r requirements.txt
```

## Configuration

Ensure the following directories and files are correctly set up:

- `TEMPLATE_DIR`: Directory containing the templates
- `OPTIONS_PATH`: Path to the JSON file with PDF options
- `FONT_DIR`: Directory containing font files
- `TRAYS_DIR`: Directory where generated PDFs will be saved

## Usage

1. Start the FastAPI server:

```sh
uvicorn main:app --reload
```

2. Use the following endpoints to interact with the API:

### Endpoints

#### Queue a Report

- **URL**: `/queue/`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "content": {
      "key": "value"
    },
    "template": "template_name"
  }
  ```
- **Response**:
  ```json
  {
    "request_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV"
  }
  ```

#### Retrieve a Report

- **URL**: `/retrieve/{request_id}`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "status": "success",
    "result": "base64_encoded_pdf_content"
  }
  ```

#### Check Queue Status

- **URL**: `/status/`
- **Method**: `GET`
- **Response**:
  ```json
  {
    "queue_count": 0,
    "worker_count": 1
  }
  ```

## Example

### Queue a Report

```sh
curl -X POST "http://127.0.0.1:8000/queue/" -H "Content-Type: application/json" -d '{"content": {"name": "John Doe"}, "template": "example_template"}'
```

### Retrieve a Report

```sh
curl -X GET "http://127.0.0.1:8000/retrieve/01ARZ3NDEKTSV4RRFFQ69G5FAV"
```

### Check Queue Status

```sh
curl -X GET "http://127.0.0.1:8000/status/"
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or inquiries, please contact [andyut101@protonmail.com](mailto:andyut101@protonmail.com).
