import datetime
from app import mongo_db


class Syslog(mongo_db.Document):
    """
    Schema for mongodb to store syslogs under Device.syslogs
    """
    src_ip = mongo_db.StringField(required=True)
    src_port = mongo_db.IntField(required=True)
    level = mongo_db.IntField(required=True)
    syslog = mongo_db.StringField(required=True)
    time = mongo_db.StringField(required=True)
    thread_ts = mongo_db.StringField()
    date_created = mongo_db.DateTimeField(default=datetime.datetime.now)

    def __init__(self, src_ip: str, src_port: str, level: str, time: str, **kwargs):
        super().__init__(src_ip=src_ip, src_port=src_port, level=level, time=time, **kwargs)