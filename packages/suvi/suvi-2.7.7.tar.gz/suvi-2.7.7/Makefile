build:
	pip install build
	python -m build


pull_dependencies:
	- mkdir -p suvi/static/dependencies
	curl -o suvi/static/dependencies/bootstrap.min.css https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css
	curl -o suvi/static/dependencies/bootstrap.bundle.min.js https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js
	curl -o suvi/static/dependencies/htmx.min.js https://unpkg.com/htmx.org@1.9.12/dist/htmx.min.js
	curl -o suvi/static/dependencies/jquery.min.js https://code.jquery.com/jquery-3.7.1.min.js
	