import logging

from app.config import BaseConfig
from app.models import Device
from app.models import Syslog
from app.utils.utils import generate_mkdn_message
from slack_sdk import WebClient
from slack_sdk.web import SlackResponse
from slack_sdk.errors import SlackApiError
from typing import Tuple
from socket import socket


class SlackIntegration:
    """
    Class to handle all slack interactions
    """
    def __init__(self):
        self.client = WebClient(token=BaseConfig.SLACK_USER_OAUTH_TOKEN)
        self.user_token = BaseConfig.SLACK_USER_OAUTH_TOKEN
        self.channel_id = None
        self.join_channel()

    def post_any_message(self, kwargs) -> None:
        try:
            response = self.client.chat_postMessage(**kwargs)
            logging.info(f"Response: {response}")
        except SlackApiError as e:
            logging.error(f"Error uploading file: {e}")

    def post_message(self, message: dict) -> any:
        """
        This function will post a message in the default channel if level is error
        :param message:
        :return:
        """
        logging.info(message)
        # If the level is greater, do not post messages
        if message["level"] > BaseConfig.LOGGING_LEVEL_FILTER:
            return
        try:
            blocks = self._generate_slack_block(message=message)
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                blocks=blocks,
                mrkdwn=True,
                text=generate_mkdn_message(message=message, format="JIRA")
            )
            return response
        except SlackApiError as e:
            logging.error(f"Got an error: {e.response['error']}")

    def join_channel(self) -> None:
        """
        Function will check if channel exists, then will join it
        :return:
        """
        response = self.client.conversations_list()
        for channel in response.data["channels"]:
            if channel["name"] == BaseConfig.SLACK_CHANNEL:
                self.channel_id = channel["id"]
        if not self.channel_id:
            raise Exception(f"Channel: {BaseConfig.SLACK_CHANNEL} was not found")
        self.client.conversations_join(channel=self.channel_id)

    def upload_file(self, filename: str) -> SlackResponse:
        """
        This will upload a file to slack
        :param filename:
        :return:
        """
        try:
            # Send Slack Message
            response = self.client.files_upload(
                file=filename,
            )
            return response
        except SlackApiError as e:
            logging.error(f"Error uploading file: {e}")

    def make_file_public(self, slack_file_id: str) -> SlackResponse:
        """
        Make file public on Slack
        :param slack_file_id:
        :return:
        """
        try:
            response = self.client.files_sharedPublicURL(
                file=slack_file_id,
                token=self.user_token
            )
            return response
        except SlackApiError as e:
            logging.error(f"Error uploading file: {e}")

    def process_syslog_message(self, request: Tuple[bytes, socket]):
        """
        This function will parse the message and store it as a message_dict.
        We will also save it to mongo db
        :param request: Tuple that contains bytes and socket
        :return:
        """
        # Parse data from socket request
        message = bytes.decode(request[0].strip())
        source_ip_address, source_port = request[1].getsockname()
        message_list = message.split("-")

        # Store it in a data structure
        message_dict = dict()
        message_dict["src_port"] = source_port
        message_dict["src_ip"] = source_ip_address
        message_dict["time"] = message_list[0].split(":", 1)[1].split(": ")[0].strip()
        message_dict["level"] = int(message_list[1])
        message_dict["syslog"] = message_list[2]

        # Save to mongo
        devices = Device.objects(src_ip=source_ip_address)
        if not devices:
            device = Device(src_ip=source_ip_address, src_port=source_port)
        else:
            device = devices[0]

        # Save syslog to database
        syslog = Syslog(**message_dict)
        syslog.save()
        message_dict["syslog_id"] = str(syslog.id)

        # Send message
        response = self.post_message(message=message_dict)

        # Get the slack thread id and save it to the syslog
        thread_ts = response.data["ts"]
        syslog.thread_ts = thread_ts
        syslog.save()

        # Reference is in the device and save the device
        device.syslogs.append(syslog)
        device.syslog_count += 1
        device.save()

    @staticmethod
    def _generate_slack_block(message: dict) -> list:
        value = message["syslog_id"]
        del message["syslog_id"]
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": generate_mkdn_message(message=message, format="SLACK")
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "style": "primary",
                        "value": value,

                        "text": {
                            "type": "plain_text",
                            "text": "Create Jira Ticket"
                        }
                    },
                    {
                        "type": "button",
                        "style": "danger",
                        "text": {
                            "type": "plain_text",
                            "text": f"SSH to {message['src_ip']}"
                        },
                        "url": f"ssh://{message['src_ip']}"
                    },
                    {
                        "type": "overflow",
                        "options": [
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Generate 1 day chart"
                                },
                                "value": value
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Generate 1 week chart"
                                },
                                "value": value
                            },
                            {
                                "text": {
                                    "type": "plain_text",
                                    "text": "Generate 1 month chart"
                                },
                                "value": value
                            }
                        ]
                    }
                ]
            }
        ]
        return blocks



