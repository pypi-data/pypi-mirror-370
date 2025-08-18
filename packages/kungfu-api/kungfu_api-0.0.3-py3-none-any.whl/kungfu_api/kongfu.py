import json, uuid, sys, os, datetime, mimetypes
from urllib.parse import parse_qs
import cgi
import threading
from io import BytesIO
import xmldict
import jwt
import tempfile
from decimal import Decimal
from peewee import Field
from .db import db, BaseModel


sys.path.append(os.getcwd())

# try:
#     from config import APP_SETTING, API_PERMISSION
# except Exception:
#     APP_SETTING = {}
#     API_PERMISSION = {}

# try:
#     from config.sql_template import SQL_TEMPLATE
# except Exception:
#     SQL_TEMPLATE = {}

try:
    from config.app_setting import APP_SETTING
    from config.permission_setting import API_PERMISSION
    import models
    from config.template_setting import SQL_TEMPLATE
    from models import MODEL_API_SETTING

    MODEL_MAPPING = {}
    for attr_name in dir(models):
        attr = getattr(models, attr_name)
        if isinstance(attr, type) and issubclass(attr, BaseModel) and attr != BaseModel:
            MODEL_MAPPING[attr._meta.table_name] = attr

    for key in MODEL_API_SETTING:
        MODEL_MAPPING[key] = MODEL_API_SETTING[key]

except Exception:
    APP_SETTING = {}
    API_PERMISSION = {}
    MODEL_MAPPING = {}
    SQL_TEMPLATE = {}

from wsgiref.simple_server import make_server


# region tools

def get_mapping_model(resource):
    if resource not in MODEL_MAPPING:
        return None
    if type(MODEL_MAPPING[resource]) == tuple:
        return MODEL_MAPPING[resource][0]
    else:
        return MODEL_MAPPING[resource]


def get_mapping_operation(resource):
    if resource not in MODEL_MAPPING:
        return []
    if type(MODEL_MAPPING[resource]) == dict:
        return MODEL_MAPPING[resource][1]
    else:
        return ['list', 'get', 'post', 'put', 'delete', 'drop']


def jwt_encode(user):
    # 把需要用来做权限校验的字段 都加入token中
    # 例如：{ "id": user.id, "role": user.role， "org_id": user.org_id }
    user_dict = user.to_dict()
    data = {}
    for item in APP_SETTING["jwt"]["column"]:
        data[item] = user_dict[item] if item in user_dict else ""

    return jwt.encode(data, APP_SETTING["jwt"]["secret"], algorithm='HS256')


def jwt_decode(token):
    return jwt.decode(token, APP_SETTING["jwt"]["secret"], algorithms=['HS256'])


def row_to_dict(cursor, row):
    """将返回结果转换为dict"""
    d = {}
    for idx, col in enumerate(cursor.description):
        if str(col[0]).startswith('_'):
            continue

        d[col[0]] = row[idx]
        if isinstance(row[idx], datetime.datetime):
            d[col[0]] = row[idx].strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(row[idx], datetime.date):
            d[col[0]] = row[idx].strftime('%Y-%m-%d')
        elif isinstance(row[idx], Decimal):
            if Decimal(str(row[idx])) == Decimal(str(row[idx])).to_integral_value():
                d[col[0]] = int(row[idx])
            else:
                d[col[0]] = float(row[idx])
        else:
            d[col[0]] = row[idx]
    return d


def get_permission(path_resource, path_operation):
    if path_resource in API_PERMISSION:
        if path_operation in API_PERMISSION[path_resource]:
            permission = API_PERMISSION[path_resource][path_operation]
        elif path_operation in API_PERMISSION["__default"]:
            permission = API_PERMISSION["__default"][path_operation]
        else:
            permission = API_PERMISSION["__default"]["__other"]
    else:
        if path_operation in API_PERMISSION["__default"]:
            permission = API_PERMISSION["__default"][path_operation]
        else:
            permission = API_PERMISSION["__default"]["__other"]
    return permission

# endregion


# region request

