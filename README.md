# Swing Server
Swing Server is an open-source Swing Chart repository written in Python language.

## Installation

The application can be installed from the PyPI repository using the next command.

```shell
pip install swing-server
```

## Requirements

To run the application, you have to provide a connection to the PostgreSQL database
and some folder, where uploaded archives will be stored. You also need to install
the Flask framework from the PyPI repository.

```shell
pip install flask
```

## Configuration

You can configure the application using environment variables.

* `SECRET_KEY` Secret token for storing of the user's session. (required)
* `DATABASE_URI` PostgreSQL database URI. (required)
* `PUBLIC_URL` Public address where the application will be accessible. (default: http://localhost:5000)
* `STORAGE_TYPE` There is currently only single type of the storage. (default: local)
* `STORAGE_LOCAL_DIR` Directory where uploaded charts will be stored. (required)
* `INIT_USER_EMAIL` E-mail of the initial user that will be created after server start-up. (default: none)
* `INIT_USER_PASSWORD` Password of the initial user. (required)

## Server Startup

The application can be started as a Flask server using the next command.

```shell
FLASK_APP=swing_server flask run
```

## Server API

* GET `/status` Return current server status, and a number of created charts.
* GET `/chart?query=<keyword>` Return list of all charts. If the query is specified, then filter charts by their name or description.
* GET `/release?chart=<chart_name>` Return list of all releases for the specific chart. Releases are ordered by the version.
* GET `/release/<chart_name>-<version>.zip` Download specific release of the chart. The filename can be for example `redis-1.0.0.zip`.
* POST `/release` Upload a new release of the chart. If the chart does not exist, then a new one is created. The archive has to be sent as a multipart form under the `chart` key with the `Content-Type` header set to `multipart/form-data`.
* DELETE `/chart/<chart_name>?version=<version>` Remove chart both from the database and from local storage. If the version is specified, then remove only the specific release.
* POST `/login` Login user using encoded credentials sent in the `Authorization` header of the request. It is used the `Basic` type of authorization in this format `<username>:<password>`.
* POST `/logout` Log out currently logged user.

## Project Requirements

### Functional Requirements
- List all uploaded charts.
- Get the detail and releases of the chart.
- Download a specific version of the chart.
- Upload a new version of the chart.
- Retrieve server status information.

### Nonfunctional Requirements
- Charts should be stored in the server filesystem.
- The server can be configurable using environment variables.
- Editing of charts has to be secured by user authentication.
- New chart storage should be easily implementable.
