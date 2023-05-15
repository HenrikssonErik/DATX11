# Installation guide

## [Windows](#getting-started-guide-on-windows)

## [Linux (Ubuntu)](#getting-started-guide-on-linux-ubuntu)

# Getting Started Guide On Linux (Ubuntu)
## Requirements
- [Go](https://go.dev/)
- [Nodejs](https://nodejs.org/en/)
  - Npm
- [Python 3](https://www.python.org/downloads/)
  - python3-venv

## 1. Installing Nodejs dependencies
```bash
npm install -g @angular/cli
cd DATX11/client
npm install
```

## 2. Installing Python 3 dependencies
```batch
VENV=YOUR/VENV/PATH
python3 -m venv $VENV
source $VENV/bin/activate
cd DATX11/server
pip install -r requirements.txt
deactivate
```

## 3. Copy credential files
Two files will need to be placed in `DATX11/server/src/`.
* `connection_config.txt`
* `mailconfig.cfg`

File one is for the database credentials and the second file is for the mail credentials.

## 3. Start The Servers
This step is needed to be done to start the servers each time. The variable `$VENV` will not exist if a new instance is used.
```bash
(source ../$VENV"/bin/activate" && export FLASK_APP="server/src/app.py" && flask run --host 0.0.0.0) & (cd client && ng serve)
```

## 4. Open website
- Frontend: [127.0.0.1:4200](http://127.0.0.1:4200)
- Backend:  [127.0.0.1:5000](http://127.0.0.1:5000)



# Getting Started Guide On Windows
## Requirements
- [Go](https://go.dev/)
- [Nodejs](https://nodejs.org/en/)
- [Python 3](https://www.python.org/downloads/)

## 1. Installing Nodejs dependencies
```batch
npm install -g @angular/cli
cd DATX11/client
npm install
```

## 2. Installing Python 3 dependencies
```batch
set VENV=YOUR\VENV\PATH
py -m venv %VENV%
%VENV%\Scripts\activate.bat
cd DATX11/server
pip install -r requirements.txt
deactivate
```

## 3. Copy credential files
Two files will need to be placed in `DATX11\server\src\`.
* `connection_config.txt`
* `mailconfig.cfg`

File one is for the database credentials and the second file is for the mail credentials.

## 3. Start The Servers
This step is needed to be done to start the servers each time. The variable `%VENV%` will not exist if a new instance is used.
```batch
start cmd /c "%VENV%\Scripts\activate.bat && set FLASK_APP=server\src\app.py && flask run --host 0.0.0.0"
start cmd /c "cd client && ng serve"
```

## 4. Open website
- Frontend: [127.0.0.1:4200](http://127.0.0.1:4200)
- Backend:  [127.0.0.1:5000](http://127.0.0.1:5000)