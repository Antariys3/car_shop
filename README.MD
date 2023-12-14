1. Install deps:

```
pip install -r requirements.txt
```
2. Run docker postgres.

```
docker run -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
```

3. Set environment variables for working with the database AWS Amazon,
AWS_STORAGE_BUCKET_NAME, AWS_S3_ACCESS_KEY_ID and AWS_S3_SECRET_ACCESS_KEY.

```
export AWS_STORAGE_BUCKET_NAME="foo"
export AWS_S3_ACCESS_KEY_ID="foo"
export AWS_S3_SECRET_ACCESS_KEY="foo"
```

4. Make migrations.

```
python manage.py migrate
```
5. Add clients to the database.

```
python manage.py generate_clients
```

6. Set you SENDGRID_API_KEY and DEFAULT_FROM_EMAIL environment variables.

```
export SENDGRID_API_KEY='foo'
export DEFAULT_FROM_EMAIL='foo'
```

7. Run Django web server.

```
python manage.py runserver
```
8. Add cars to the database. Go to the website page http://127.0.0.1:8000/create_cars/
