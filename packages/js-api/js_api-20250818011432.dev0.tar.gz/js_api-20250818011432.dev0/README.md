# API
This is a custom API, written in Python using FastAPI, to help me accomplish tasks the can be improved through a RESTful API

## Setup
Simplest setup is to start from [compose.yml](https://github.com/jnstockley/api/blob/dev/compose.yml) and [template.env](https://github.com/jnstockley/api/blob/dev/template.env), which should be renamed to `.env`

### Environment Vairables
- `API_KEY` - Any long, random string. Keep this secret as this is the only form of authentication for the API. All routes require it, except `/health-check/`
- `DATABASE_URL` - The URL to connect to postgres DB. Must start with `postgresql+psycopg://`. Should be in the format specifiec in [template.env](https://github.com/jnstockley/api/blob/dev/template.env)
- `TZ` - Timezone of the container
- `PGTZ` - Timezone the Postgres container should use

## How to Access
Using the [compose.yml](https://github.com/jnstockley/api/blob/dev/compose.yml) file, you can access the API at `http://<IP>:5000/health-check`. If everything is setup correctly, you should see `{"status":"ok"}`