url_map = {}
class Request(threading.local):

    def getRequestText(self):
        MEMFILE_MAX = 1024 * 100

        maxread = max(0, self.content_length)
        stream = self._environ['wsgi.input']
        body = BytesIO() if maxread < MEMFILE_MAX else tempfile.TemporaryFile(mode='w+b')
        while maxread > 0:
            part = stream.read(min(maxread, MEMFILE_MAX))
            if not part:  # TODO: Wrong content_length. Error? Do nothing?
                break
            body.write(part)
            maxread -= len(part)
        return body.getvalue().decode()

    def bind(self, environ, url_map):
        self._environ = environ

        self._headers = None
        self._user = None
        self._text = ''
        self._params = {}
        self._data = {}
        self._files = {}

        self.path = self._environ.get('PATH_INFO', '')
        self.path_resource = ''
        self.path_operation = ''
        self.path_param = ''

        if self.path.startswith('/api/'):
            arr_path = str(str(self.path).replace('/api/', '')).split('/')
            self.path_resource = arr_path[0]
            self.path_operation = arr_path[1]
            self.path_param = arr_path[2] if len(arr_path) == 3 else None

        # region URL 参数
        query_string = self._environ.get('QUERY_STRING', '')
        raw_dict = parse_qs(query_string, keep_blank_values=1)
        for key, value in raw_dict.items():
            if len(value) == 1:
                self._params[key] = value[0]
            else:
                self._params[key] = value
        # endregion

        # region 请求处理
        if self.path_resource in url_map and self.path_operation in url_map[self.path_resource] \
                and url_map[self.path_resource][self.path_operation]["secret"] != None:
            secret = url_map[self.path_resource][self.path_operation]["secret"]
        elif self.path_resource == "file":
            secret = False
        else:
            secret = APP_SETTING["request"]["secret"]

        if self.path_resource != "file":
            self._text = self.getRequestText()
        if "multipart/form-data" in self.content_type and self.path_resource:
            raw_data = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
            if raw_data.list:
                for key in raw_data:
                    if raw_data[key].filename:
                        self._files[key] = raw_data[key]
                    elif isinstance(raw_data[key], list):
                        self._data[key] = [v.value for v in raw_data[key]]
                    else:
                        self._data[key] = raw_data[key].value

            if secret:
                self._data = APP_SETTING["request"]["process"](self._data)
        if "application/json" in self.content_type:
            self._data = json.loads(self._text) if self._text else {}
            if secret:
                self._data = APP_SETTING["request"]["process"](self._data)
        if "application/xml" in self.content_type or "text/xml" in self.content_type:
            self._data = xmldict.xml_to_dict(self._text)
            if secret:
                self._data = APP_SETTING["request"]["process"](self._data)
        # endregion

    # region 请求信息

    @property
    def method(self):
        return self._environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def headers(self):
        if self._headers == None:
            self._headers = {}
            for key, value in dict(self._environ).items():
                if str(key).startswith("HTTP_"):
                    self._headers[str(key).replace("HTTP_", "")] = value
        return self._headers

    @property
    def user(self):
        if self._user == None:
            token = self.headers["AUTHORIZATION"] if "AUTHORIZATION" in self.headers and self.headers[
                "AUTHORIZATION"] else ""
            if token:
                self._user = jwt_decode(token)
            else:
                self._user = {
                    "id": "",
                    "username": "anymore",
                    "name": "匿名用户",
                    "role": "anymore"
                }
                for item in APP_SETTING["jwt"]["column"]:
                    if item not in self._user:
                        self._user[item] = ""
        return self._user

    @property
    def content_type(self):
        return self._environ.get('CONTENT_TYPE', '')

    @property
    def content_length(self):
        return int(self._environ.get('CONTENT_LENGTH', '') or -1)

    # endregion

    # region 请求数据

    @property
    def text(self):
        return self._text

    @property
    def params(self):
        return self._params

    @property
    def data(self):
        return self._data

    @property
    def files(self):
        return self._files

    # endregion

# endregion


# region db

# endregion


# region auto_view

def generate_where_and_params(dict_where):
    #     """
    #     __exact 精确等于 like ‘aaa’
    #     __contains 包含 like ‘%aaa%’
    #     __gt 大于
    #     __gte 大于等于
    #     __lt 小于
    #     __lte 小于等于
    #     __in 存在于一个list范围内 (1, 2)
    #     __isnull 为null 不是'' ， 值：true， false
    #     """
    #
    #     """
    #     __year 时间或日期字段的年份
    #     __month 时间或日期字段的月份
    #     __day 时间或日期字段的日
    #     __date 时间或日期字段的日期部分
    #     __startswith 以…开头
    #     __endswith 以…结尾
    #     """

    arr_where = []
    param_where = []
    for key in dict_where.keys():
        if dict_where[key] != '':
            arr_k = key.split("__")
            if len(arr_k) == 1:
                arr_where.append(key + " = %s")
                param_where.append(dict_where[key])
            if len(arr_k) == 2:
                field = arr_k[0]
                operation = str(arr_k[1]).lower()
                if operation == "exact":
                    arr_where.append(field + " = %s")
                    param_where.append(dict_where[key])
                if operation == "contains":
                    arr_where.append(field + " like %s")
                    param_where.append("%" + dict_where[key] + "%")
                if operation == "gt":
                    arr_where.append(field + " > %s")
                    param_where.append(dict_where[key])
                if operation == "gte":
                    arr_where.append(field + " >= %s")
                    param_where.append(dict_where[key])
                if operation == "lt":
                    arr_where.append(field + " < %s")
                    param_where.append(dict_where[key])
                if operation == "lte":
                    arr_where.append(field + " <= %s")
                    param_where.append(dict_where[key])
                if operation == "in" and len(dict_where[key]) > 0:
                    arr_where.append(field + " in (" + ",".join(['%s' for item in dict_where[key]]) + ") ")
                    if isinstance(dict_where[key], list):
                        for  item in dict_where[key]:
                            param_where.append(item)
                if operation == "isnull" and dict_where[key] == True:
                    arr_where.append("ISNULL(" + field + ")")
                if operation == "isnull" and dict_where[key] == False:
                    arr_where.append("NOT ISNULL(" + field + ")")

    return arr_where, tuple(param_where)


