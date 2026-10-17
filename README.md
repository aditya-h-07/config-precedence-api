# 12-Factor Config Precedence API

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Open `http://127.0.0.1:8000/effective-config`.

Test query overrides:

```bash
curl 'http://127.0.0.1:8000/effective-config?set=port=9000&set=debug=true'
```

## Render

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Optional environment variables: `APP_ENV=development`, `APP_DEBUG=false`,
  `APP_API_KEY=key-jp5pyc1ifw`

The API masks `api_key` in all responses.
