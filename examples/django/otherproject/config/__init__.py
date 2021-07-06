config = {
    "postgres_datadir": "/tmp/pg_datadir",
    "postgres_dbname": "test",
    "postgres_log": "/tmp/postgres.log",
    "postgres_password": "test",
    "postgres_port": 5432,
    "postgres_postmaster_log": "/tmp/postmastre.log",
    "postgres_username": "test",

    "gunicorn_access_log": "/tmp/gunicorn-access.log",
    "gunicorn_log": "/tmp/gunicorn.log",
    "gunicorn_pid": "/tmp/gunicorn.pid",
    "gunicorn_socket": "/tmp/gunicorn.sock",
    "gunicorn_workers": 5,

    "django_static_root": "/tmp/otherproject/static",
    "django_static_url": "/static/",

    "nginx_access_log": "/tmp/nginx_access.log",
    "nginx_temp_path": "/tmp/nginx",
    "nginx_error_log": "/tmp/nginx_error.log",
    "nginx_pid": "/tmp/nginx.pid",
    "nginx_port": 8000,
}