def auto_list(request, table_name):
    select = request.data.get('select', '*')
    where = request.data.get('where', '{}')
    order_by = request.data.get('order_by', '')

    page = int(request.data.get('page', '1'))
    size = int(request.data.get('size', '10000'))

    str_sql = "select " + select + " from " + table_name

    if table_name in SQL_TEMPLATE:
        str_sql = "select " + select + " from (" + SQL_TEMPLATE[table_name] + ") t_template "

    dict_temp = where if type(where) == dict else json.loads(where)
    dict_template = dict()
    dict_where = dict()

    for key in dict_temp:
        if '__template' in key:
            dict_template[str(key).replace('__template', '')] = dict_temp[key]
        else:
            dict_where[key] = dict_temp[key]

    if dict_template:
        str_sql = str_sql.format(**dict_template)

    arr_where, param_where = generate_where_and_params(dict_where)

    if len(arr_where) > 0:
        str_sql += " where " + " and ".join(arr_where)

    if order_by:
        str_sql += " order by " + order_by

    data_sql = "select * from (" + str_sql + ") t limit " + str((page - 1) * size) + "," + str(size)
    data_cursor = db.execute_sql(data_sql, param_where)
    data = data_cursor.fetchall()

    count_sql = "select count(*) from (" + str_sql + ") t "
    count_cursor = db.execute_sql(count_sql,param_where)
    count = count_cursor.fetchall()

    return {
        "code": 200,
        "data": [row_to_dict(data_cursor, row) for row in data],
        "total": count[0][0],
        "msg": "Success"
    }


def auto_get(request, table_name, pk):
    select = request.data.get('select', '*')
    str_sql = "select " + select + " from " + table_name + " where id = %s "

    cursor = db.execute_sql(str_sql, (pk,))
    row = cursor.fetchone()

    if not row:
        return {
            "code": 404,
            "msg": "Not Found"
        }

    data = row_to_dict(cursor, row)

    return {
        "code": 200,
        "data": data,
        "msg": "Success"
    }


def auto_post(request, table_name):
    Model = get_mapping_model(table_name)

    model = Model.create(**request.data)

    return {
        "code": 200,
        "msg": "Success",
        "data": model.to_dict()
    }


def auto_put(request, table_name, pk):

    Model = get_mapping_model(table_name)
    model = Model.get_or_none(Model.id == pk)

    if not model:
        return {"code": 400, "msg": "参数错误！"}

    for r in request.data.keys():
        model.__setattr__(r, request.data[r])

    model.save()

    return {
        "code": 200,
        "msg": "Success",
        "data": model.to_dict()
    }


def auto_delete(request, table_name, pk):
    Model = get_mapping_model(table_name)
    model = Model.get_or_none(Model.id == pk)

    if not model:
        return {"code": 400, "msg": "参数错误！"}

    model.is_del = 1
    model.save()

    return {
        "code": 200,
        "msg": "Success"
    }


def auto_drop(request, table_name, pk):
    Model = get_mapping_model(table_name)
    model = Model.get_or_none(Model.id == pk)

    if not model:
        return {"code": 400, "msg": "参数错误！"}

    model.delete_instance()

    return {
        "code": 200,
        "msg": "Success"
    }


auto_config = {
    "list": auto_list,
    "get": auto_get,
    "post": auto_post,
    "put": auto_put,
    "delete": auto_delete,
    "drop": auto_drop
}

# endregion


# region file_view

def file_file(request, operation):
    field_storage = request.files.get("file")

    allow_file_type = APP_SETTING["file"][operation]
    file_type = field_storage.filename.split('.')[-1]
    if str(file_type).lower() not in allow_file_type:
        return {
            "code": 400,
            "msg": "File Type Error!"
        }

    file_name = uuid.uuid4().hex + '.' + file_type

    root_path = os.getcwd()
    dt_path = datetime.datetime.now().strftime("%Y%m%d")
    full_path = os.path.join(root_path, 'static/files', dt_path)

    if not os.path.isdir(full_path):
        os.makedirs(full_path)

    with open(os.path.join(full_path, file_name), "wb") as f:
        f.write(field_storage.value)

    return {
        "code": 200,
        "data": '/static/files/' + dt_path + '/' + file_name,
        "msg": "Success"
    }

# endregion


# region doc_view

