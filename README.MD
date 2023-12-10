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

4. Set the environment variables (needed for registration and login)
SENDGRID_API_KEY and DEFAULT_FROM_EMAIL.

```
export SENDGRID_API_KEY='foo'
export DEFAULT_FROM_EMAIL='foo'
```

5. Set the environment variables (needed for registration and login via Google)
GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.

```
export GOOGLE_CLIENT_ID='foo'
export GOOGLE_CLIENT_SECRET='foo'
```

6. Run Django web server.

```
python manage.py runserver
```

