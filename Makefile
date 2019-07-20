django:
	python manage.py runserver

redis:
	redis-server

celery:
	celery worker --app=core.celery -l info

shell:
	python manage.py shell

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

superuser:
	python manage.py createsuperuser

e:
	source env/bin/activate

h-celery:
	heroku logs -t -p worker

h-logs:
	heroku logs --tail

h-deploy:
	git push heroku master

h-shell:
	heroku run bash

h-migrations:
	heroku run python manage.py makemigrations

h-migrate:
	heroku run python manage.py migrate

h-superuser:
	heroku run python manage.py createsuperuser