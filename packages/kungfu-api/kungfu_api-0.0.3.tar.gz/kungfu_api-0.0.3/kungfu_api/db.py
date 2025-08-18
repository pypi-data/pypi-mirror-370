import sys, os, datetime, uuid
from playhouse.shortcuts import ReconnectMixin

sys.path.append(os.getcwd())
try:
    from config.app_setting import APP_SETTING
except Exception:
    APP_SETTING = {}

import peewee as pw

class ReconnectMySQLDatabase(ReconnectMixin, pw.MySQLDatabase):
    pass


db = ReconnectMySQLDatabase(
    host=APP_SETTING["db"]["host"] if "db" in APP_SETTING else "",
    port=APP_SETTING["db"]["port"] if "db" in APP_SETTING else "",
    user=APP_SETTING["db"]["user"] if "db" in APP_SETTING else "",
    passwd=APP_SETTING["db"]["passwd"] if "db" in APP_SETTING else "",
    database=APP_SETTING["db"]["database"] if "db" in APP_SETTING else "",
    charset=APP_SETTING["db"]["charset"] if "db" in APP_SETTING else ""
)


def gen_id():
    return uuid.uuid4().hex


class BaseModel(pw.Model):
    id = pw.CharField(primary_key=True, unique=True, max_length=128, default=gen_id, help_text="主键ID")
    created = pw.DateTimeField(default=datetime.datetime.now, help_text="创建时间")
    is_del = pw.IntegerField(default=0, help_text="是否删除，0-否，1-是")

    class Meta:
        database = db

    def to_dict(self):
        data = {}
        for k in self.__dict__['__data__'].keys():
            if str(k).startswith('_'):
                continue
            if isinstance(self.__dict__['__data__'][k], datetime.datetime):
                data[k] = self.__dict__['__data__'][k].strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(self.__dict__['__data__'][k], datetime.date):
                data[k] = self.__dict__['__data__'][k].strftime('%Y-%m-%d')
            else:
                data[k] = self.__dict__['__data__'][k]
        return data
