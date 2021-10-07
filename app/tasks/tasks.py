import logging
import os
import socketserver


from app import celery
from app import BaseConfig
from app.models import SlackIntegration, Syslog, SyslogUDPHandler
from app.utils.utils import create_jira_issue, DAYS, generate_chart
from celery.contrib.abortable import AbortableTask
from datetime import datetime, timedelta
from mongoengine import connect

slack = SlackIntegration()
connect(host=BaseConfig.MONGODB_HOST)


@celery.task()
def generate_jira_ticket(json_body: dict) -> None:
    """
    Asynchronous task to generate a jira ticket and post in slack channel
    :param json_body:
    :return:
    """
    try:
        # Parse Response
        action = json_body["actions"][0]
        syslog_id = action["value"]
        syslog = Syslog.objects.get(id=syslog_id)

        # Create Jira Issue
        jira_url = create_jira_issue(message=syslog.to_mongo())

        params = {
            "channel": json_body["channel"]["id"],
            "mrkdwn": True,
            "thread_ts": syslog.thread_ts,
            "text": f"JIRA bug created here {jira_url}"
        }

        slack.post_any_message(kwargs=params)
    except Exception as e:
        logging.info(f"Error: {e}")


@celery.task()
def generate_timeline_chart(json_body: dict) -> None:
    """
    Asynchronous task to generate chart and post in slack channel
    :param json_body:
    :return:
    """
    # Parse response
    selected_option = json_body["actions"][0]["selected_option"]
    syslog_id = selected_option["value"]
    syslog = Syslog.objects.get(id=syslog_id)

    # Generate chart range
    chart_type = selected_option["text"]["text"]
    chart_name = chart_type[9:]
    days = DAYS[chart_name]
    end_time = datetime.today()
    start_time = end_time - timedelta(days=days)

    # Create mongodb aggregation
    query_pipeline = [
        {"$match": {"src_ip": syslog.src_ip, "date_created": {"$gte": start_time, "$lt": end_time}}},
        {"$group": {"_id": {"day": {"$dayOfMonth": "$date_created"}, "month": {"$month": "$date_created"}, "year": {"$year": "$date_created"}}, "count": {"$sum": 1}}}
    ]

    # Make Database aggregation from data
    per_day_counts = list(Syslog.objects().aggregate(pipeline=query_pipeline))

    # Generate a chart and save it as a .png file
    temp_filename = generate_chart(mongo_db_data=per_day_counts, end_time=end_time, start_time=start_time)

    # Upload chart image to slack
    upload_response = slack.upload_file(filename=temp_filename)
    os.remove(temp_filename)
    slack_file_id = upload_response.data["file"]["id"]

    # Make the file public
    public_file_response = slack.make_file_public(slack_file_id=slack_file_id)
    permalink = public_file_response.data["file"]["permalink_public"]

    params = {
        "channel": json_body["channel"]["id"],
        "mrkdwn": True,
        "attachments": [
            {
                "image_url": permalink,
                "text": f"{chart_name.title()} for {syslog.src_ip}"
            }
        ],
        "thread_ts": syslog.thread_ts,
    }

    # Post chart image to slack thread
    slack.post_any_message(kwargs=params)


@celery.task(bae=AbortableTask)
def run_syslog_server() -> None:
    """
    Code start the syslog server
    :return:
    """
    # Kill old server if still running
    logging.info("Killing any process using syslog port")
    os.system(f"lsof -t -i :{BaseConfig.PORT} | xargs kill -9")
    try:
        print("Syslog Server Starting")
        server = socketserver.UDPServer((BaseConfig.HOST, BaseConfig.PORT), SyslogUDPHandler)
        server.serve_forever(poll_interval=0.5)
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("Crtl+C Pressed. Shutting down.")


