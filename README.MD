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

4. Set the environment variables (needed to send emails)
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

6. Set environment variables (needed to pay for goods)
```
MONOBANK_TOKEN='foo'
```
7. Make migrations.
```
python manage.py migrate
```
8. Add cars to the database (12 cars).
```
python manage.py generate_cars
```

9. Run Django web server.
```
python manage.py runserver
```
