import logging
from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from redis import StrictRedis

from config import config_dict

db = SQLAlchemy()
redis_store = None


def setup_log(config_name):
    # 设置日志的记录等级
    logging.basicConfig(level=config_dict[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """创建不同的app方法"""
    # 配置日志，并传入配置名字一遍能获得对应配置的日志等级
    setup_log(config_name)
    app = Flask(__name__)
    app.config.from_object(config_dict[config_name])
    # 初始化Mysql数据库对象
    db.init_app(app)
    # 初始化Redis数据库对象
    # 声明redis_store为全局变量
    global redis_store
    redis_store = StrictRedis(host=config_dict[config_name].REDIS_HOST,
                              port=config_dict[config_name].REDIS_PORT,
                              decode_responses=True)

    # 开启CSRF保护
    # 它已经帮我们做好了:从cookie中取出随机值,从表单中取出随机值,和校验的功能
    # 我们需要做:  设置cookie中的随机值,设置表单中的随机值
    CSRFProtect(app)

    @app.after_request
    def after_request(response):
        # 在返回响应之前可以设置csrf_token
        csrf_token = generate_csrf()
        response.set_cookie("csrf_token", csrf_token)
        return response
        # 然而我们不是使用的表单提交,而是使用ajax提交
        # 所以需要在ajax请求时带上csrf_token

    # 设置 指定session保存位置
    Session(app)
    # 注册蓝图
    from logic.modules.index import index_blu
    app.register_blueprint(index_blu)

    from logic.modules.logter import logter_blu
    app.register_blueprint(logter_blu)

    return app
