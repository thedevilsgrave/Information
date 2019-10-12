from datetime import datetime

from flask import render_template, request, redirect, current_app, session, url_for, g
from logic.models import User
from logic.modules.admin import admin_blu
from logic.tools.common import user_login_data
import time


@admin_blu.route("/login", methods=["POST", "GET"])
def login():
    """管理员用户登录页"""
    if request.method == "GET":

        # 判断用户是否已登录,如果已经登录,则直接跳转到管理员首页
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)

        if user_id and is_admin:
            return render_template("admin/index.html")

        return render_template("admin/login.html")

    # 取到表单的参数
    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template("admin/login.html", errmsg="参数错误")

    try:
        user = User.query.filter(User.mobile == username, User.is_admin == True).first()
    except Exception as err:
        current_app.logger.error(err)
        return render_template("admin/login.html", errmsg="数据查询失败")

    if not user:
        return render_template("admin/login.html", errmsg="未查询到用户信息")

    if not user.check_passowrd(password):
        return render_template("admin/login.html", errmsg="用户名或密码错误")

    # 3. 保存用户登录状态
    session["user_id"] = user.id
    session["user_phone"] = user.mobile
    session["user_name"] = user.nick_name
    session["is_admin"] = user.is_admin

    # 登录成功后跳转页面
    return redirect(url_for("admin.index"))


@admin_blu.route("/index")
@user_login_data
def index():
    """管理员主页显示"""
    user = g.user
    if not user:
        return redirect("admin.login")

    return render_template("admin/index.html", data=user.to_dict())


@admin_blu.route("/user_count")
@user_login_data
def user_count():
    user = g.user

    user_total = 0
    # 用户总数
    try:
        user_total = User.query.filter(User.is_admin==False).count()
    except Exception as err:
        current_app.logger.error(err)

    # 月新增数
    mouth_total = 0
    t = time.localtime()
    begin_mon_time = datetime.strptime(("%d-%02d-01" % (t.tm_year, t.tm_mon)), "%Y-%m-%d")
    try:
        mouth_total = User.query.filter(User.is_admin==False, User.create_time > begin_mon_time).count()
    except Exception as err:
        current_app.logger.error(err)

    # 日新增数
    begin_day_time = datetime.strptime(("%d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    day_total = 0
    try:
        day_total = User.query.filter(User.is_admin==False, User.create_time > begin_day_time).count()
    except Exception as err:
        current_app.logger.error(err)

    data = {
        "user_total": user_total,
        "mouth_total": mouth_total,
        "day_total": day_total
    }
    return render_template("admin/user_count.html", data=data)
