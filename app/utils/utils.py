import json
import logging
import matplotlib.pyplot as plt
import sys
import uuid

from app.config import BaseConfig
from celery import Celery
from datetime import datetime, timedelta
from flask import Flask
from flask import Request
from jira import JIRA, JIRAError

# Constants
DAYS = {"1 day chart": 1, "1 week chart": 7, "1 month chart": 30}


def generate_chart(mongo_db_data: list, start_time: datetime, end_time: datetime) -> str:
    """
    Generating a chart based on the user input and from mongodb
    :param mongo_db_data:
    :param start_time:
    :param end_time:
    :return:
    """
    # Generating matplotlib chart xaxis and yaxis
    data_from_db = {
        datetime.strptime(f"{d['_id']['day']}-{d['_id']['month']}-{d['_id']['year']}", '%d-%m-%Y').isocalendar(): d["count"] for d in mongo_db_data
    }
    delta = end_time - start_time  # as timedelta
    xaxis = list()
    yaxis = list()
    for i in range(delta.days + 1):
        date = (start_time + timedelta(days=i)).date()
        # Set default value to 0
        count = 0
        # If the database returns a datapoint, subsitute it
        if date.isocalendar() in data_from_db:
            count = data_from_db[date.isocalendar()]

        xaxis.append(date)
        yaxis.append(count)

    # Create the chart
    fig, ax = plt.subplots()
    ax.bar(xaxis, yaxis)
    ax.xaxis_date()
    fig.autofmt_xdate()
    plt.xlabel("Day")
    plt.ylabel("# of Error Syslogs")

    # Save chart to a file
    temp_filename = f"tmp/{uuid.uuid4()}-chart.png"
    plt.savefig(temp_filename)

    return temp_filename


def generate_200_ok():
    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


def generate_mkdn_message(message: dict, format: str):
    if format == "JIRA":
        error_message = f"{{code:bash}} {message['syslog']} {{code}}"
    elif format == "SLACK":
        error_message = f"```{message['syslog']}```"
    else:
        raise Exception("Please select format as JIRA or SLACK")
    return f"*Device* - {message['src_ip']}\n" \
           f"*Time* - {message['time']} UTC\n" \
           f"*Error Log* - {error_message}\n"


def unmarshall_slack_api_request(api_request: Request) -> dict:
    return json.loads(api_request.form["payload"])


def create_jira_issue(message: dict) -> str:
    """
    Create jira ticket with metadata
    :param message:
    :return:
    """
    jira = JIRA(
        server=BaseConfig.JIRA_URL,
        basic_auth=(BaseConfig.JIRA_EMAIL, BaseConfig.JIRA_API_TOKEN)
    )
    issue_dict = {
        "project": {"id": BaseConfig.JIRA_PROJECT},
        "summary": f"P1 - Error message from {message['src_ip']}",
        "description": generate_mkdn_message(message=message, format="JIRA"),
        "issuetype": {'name': 'Bug'},
        "labels": ["OPS", "NETWORK"],
        "priority": {
                 "name": "Highest",
                 "id": "1",
                 "iconUrl": "https://slack-integration.atlassian.net/images/icons/priorities/highest.svg"
             },
        "environment": "Backbone Network"
    }
    try:
        response = jira.create_issue(fields=issue_dict)
        return f"{BaseConfig.JIRA_URL}/browse/{response.key}"
    except JIRAError as e:
        logging.error(f"Error creating jira issue: {e}")


def configure_logging(app: Flask) -> None:
    """
    Let the logging handler
    :param app:
    :return:
    """
    if app.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logger = logging.getLogger(__name__)
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    # Set the level
    logger.setLevel(level)
    # Print debug logs to stdout
    handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(handler)


def make_celery() -> Celery:
    """
    Celery app factory
    :return:
    """
    return Celery(
        BaseConfig.APP_NAME,
        backend=BaseConfig.CELERY_RESULT_BACKEND,
        broker=BaseConfig.CELERY_BROKER_URL,
        include=["app.tasks"]
    )


def init_celery(celery: Celery, app: Flask) -> Celery:
    """
    Celery factory
    :param celery:
    :param app:
    :return:
    """
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

