# ProSEIT Innovation-to-Implementation Agent

A Streamlit web application that converts innovation ideas into complete,
implementation-ready product packages using the ProSEIT 19-stage pipeline
powered by Claude AI.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Configuration

Set your `ANTHROPIC_API_KEY` in `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

Or enter it directly in the app sidebar.

## Deployment

Deploy on [Streamlit Community Cloud](https://streamlit.io/cloud) — connect the repo,
set `ANTHROPIC_API_KEY` as a secret, and point to `app.py`.

## About ProSEIT

ProSEIT (Professional Society for Engineering, Innovation & Technology) is a
Pan-African professional body headquartered in Uganda.
