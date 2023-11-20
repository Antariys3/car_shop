1. Install deps:

```
pip install -r requirements.txt
```
2. Run docker postgres.

```
docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
```

3. Make migrations.

```
python manage.py migrate
```

4. Set you SENDGRID_API_KEY and DEFAULT_FROM_EMAIL environment variables.

```
export SENDGRID_API_KEY='foo'
export DEFAULT_FROM_EMAIL='foo'
```

5. Run Django web server.

```
python manage.py runserver
```

