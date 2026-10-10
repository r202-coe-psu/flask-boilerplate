from app_name import worker


def main():
    server = worker.create_server()
    server.run()
