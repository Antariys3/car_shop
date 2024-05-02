run:
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements.txt
	docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres
	export AWS_STORAGE_BUCKET_NAME="foo"
	export AWS_S3_ACCESS_KEY_ID="foo"
	export AWS_S3_SECRET_ACCESS_KEY="foo"
	export SENDGRID_API_KEY='foo'
	export DEFAULT_FROM_EMAIL='foo'
	export GOOGLE_CLIENT_ID='foo'
	export GOOGLE_CLIENT_SECRET='foo'
	MONOBANK_TOKEN='foo'
	python manage.py migrate
	python manage.py generate_cars
	python manage.py runserver