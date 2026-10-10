from ..web import create_app, get_program_options


def main():
    app = create_app()
    options = get_program_options()

    if options.profile:
        from werkzeug.middleware.profiler import ProfilerMiddleware

        app.config["PROFILE"] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
        options.debug = True

    app.run(host=options.host, port=int(options.port), debug=options.debug)
