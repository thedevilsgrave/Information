from flask import render_template, g, redirect, request, jsonify
from logic.tools.common import user_login_data
from logic.modules.personal import user_blu


@user_blu.route("/info")
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect("/")
    data = {"user": user.to_dict()}
    return render_template("news/user.html", data=data)


@user_blu.route("/base_info", methods=["GET", "POST"])
@user_login_data
def base_info():
    user = g.user
    if not user:
        return redirect("/")

    # 不同的请求方式做不同的事
    if request.method == "GET":
        return render_template("news/user_base_info.html", data={"user": user.to_dict()})

    # 接收参数
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    # 判断参数
    if not all([nick_name, signature, gender]):
        return jsonify(errno="3500", errmsg="参数错误")
    if gender not in ("MAN", "WOMAN"):
        return jsonify(errno="3500", errmsg="参数错误")

    user.nick_name = nick_name
    user.gender = gender
    user.signature = signature

    return jsonify(errno="2000", errmsg="OK")
