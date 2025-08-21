# GCP Notifier

A simple notification library for Google Cloud projects. Send alerts via Email and Google Chat with a single function call. Designed to be imported and used as a Python module in your own code.

## Features

- Send notifications via Email and Google Chat (Webhook)
- Unified, simple Python API: `notify(subject, body, channels)`
- Tenacity-compatible error callback: `notify_on_failure`
- Secrets are securely loaded from Google Secret Manager

## Installation

Install from PyPI (recommended):

```sh
pip install gcp-notifier
```

Or, to test the latest version from TestPyPI:

```sh
pip install -i https://test.pypi.org/simple/ gcp-notifier
```

Or, for local development:

```sh
pip install .
```

Or add to your requirements.txt (recommended for PyPI):

```text
gcp-notifier
```

For development versions from GitHub (not recommended for production):

```text
gcp_notifier @ git+https://github.com/marcellusmontilla/gcp_notifier.git
```

## Quick Start

1. Install the package (see Installation above).

2. The account (personal or service) running this code must have the 'Secret Manager Secret Accessor' role in your GCP project.

3. The required secrets must be in the same GCP project where your Python script or notebook is running.

4. Add your required secrets to Google Secret Manager in your GCP project:

   - `GCHAT_WEBHOOK_URL` (for Google Chat)
   - `EMAIL_SENDER` (sender email address for Email)
   - `EMAIL_PASSWORD` (password or app password for sender)
   - `EMAIL_RECIPIENTS` (comma-separated list of recipient email addresses)

5. Import and use `notify` in your code as shown below.

## Usage

Import and use in your Python code:

```python
from gcp_notifier import notify, notify_on_failure

# Send a notification (choose channels: "email", "gchat", or both)
notify(
  subject="Alert Subject",
  body="Alert body text",
  channels=["email", "gchat"]  # or ["email"] or ["gchat"]
)

# Use as tenacity retry_error_callback
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(3), retry_error_callback=notify_on_failure)
def always_fails():
  # This function will always fail, triggering notify_on_failure after retries
  raise ValueError("This is a test error for notification.")

always_fails()
```

## Building and Publishing

This project uses a modern Python packaging workflow with `pyproject.toml`.

To build the package:

```sh
python -m pip install --upgrade build
python -m build
```

To check and upload to PyPI:

```sh
python -m pip install --upgrade twine
twine check dist/*
twine upload dist/*
```

See [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/) for more details.

## License

MIT
