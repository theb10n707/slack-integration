import datetime
from app import mongo_db
from app.models import Syslog


class Device(mongo_db.Document):
    """
    Schema for mongodb to store devices
    """
    src_ip = mongo_db.StringField()
    src_port = mongo_db.IntField()
    syslog_count = mongo_db.IntField()
    syslogs = mongo_db.ListField(mongo_db.ReferenceField(Syslog))
    date_created = mongo_db.DateTimeField(default=datetime.datetime.now)

    def __init__(self, src_ip: str, src_port: str, **kwargs):
        if "syslog_count" not in kwargs:
            syslog_count = 0
            super().__init__(src_ip=src_ip, src_port=src_port, syslog_count=syslog_count, **kwargs)
        else:
            super().__init__(src_ip=src_ip, src_port=src_port, **kwargs)