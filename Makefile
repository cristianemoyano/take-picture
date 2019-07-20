django:
	python manage.py runserver

redis:
	redis-server

celery:
	celery worker --app=core.celery -l info

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