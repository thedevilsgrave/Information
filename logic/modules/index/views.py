from flask import render_template, current_app

from . import index_blu
from logic import redis_store


@index_blu.route('/')
def index():
    # session["name"] = "lishu"
    # # 测试log日志
    # logging.debug('测试用的debug')
    # logging.error('测试用的error')
    # logging.warning('测试用的warning')
    return render_template("news/index.html")


@index_blu.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("news/favicon.ico")