def doc_list():
    result = {}

    temp = {
        "demo": {
            "get": {
                "title": "获取demo",
                "role": ["all"],
                "params": [],
                "body": [],
                "desc": "获取demo"
            },
            "post": {
                "title": "获取demo",
                "role": ["all"],
                "params": [],
                "body": [],
                "desc": "获取demo"
            }
        }
    }

    for key, value in MODEL_MAPPING.items():
        result[key] = {}
        if isinstance(value, tuple):
            Model = value[0]
            operations = value[1] if len(value) >= 2 else ['list', 'get', 'post', 'put', 'delete', 'drop']
        else:
            Model = value
            operations = ['list', 'get', 'post', 'put', 'delete', 'drop']

        operation_desc_dict = {
            "list": "获取{}列表",
            "get": "根据主键ID获取单个{}",
            "post": "新增{}",
            "put": "修改{}",
            "delete": "软删除{}",
            "drop": "真删除{}"
        }

        for operation in operations:
            body = []
            for item in dir(Model):
                column = getattr(Model, item)
                if len(item) > 1 and item[0] != '_' and issubclass(type(column), Field):
                    if operation in ['post', 'put'] and column.name not in ['id', 'is_del', 'created']:
                        body.append({
                            "name": column.name,
                            "type": column.field_type,
                            "desc": column.help_text,
                        })
                    if operation in ['list'] and column.name not in ['id']:
                        body.append({
                            "name": column.name,
                            "type": column.field_type,
                            "desc": column.help_text,
                        })

            params = [{
                "id": "主键ID"
            }] if operation in ['get', 'put', 'delete', 'drop'] else []

            if operation == 'list':
                curl_cmd = '''# 使用curl命令调用：\n '''
                curl_cmd += '''$ curl -X POST -H 'Content-Type: application/json' -H 'AUTHORIZATION: Your Token' -d '{"select": "*", "where": {"is_del": 0}, "order_by": "created desc", "page": 1, "size": 10}' '''
                curl_cmd += f''' http://127.0.0.1:8000/api/{key}/{operation} \n\n'''
                curl_cmd += '''# 更多高级查询技巧参考教程'''
            else:
                curl_cmd = '''# 使用curl命令调用： \n$ curl -X POST -H 'Content-Type: application/json' -H 'AUTHORIZATION: Your Token' '''
                if body:
                    curl_data = []
                    for row in body:
                        curl_data.append('"' + row['name'] + '": Your Value')
                    curl_cmd += ''' -d '{ ''' + ', '.join(curl_data) + ''' }' '''

                curl_cmd += f'''  http://127.0.0.1:8000/api/{key}/{operation}{'/{id}' if params else ''} '''
            result[key][operation] = {
                "category": "generate",
                "method": ["POST"],
                "title": operation_desc_dict[operation].format(Model.__doc__),
                "role": get_permission(key, operation),
                "params": params,
                "body": body,
                "run": curl_cmd
            }

    for resource_key, resource_value in url_map.items():
        if resource_key not in result:
            result[resource_key] = {}

        for operation_key, operation_value in resource_value.items():
            result[resource_key][operation_key] = {
                "category": "user",
                "method": operation_value["method"],
                "title": "用户自定义接口，不生成参数，调用方式见右侧说明！",
                "role": get_permission(resource_key, operation_key),
                "params": [],
                "body": [],
                "run": operation_value["handle"].__doc__
            }

    # print(result)

    style = '''
    <style type="text/css">
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        html, body {
            height: 100%;
        }

        .container {
            height: 100%;
            display: flex;
            flex-direction: row;
        }

        .container > .menu {
            height: 100%;
            width: 220px;
            border-right: 1px solid black;
            display: flex;
            flex-direction: column;
        }

        .container > .menu > .menu-title {
            width: 100%;
            background-color: #22282F;
            border-bottom: 1px solid black;
            padding: 20px 10px;
            color: white;
            font-size: 24px;
            line-height: 24px;
            font-weight: bold;
        }

        .container > .menu > .menu-items {
            flex: 1;
            background-color: #2B333B;
            overflow: auto;
        }

        .container > .menu > .menu-items > .menu-group {
            width: 100%;
            background-color: #2D353E;
            border-left: 4px solid #2D353E;
            transition: all .3s;
        }

        .container > .menu > .menu-items > .menu-group:hover {
            border-left: 4px solid goldenrod;
        }

        .container > .menu > .menu-items > .menu-group > .group-title {
            height: 36px;
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            padding: 0 8px;
        }

        .container > .menu > .menu-items > .menu-group > .group-title:hover {
            background-color: #4D5B6B;
        }

        .container > .menu > .menu-items > .menu-group > .group-title > .title-left {
            display: flex;
            flex-direction: row;
            align-items: center;
        }

        .container > .menu > .menu-items > .menu-group > .group-title > .title-left > .resource-icon {
            margin-right: 8px;
            width: 16px;
            height: 16px;
            background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAShJREFUOE+lkz8vBFEUxX/nayhQEaJXod5EolLaRDb6LRCVf5XQUItItCoJUSPxCYTsVih8jcOb3JGZzZsV3GYm8879zbnvnSf+WWrqtz0GbMT6kaS3nDYLsN0FtoGzaOoA+5KOByE1gO0l4AB4B1YlfaQG2yPAOTAKbEm6KkHfANt3wCSwLOkhZ9f2HHAJ9CQtJE0VYEmyPSGp3wAYl/Rqu9A2AXaBFtCR9BQjzMR+9CWtDAVEwyxwAjyGkwRcl3QT680OqtZtJzd8uS2eZf3ooCLcCcDeXwG/cnAf59yS9BKz1gC2p4DblBNJ87VTiIY2kNJ2LaltezpGeLZ9ASwCXUnpvaimKB/GPVgL3SmQ7sPm0CgPbFRKZZn99NdeLlyNtzEnzn37BL5nmxGaAbsSAAAAAElFTkSuQmCC')
        }

        .container > .menu > .menu-items > .menu-group > .group-title > .title-left > .resource {
            font-size: 14px;
            line-height: 14px;
            color: white;
        }

        .container > .menu > .menu-items > .menu-group > .group-title > .title-right > .sel-icon {
            width: 16px;
            height: 16px;
            background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAIhJREFUOE/NksERgCAMBO9KswgtwibUJixCi7C0Exx0FIkyw4d8+GQ3XCZEYbGQRyUCSRuAmeSaE0lSC6An2RwRJI3uGQB0f5IAL44bSU7XDnIkMeyHP5b4JUnBL4EVx4KTglgSluozTyT9rh5l3sEtjgeSsPmDc0SQIDX57KnkEnOuz+opjrADwIVAEfeS3ZYAAAAASUVORK5CYII=')
        }

        .container > .menu > .menu-items > .menu-group > .group-list {
            background-color: #171C21;
            display: none;
        }

        .container > .menu > .menu-items > .menu-group-open > .group-title > .title-right > .sel-icon {
            transform: rotate(180deg);
        }

        .container > .menu > .menu-items > .menu-group-open > .group-list {
            display: block;
            /*height: auto;*/
        }
        .container > .menu > .menu-items > .menu-group-open > .group-list > .group-list-item {
            height: 36px;
            display: flex;
            flex-direction: row;
            align-items: center;
            border-bottom: 1px solid #2D353E;
            text-decoration: none;
        }
        .container > .menu > .menu-items > .menu-group-open > .group-list > .group-list-item:hover {
            background-color: #020203;
        }

        .container > .menu > .menu-items > .menu-group-open > .group-list > .group-list-item > .group-list-item-icon {
            margin-right: 8px;
            width: 16px;
            height: 16px;
            background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAG1JREFUOE+108ENgCAQRNG/7VCQFzuwA1uyINsZ5WBiIshEhIQbPJbNbNC5onRfUoqI3bEfgKQZWIHJQWoVbEBykCKQSz+/YSFVwEVeAQdpAi1kPNBq5rgmtl6+Uvp/kCQtQN5dUf4+TM4E3s8c0XpEEaAFoz8AAAAASUVORK5CYII=');
        }
        .container > .menu > .menu-items > .menu-group-open > .group-list > .group-list-item > .group-list-item-text {
            color: white;
            font-size: 14px;
            line-height: 14px;
        }
        .container > .menu > .menu-items > .menu-group-open > .group-list > .group-list-item > .group-list-item-text-user {
            color: orange;
        }

        .container > .menu > .menu-auth {
            width: 100%;
            height: 36px;
            border-top: 1px solid black;
            background-color: #2B333B;
            color: white;
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            align-items: center;
            padding: 0 8px;
        }

        .container > .menu > .menu-auth > .auth-left {
            display: flex;
            flex-direction: row;
        }

        .container > .menu > .menu-auth > .auth-left > .user-icon {
            margin-right: 8px;
            width: 16px;
            height: 16px;
            background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAPxJREFUOE+l061OA0EUxfH/seAABy9QFCBRFU2RuPoiwDXBoEESEtJUIorB4XCAoE+w4HgAHB8S7KGTLE2Zmc0uYc0kmzO/vffOrPjno9x+2+vAGbANvAITSQe5bALYXgI+MuGhpMP4fQ44B5JgubEn6XoeyQEP05LbFaM5kXRcB5wCRxXArqSbOmANeMkA95K6tTMIAdurwAjoAG/AVVz6D5Q9xr9cjdwQ94ENoBVBz8CTpIvKGdi+BZI+I+hO0k7Sgu0+MG5Y/p6ky5CdtWC7ADYbAo/T49yKgU9goSHwJWkxBsKxBXUFWC7Xee+9/EfCWkga/AIafjmJfQNlHUcRuJI++QAAAABJRU5ErkJggg==')
        }

        .container > .menu > .menu-auth > .auth-left > .current {
            font-size: 14px;
            line-height: 14px;
            margin: 0 8px;
        }

        .container > .menu > .menu-auth > .user-add {
            width: 16px;
            height: 16px;
            background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAAV5JREFUOE+lk78rhVEYxz/ff8BkIAablBgoFEYmkjC5YpKyymq9WZVM5JqQxMSIQjGQks1ADCb/wOM9b+e5vffy3m45y1vvOc/n+XE+R/xzqTrezNqAJaAD6In798AzsCnpNRtTATCzeWADOEqCT4HreHgAGAMmgWVJOw4pA8xsCLgAZiQd/NWZmU0D+8CwpMtwJgWYWSPwAoxICuXmLjMLbZ0D7ZK+HLAONEhazEaa2VqaRUq/vsxsC/iWtOKAM2BPUqlOQAGYlTTqgE+g3yfsmav78EriTd1IanLAO9An6S3OpKLk8sRjK2bWCtxKanHACVCqnn6NGYTbKEgad0ARaJY0V+cMdoEPSasOCPY9AQt5DmRuIGTfBjrDzLIiBQvDRm+eC9GBu5gotbFa5WDjcUI/BK6A1DYg/B9MqpwCJtzCX4CMlavJe+gCuiPgIXkHj0Ax2Jf7mGopnLf3A/Q7lBHaGyO1AAAAAElFTkSuQmCC');
            cursor: pointer;
        }

        .container > .content {
            flex: 1;
            overflow-y: auto;
            padding: 0 28px;
            color: #333;
        }

        .container > .content > .content-title {
            width: 100%;
            padding: 20px 0;
            color: #333;
            font-size: 24px;
            line-height: 24px;
            font-weight: bold;
        }

        .container > .content > .content-resource {
            font-size: 30px;
            line-height: 30px;
            margin-bottom: 12px;
        }

        .container > .content > .line {
            width: 100%;
            border-bottom: 1px solid #ddd;
            margin-bottom: 28px;
        }

        .container > .content > .content-operation {
            display: flex;
            flex-direction: row;
            margin-bottom: 32px;
        }
        .container > .content > .content-operation > .operation-left {
            flex: 1;
            margin-right: 32px;
        }
        .container > .content > .content-operation > .operation-left > .operation-title {
            font-size: 20px;
            line-height: 20px;
            font-weight: bold;
            margin-bottom: 16px;
        }
        .container > .content > .content-operation > .operation-left > .operation-url {
            display: flex;
            flex-direction: row;
            margin-bottom: 12px;
        }
        .container > .content > .content-operation > .operation-left > .operation-url > .operation-url-method {
            font-size: 14px;
            line-height: 14px;
            background-color: #337ab7;
            padding: 4px 8px;
            color: white;
            border-radius: 4px;
            margin-right: 12px;
        }
        .container > .content > .content-operation > .operation-left > .operation-url > .operation-url-path {
            font-size: 14px;
            line-height: 14px;
            background-color: #f9f2f4;
            padding: 4px 8px;
            color: #c7254e;
            border-radius: 4px;
            margin-right: 12px;
        }
        .container > .content > .content-operation > .operation-left > .operation-des {
            font-size: 14px;
            line-height: 14px;
            margin-bottom: 12px;
        }
        .container > .content > .content-operation > .operation-left > .operation-role {
            font-size: 14px;
            line-height: 14px;
            margin-bottom: 12px;
            display: flex;
            flex-direction: row;
            align-items: center;
        }
        .container > .content > .content-operation > .operation-left > .operation-role > .role {
            font-size: 14px;
            line-height: 14px;
            background-color: #eeffee;
            padding: 2px 4px;
            color: #008800;
            border-radius: 4px;
            margin: 0 4px;
        }
        .container > .content > .content-operation > .operation-left > .operation-param-type {
            font-size: 16px;
            line-height: 16px;
            font-weight: bold;
            margin-bottom: 12px;
        }
        .container > .content > .content-operation > .operation-left > .operation-param-table {
            border-collapse: collapse;
            border: 1px solid #dddddd;
            width: 100%;
            margin-bottom: 12px;
        }
        .container > .content > .content-operation > .operation-left > .operation-param-table th {
            border: 1px solid #dddddd;
            padding: 8px;
            font-size: 14px;
            font-weight: bold;
        }
        .container > .content > .content-operation > .operation-left > .operation-param-table tr td {
            border: 1px solid #dddddd;
            padding: 8px;
            font-size: 14px;
        }

        .container > .content > .content-operation > .operation-left > .operation-param-table tbody tr:nth-child(odd) {
            background-color: #f9f9f9;
        }

        .container > .content > .content-operation > .operation-right {
            flex: 1;
            height: fit-content;
            min-height: 32px;
            border: 1px solid #ccc;
            background-color: #f8f8f8;
            border-radius: 4px;
            padding: 8px 16px;
            color: #666;
            overflow-x: auto;
        }
        .container > .content > .content-operation > .operation-right div {
            font-size: 14px;
            line-height: 24px;
            min-height: 28px;
            width: fit-content;
        }
    </style>
    '''

    script = '''<script>
      // 判断class有无
      function hasClass (ele, cls) {
        return ele.classList.contains(cls)
      }

      // 添加class
      function addClass (ele, cls) {
        if (!ele.classList.contains(cls)) {
          ele.classList.add(cls)
        }
      }

      // 去除class
      function removeClass (ele, cls) {
        if (ele.classList.contains(cls)) {
          ele.classList.remove(cls)
        }
      }

      function onMenuGroupClick(e) {
        let parent = e.parentNode
        if (hasClass(parent, 'menu-group-open')) {
          removeClass(parent, 'menu-group-open')
        } else {
          addClass(parent, 'menu-group-open')
        }
      }

      window.onload = () => {
      }
    </script>
    '''

    menu_group = ''
    for resource, resource_obj in result.items():
        menu_group_data = ''
        for operation, operation_obj in resource_obj.items():
            class_name = 'group-list-item-text-user' if operation_obj['category'] == 'user' else ''
            menu_group_data += '''
                    <a class="group-list-item" href="#{resource}_{operation}">
                        <div class="group-list-item-icon"></div>
                        <div class="group-list-item-text {class_name}">{operation}</div>
                    </a>
            '''.format(resource=resource, operation=operation, class_name=class_name)

        menu_group += f'''
        <div class="menu-group">
                <div class="group-title" onclick="onMenuGroupClick(this)">
                    <div class="title-left">
                        <div class="resource-icon"></div>
                        <div class="resource">{resource}</div>
                    </div>
                    <div class="title-right">
                        <div class="sel-icon"></div>
                    </div>
                </div>
                <div class="group-list">
                    {menu_group_data}
                </div>
            </div>
        '''

    operations = ''
    for resource, resource_obj in result.items():
        operations += f'''
            <div id="user" class="content-resource">{resource.capitalize()}</div>
            <div class="line"></div>
        '''

        for operation, operation_obj in resource_obj.items():
            method_str = ''
            for m in  operation_obj['method']:
                method_str += f'<div class="operation-url-method">{m}</div>'
            operations += f'''
                <div class="content-operation" id="{resource}_{operation}">
                    <div class="operation-left">
                        <div class="operation-title">{resource} > {operation}</div>
                        <div class="operation-url">
                            {method_str}
                            <div class="operation-url-path">/api/{resource}/{operation}{ '/{id}' if operation_obj["params"] else ''}</div>
                        </div>
                        <div class="operation-des">接口说明：{operation_obj["title"]}</div>
                        <div class="operation-role">
                            <span>接口权限：[</span>'''
            for  role in operation_obj["role"]:
                operations += f'''<span class="role">{role}</span>'''
            operations += '''<span>]</span>
                        </div>'''

            if operation_obj["params"]:
                operations += '''
                    <div class="operation-param-type">Url参数</div>
                            <table class="operation-param-table">
                                <thead>
                                <tr>
                                    <th>参数</th>
                                    <th>描述</th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr>
                                    <td>id</td>
                                    <td>主键ID</td>
                                </tr>
                                </tbody>
                            </table>'''

            if operation_obj["body"]:
                operation_body_data = ''
                for row in operation_obj["body"]:
                    operation_body_data += f'''
                            <tr>
                                <td>{row['name']}</td>
                                <td>{row['type']}</td>
                                <td>{row['desc']}</td>
                            </tr>
                    '''
                operations += f'''
                    <div class="operation-param-type">请求参数</div>
                        <table class="operation-param-table">
                            <thead>
                            <tr>
                                <th>参数</th>
                                <th>类型</th>
                                <th>描述</th>
                            </tr>
                            </thead>
                            <tbody>
                            {operation_body_data}
                            </tbody>
                        </table>
                '''

            right_text = ''
            for line in str(operation_obj["run"]).splitlines():
                right_text += f'''<div>{line}</div>'''

            operations += f'''
                    </div>
                    <div class="operation-right">
                        {right_text}
                        <div></div>
                    </div>
                </div>
            '''

    return  f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>接口文档</title>
    { style + script }
