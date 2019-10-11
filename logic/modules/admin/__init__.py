from flask import Blueprint, session, redirect, request, url_for

# 创建蓝图
admin_blu = Blueprint("admin", __name__, url_prefix="/admin")

from . import views


@admin_blu.before_request
def check_admin():

    # 如果不是管理员,直接跳转到新闻首页
    is_admin = session.get("is_admin", False)
    # 如果不是管理员并且访问的url不是管理员登录页面
    if not is_admin and not request.url.endswith(url_for("admin.login")):
        return redirect("/")
