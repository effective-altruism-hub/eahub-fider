## Restore data from a fider json backup

- unzip the backup.zip to root of the project in `backup/` directory
- start db docker container, make sure that your `/etc/hosts` points `postgres` to `127.0.0.1`
- create a python3.6+ venv
- `pip install divio-cli psycopg2-binary python-magic-bin`
- `python fider-import.py`
- `cp .aldryn-example .aldryn`
- replace the Dockerfile content with the following content and deploy the server
    ```dockerfile
    FROM divio/base:1.0-py3.9-slim-buster
    RUN apt update
    RUN apt install --yes nginx
    CMD ["nginx", "-g", "daemon off;"]
    ```
- `pg_dump --no-owner --no-privileges "postgres://postgres@postgres:5432/db?sslmode=disable" > local_db.sql`
- `divio project pull db live`
- restore the old content of your Dockerfile
