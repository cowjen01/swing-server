# Swing Server
Swing Server is an open-source Swing Chart repository server written in Python language.

## Functional Requirements
- List all uploaded charts.
- Get the detail and releases of the chart.
- Download a specific version of the chart.
- Upload a new version of the chart.
- Retrieve server status information.

## Nonfunctional Requirements
- Charts should be stored in the server filesystem.
- The server can be configurable using environment variables.
- Editing of charts has to be secured by user authentication.
- New chart storage should be easily implementable.

## Documentation
- https://flask-login.readthedocs.io/en/latest/
- https://flask-session.readthedocs.io/en/latest/
- https://flask-sqlalchemy.palletsprojects.com/en/2.x/
- https://medium.com/dev-bits/ultimate-guide-for-working-with-i-o-streams-and-zip-archives-in-python-3-6f3cf96dca50
- https://stackoverflow.com/questions/9419162/download-returned-zip-file-from-url