</head>
<body>
<div class="container">
    <div class="menu">
        <div class="menu-title">接口文档</div>
        <div class="menu-items">
            {menu_group}
        </div>
        <div class="menu-auth">
            <div class="auth-left">
                <div class="user-icon"></div>
                <div class="current">开发者</div>
            </div>
            <div class="user-add"></div>
        </div>
    </div>
    <div class="content">
        <div class="content-title">接口文档</div>
        {operations}
    </div>
</div>
</body>
</html>
'''

# endregion


def application(environ, star_response):
    request = Request()
    request.bind(environ, url_map)

    # region html请求
    if request.method == "GET" and (request.content_type == "text/plain" or request.content_type == "text/html"):
        if request.path == '/favicon.ico':
            file_path = 'static/favicon.ico'
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                star_response('404 Not Found', [('Content-Type', 'text/html')])
                return [''.encode('utf-8'), ]

            mimetype, encoding = mimetypes.guess_type(file_path)
            star_response('200 OK', [('Content-Type', mimetype)])
            return '' if request.method == 'HEAD' else open(file_path, 'rb')

        elif request.path == '/docs':
            star_response('200 OK', [('Content-Type', 'text/html')])
            return [doc_list().encode('utf-8')]

        elif str(request.path).startswith('/static/'):
            file_path = os.path.join("/static/", request.path).lstrip('/')
            if not os.path.exists(file_path) or not os.path.isfile(file_path):
                star_response('404 Not Found', [('Content-Type', 'text/html')])
                return [''.encode('utf-8'), ]

            mimetype, encoding = mimetypes.guess_type(file_path)
            star_response('200 OK', [('Content-Type', mimetype)])
            return '' if request.method == 'HEAD' else open(file_path, 'rb')
        else:
            if not request.path_resource or not request.path_operation:
                star_response('200 OK', [('Content-Type', 'text/html')])
                return ['''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Title</title></head><body>接口不存在</body></html>'''.encode('utf-8'), ]

            # star_response('200 OK', [('Content-Type', 'text/html')])
            # return ['''<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>Title</title></head><body>接口页面</body></html>'''.encode('utf-8'), ]

    # endregion

    # 资源
    path_resource = request.path_resource
    # 方法
    path_operation = request.path_operation
    # 参数
    path_param = request.path_param

    # region 接口权限判断
    permission = get_permission(path_resource, path_operation)

    permission_check = False

    if len(permission) == 0:
        star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
        response = json.dumps({"code": 403, "msg": "Permission Denied"}).encode('utf-8')
        return [response, ]

    if permission_check == False and "anymore" in permission:
        permission_check = True

    if permission_check == False and "all" in permission and request.user and request.user["id"]:
        permission_check = True

    permission_role = []
    permission_column = []
    for item in permission:
        if "__" in item:
            permission_column.append(item)
        else:
            permission_role.append(item)

    if permission_check == False and request.user["role"] in permission_role:
        permission_check = True

    if permission_check == False and len(permission_column) > 0 and path_param:
        permission_check_model = get_mapping_model(path_resource).get_or_none(get_mapping_model(path_resource).id == path_param)
        if not permission_check_model:
            star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
            response = json.dumps({"code": 404, "msg": "Not Found!"}).encode('utf-8')
            return [response, ]
        permission_check_model = permission_check_model.to_dict()
        for item in permission_column:
            user_column = item.split("__")[0]
            model_column = item.split("__")[1]
            if user_column in request.user and model_column in permission_check_model:
                if request.user[user_column] in permission_check_model[model_column]:
                    permission_check = True
                    break

    if not permission_check:
        star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
        response = json.dumps({"code": 403, "msg": "Permission Denied"}).encode('utf-8')
        return [response, ]
    # endregion

    # 请求地址 在url_map 中 已注册
    if path_resource in url_map and path_operation in url_map[path_resource]:
        if path_operation in url_map[path_resource]:
            func = url_map[path_resource][path_operation]

            if request.method not in func["method"]:
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                response = json.dumps({"code": 405, "msg": "Method Not Allowed!"}).encode('utf-8')
                return [response, ]

            handle = func["handle"]
            if path_param is not None:
                result = handle(request, path_param)
            else:
                result = handle(request)

            if type(result) == dict:
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                return [json.dumps(result).encode('utf-8'), ]
            elif type(result) == str:
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                return [result.encode('utf-8'), ]
            else:
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                return [result, ]
    elif path_resource == "file":
        # 文件接口
        if path_operation in APP_SETTING["file"]:
            if request.method != "POST":
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                response = json.dumps({"code": 405, "msg": "Method Not Allowed!"}).encode('utf-8')
                return [response, ]

            result = file_file(request, path_operation)

            star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
            response = json.dumps(result).encode('utf-8')
            return [response, ]
        else:
            star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
            response = json.dumps({"code": 404, "msg": "Not Found!"}).encode('utf-8')
            return [response, ]
    else:
        if path_operation in auto_config:
            if request.method != "POST":
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                response = json.dumps({"code": 405, "msg": "Method Not Allowed!"}).encode('utf-8')
                return [response, ]

            handle = auto_config[path_operation]

            if path_param is not None:
                result = handle(request, path_resource, path_param)
            else:
                result = handle(request, path_resource)

            if type(result) == dict:
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                return [json.dumps(result).encode('utf-8'), ]
            elif type(result) == str:
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                return [result.encode('utf-8'), ]
            else:
                star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
                return [result, ]
        else:
            star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])
            response = json.dumps({"code": 404, "msg": "Not Found!"}).encode('utf-8')
            return [response, ]


def route(resource, operation, method=['POST'], secret=None):
    def wrapper(handler):
        if resource not in url_map:
            url_map[resource] = {}

        url_map[resource][operation] = {
            "method": method,
            "handle": handler,
            "secret": secret
        }
        return handler

    return wrapper


def run(host='127.0.0.1', port=8000):
    '''
    启动监听服务
    '''
    httpd = make_server(host, port, application)
    print('服务已启动 ...')
    print('正在监听 http://%s:%d/' % (host, port))
    print('按 Ctrl-C 退出')
    print('')
    httpd.serve_forever()
