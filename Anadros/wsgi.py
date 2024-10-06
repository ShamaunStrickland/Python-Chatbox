from gevent import monkey

monkey.patch_all()

from apps import app as application

if __name__ == "__main__":
    application.run()
