from flask import render_template, request, redirect, current_app, session, url_for
from logic.models import User
from logic.modules.admin import admin_blu


@admin_blu.route("/login", methods=["POST", "GET"])
def login():
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
def index():
    return render_template("admin/index.html")
