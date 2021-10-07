import logging

from app.config import BaseConfig
from app.server import app_blueprints
from app.tasks import generate_jira_ticket, generate_timeline_chart
from flask import abort, jsonify
from flask import request
from app.utils.utils import unmarshall_slack_api_request, generate_200_ok

logger = logging.getLogger(__name__)


@app_blueprints.before_request
def pre_check():
    """
    Verify Slack token for every request
    :return:
    """
    if "payload" in request.form:
        logger.info(f"Slack Body: {unmarshall_slack_api_request(api_request=request)}")
        json_body = unmarshall_slack_api_request(api_request=request)
        if json_body["token"] != BaseConfig.SLACK_VERIFICATION_TOKEN:
            return abort(403)


@app_blueprints.route('/', methods=['GET'])
def index():
    """
    Sanity API route to verify server is up
    :return:
    """
    return jsonify("API is Up")


@app_blueprints.route('/slack/message_actions', methods=['POST'])
def slack_button_response():
    """
    API route to handle user interactions to bot messages
    :return:
    """
    if request.method != "POST":
        abort(400)

    json_body = unmarshall_slack_api_request(api_request=request)
    button_action = json_body["actions"][0]
    button_type = button_action["type"]
    if button_type == "button":
        button_metadata = button_action["text"]["text"]
        if button_metadata == "Create Jira Ticket":
            generate_jira_ticket.apply_async(args=[json_body])
    elif button_type == "overflow":
        generate_timeline_chart.apply_async(args=[json_body])

    return generate_200_ok()



