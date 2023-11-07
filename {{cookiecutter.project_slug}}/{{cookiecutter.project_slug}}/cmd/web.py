from {{ cookiecutter.project_slug }} import web


def main():
    app = web.create_app()
    app.run()
