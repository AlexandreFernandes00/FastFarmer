# FastFarmer v0.1 (Postgres + Frontend)

## Quick start
```bash
pip install -r requirements.txt
python setup.py   # creates tables in your Postgres DB
python run.py     # http://127.0.0.1:8000
```

### Configure DB (optional)
- Default DB URL is set in `app/config.py`.
- Or create a `.env` file (copy `.env.example`) and set `DATABASE_URL`.

## Pages
- Home: http://127.0.0.1:8000/
- Register: http://127.0.0.1:8000/register
- API docs: http://127.0.0.1:8000/docs

## API
- `POST /api/v1/users/` — create a user
- `GET /api/v1/users/` — list users
