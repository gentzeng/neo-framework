# Installation

## Preliminaries

In order to use the Newsfeed Exposure Framework (NEO), first install [pyenv](https://github.com/pyenv/pyenv) for python version management and [poetry](https://python-poetry.org/) for dependency management. We furthermore recommend to use [nvm](https://github.com/nvm-sh/nvm) for Node.js version management. We also use [yarn](https://yarnpkg.com/) for Node.js dependency management.

Clone the repository:

```
git clone --depth 1 https://github.com/gentzeng/neo-framework.git
```

## Building the NEO Framework

Both parts of the framework. i.e., front- and backend are served by the underlying django components.

### Frontend

First install at least node version v16.6.1 (via nvm) and activate it:

```
nvm install v16.6.1
nvm use v16.6.1
```

Install all packages.

```
yarn install
```

Finally, build the frontend with:

```
npx gulp build
```

or

```
yarn run build
```

### Backend

Set the local python version and install all dependencies:

```
pyenv local 3.8.10
poetry install
mkdir output
mkdir log
```

After that, you should be able to run backend. Checkout django for more information on manage.py

## Running the Neo Framework

(First, build front- and backend.)

Active the development settings

```
cd neof_backend_root
export DJANGO_SETTINGS_MODULE=neof_backend.settings.development
```

In order to run the framework, start the django server in the respective directory of manage.py

```
poetry run python manage.py runserver
```

After running the framework, the researcher frontend is accessible via the link

```
http://127.0.0.1:8000/dashboard/
```

Login with username="testuser1" and password="testuser1!"

To view a test newsfeed preview click "Test newsfeed" in navbar or visit

```
http://127.0.0.1:8000/newsfeed/1/fb/
```
