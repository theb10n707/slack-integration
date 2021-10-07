import os
import json


from dotenv import load_dotenv
load_dotenv()


def load_file(file_name: str) -> dict:
    with open(f"{BaseConfig.BASEDIR}/{file_name}") as file:
        return json.load(file)


class BaseConfig:

    APP_NAME = "slack_integration"
    BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    DEBUG = False

    # Syslog Server
    LOG_FILE = os.path.join(BASEDIR, 'tmp/syslog.log')
    HOST = os.getenv("HOST")
    PORT = int(os.getenv("PORT"))
    LOGGING_LEVEL_FILTER = 2

    # Slack Credentials
    SLACK_VERIFICATION_TOKEN = os.getenv("SLACK_VERIFICATION_TOKEN")
    SLACK_USER_OAUTH_TOKEN = os.getenv("SLACK_USER_OAUTH_TOKEN")
    SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

    # JIRA Credentials
    JIRA_URL = os.getenv("JIRA_URL")
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_PROJECT = os.getenv("JIRA_PROJECT")

    # MongoDB setup
    MONGODB_IP = os.getenv("MONGODB_IP")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT"))
    MONGODB_DB_NAME = APP_NAME
    MONGODB_USER = os.getenv("MONGODB_USER")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")
    MONGODB_HOST = os.getenv("MONGODB_HOST")

    # Celery
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND")

    # Flask Config
    FLASK_PORT = int(os.getenv("FLASK_PORT"))
    FLASK_IP_ADDRESS = os.getenv("FLASK_IP_ADDRESS")

