import os

from app.tasks import run_syslog_server
from flask import Blueprint
from multiprocessing import Process
commands_blueprints = Blueprint("commands", __name__, cli_group=None)


@commands_blueprints.cli.command()
def make_test():
    """
    Run basic tests
    """
    pass


@commands_blueprints.cli.command()
def install_git_hooks():
    """
    Initialize git prehooks
    """
    print("Installing Pre hooks")
    os.system("pre-commit install")
    print("Pre hooks installed")


@commands_blueprints.cli.command()
def start_celery_worker():
    """
    CLI to start celery worker
    """
    # Purge all tasks
    os.system("celery -A app.celery purge -f")
    worker = Process(target=os.system, args=("celery -A app.celery worker --loglevel=info --pool=solo -n wkr", ))
    try:
        worker.start()
    except (KeyboardInterrupt, SystemExit):
        worker.terminate()


@commands_blueprints.cli.command()
def start_syslog_server():
    run_syslog_server()

