# R202 Flask Boilerplate
Flask Project template for R202 lab

### How to use it?
First you need to install cookiecutter
```
$ sudo apt install cookiecutter
```
### Create project
```
cookiecutter https://github.com/r202-coe-psu/r202-flask-boilerplate.git
```
### Setup the project
```
$ cd <project_name>

# create python3 virtual environment
$ python3 -m venv venv

# activate virtual environment
$ source venv/bin/activate

# setup python packages
$ ./scripts/setup

# setup node packages
$ ./scripts/npm install

# complie tailwind CSS
$ ./scripts/npm run tw
```

### Run the project
```
$ ./scripts/run-web
```

#### More Information
- Poetry: https://python-poetry.org/docs/
- Cookiecutter: https://cookiecutter.readthedocs.io/en/1.7.2/
