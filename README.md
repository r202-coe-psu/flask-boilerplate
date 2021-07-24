# R202 Flask Boilerplate
Flask Project template for R202 lab

### How to use it?
First you need to install cookiecutter and poetry
```
$ sudo apt install cookiecutter
$ pip install --user poetry
```
Go to the directory where you want to create the project then create the virtual environment
```
cd my-awesome-flask-project
python3 -m venv env
source ./env/bin/activate
```
Use flask-boilerplate and install python dependencies packages:
```
cookiecutter https://github.com/r202-coe-psu/r202-flask-boilerplate.git
cd <project name>
poetry install
```
Run the project
```
./scripts/run-web
```

#### More Information
- Poetry: https://python-poetry.org/docs/
- Cookiecutter: https://cookiecutter.readthedocs.io/en/1.7.2/
