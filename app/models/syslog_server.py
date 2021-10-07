import logging
import socketserver

from app.config import BaseConfig
from app.models import SlackIntegration


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=BaseConfig.LOG_FILE,
    filemode='a')


slack_integration = SlackIntegration()


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    """
    Adding a custom handler per syslog request
    """
    def handle(self) -> None:
        # Push message to slack channel
        slack_integration.process_syslog_message(request=self.request)
