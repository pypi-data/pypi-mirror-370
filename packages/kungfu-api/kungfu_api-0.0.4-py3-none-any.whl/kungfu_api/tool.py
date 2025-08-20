import argparse

import sys
import os
import shutil
sys.path.append(os.getcwd())

from .kungfu import db
try:
    from config.app_setting import APP_SETTING
    import models
except:
    APP_SETTING = {}
    models = None

from peewee_migrate import Router


def init():
    print("** 项目初始化中..")

    if not os.path.isdir("config"):
        os.makedirs("config")
        print("创建config文件夹")

    with open("config/__init__.py", 'w') as file:
        file.write("")
        print("创建config/__init__.py")

    with open("config/app_setting.py", 'w') as file:
        file.write("""# 全局配置

def request_process(r):
    return r
    

def response_process(r):
    return r


APP_SETTING = {
    # 数据库链接
    "db": {
        "host": "127.0.0.1",
        "port": 3306,
        "user": "",
        "passwd": "",
        "database": "",
        "charset": "utf8mb4"
    },
    # jwt 配置
    "jwt": {
        # jwt中 包含的用户列, 至少包含["id", "username", "name", "role"]，可以按需增加其他列
        "column": ["id", "username", "name", "role"],
        # jwt加密解密使用的密钥串
        "secret": "123!@#"
    },
    "file": {
        # 配置文件上传接口 可以上传的文件类型，调用方式：/api/file/image, /api/file/video
        "image": ["jpg", "jpeg", "bmp", "gif", "png"],
        "video": ["mp4"]
    },
    "request_process": request_process,
    "response_process": response_process
}
""")
        print("创建config/app_setting.py")

    with open("config/permission_setting.py", 'w') as file:
        file.write("""# anymore 所有用户，包含匿名用户
# all 所有用户（登录）
# 角色
# 用户字段__表字段
# 例1（只有负责人才能调用接口）：id__master_id 如果用户的id在资源的master_id中，则有权限
# 例2（只有特定组织的用户可以调用接口）：org_id__org_id 如果用户的org_id在资源的org_id中，则有权限

# 权限配置
API_PERMISSION = {
    # 未配置资源接口权限时，使用以下默认权限
    "__default": {
        "list": ["anymore"],
        "get": ["anymore"],
        "post": ["anymore"],
        "put": ["anymore"],
        "delete": ["anymore"],
        "drop": ["anymore"],
        "__other": ["anymore"]
    },
    # 文件接口权限
    "file": {
        "image": ["anymore"],
        "video": ["anymore"]
    },
    "users": {
        "login": ["anymore"]
    }
}
""")
        print("创建config/permission_setting.py")

    with open("config/template_setting.py", 'w') as file:
        file.write("""SQL_TEMPLATE = {
    "my_order": "select * from a left join b on b.xxx = '{xxx}' where a.is_del = 0"
}
""")
        print("创建config/template_setting.py")

    if not os.path.isdir("views"):
        os.makedirs("views")
        print("创建views文件夹")

    with open("views/__init__.py", 'w') as file:
        file.write("""from .users_view import *
""")
        print("创建views/__init__.py")

    with open("views/users_view.py", 'w') as file:
        file.write("""from kungfu_api import route
from kungfu_api import jwt_encode
from models import Users


@route('users', 'login', ["POST"])
def users_login(request):
    \"\"\"
    用户登录
    参数：
    username: 用户名
    password: 密码
    返回:
    id: 用户ID
    name: 姓名、昵称
    username: 用户名、登录名
    role: 用户角色
    token: 登录成功后返回的token

    curl 调用示例：
    curl -X POST -H "Content-Type: application/json" -d '{"username":Your Value,"password": Your Value}' http://127.0.0.1:8000/api/users/login
    \"\"\"

    username = request.data.get('username', '')
    password = request.data.get('password', '')

    if not username:
        return {"code": 400, "msg": "请输入用户名!"}

    if not password:
        return {"code": 400, "msg": "请输入密码!"}

    user = Users.get_or_none(Users.username == username)
    if not user:
        return {"code": 400, "msg": "用户名或密码错误!"}

    if user and user.verify_password(password):
        token = jwt_encode(user)
        return {
            "code": 200,
            "msg": "登录成功!",
            "data": {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "role": user.role,
                "token": token
            }
        }
    else:
        return {"code": 400, "msg": "用户名或密码错误!"}

""")
        print("创建views/users_view.py")

    with open("app.py", 'w') as file:
        file.write("""from kungfu_api import route, run, application

from views import *


if __name__ == '__main__':
    run(host='127.0.0.1', port=8000)
""")
        print("创建app.py")

    with open("models.py", 'w') as file:
        file.write("""import hashlib
from peewee import *
from kungfu_api.db import BaseModel


class Users(BaseModel):
    \"\"\"用户\"\"\"
    username = CharField(max_length=128, unique=True, index=True, help_text="用户名、登录名")
    _password = CharField(max_length=128, help_text="加密密码")
    name = CharField(max_length=100, help_text="姓名、昵称")
    role = CharField(max_length=50, help_text="角色")

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        # 建议加入混淆字符串，防止md5碰撞
        self._password = hashlib.md5(password.encode(encoding='utf-8')).hexdigest()

    def verify_password(self, password):
        # 建议加入混淆字符串，防止md5碰撞
        return hashlib.md5(password.encode(encoding='utf-8')).hexdigest() == self._password

    class Meta:
        # 指定数据库表名和接口资源名称，如果不写默认为实体类名小写
        db_table = 'users'


# 模型和接口的映射配置，键需要和表名一致
# 默认生成全部接口['list', 'get', 'post', 'put', 'delete', 'drop']，
# 如果不需要全部接口，可以在下面配置,如：'table1': (Table1, ['list', 'get'])
MODEL_API_SETTING = {
    "users": (Users, [])
}
""")
        print("创建models.py")

    print("** 项目初始化完成...")


def migrate():
    print("** 数据库同步中...")

    db.connect()

    router = Router(db, ignore="basemodel")
    router.create(auto=models)
    router.run()

    db.close()

    print("** 数据库同步完成...")


def user():
    print("** 正在创建用户，请输入用户信息...")
    username = input("请输入账号(登录名)*：")
    password = input("请输入密码*：")
    name = input("请输入用户名(姓名)*：")
    role = input("请输入角色*：")

    try:
        model = models.Users.create(**{
            "username": username,
            "password": password,
            "name": name,
            "role": role,
        })
        print("** 创建用户成功...")
    except Exception as e:
        print(e)
        print("** 创建用户失败...")


def main():
    parser = argparse.ArgumentParser()
    # parser.add_argument("-f", help="")
    parser.add_argument("exec", help="参数: [init, migrate, user]")

    # 解析
    args = parser.parse_args()
    exec = args.exec

    if exec == "init":
        init()
    elif exec == "migrate":
        migrate()
    elif exec == "user":
        user()
    else:
        print("参数错误")


if __name__ == '__main__':
    main()
