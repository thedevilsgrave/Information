from flask import render_template, g, redirect, request, jsonify
from logic.tools.common import user_login_data
from logic.modules.personal import user_blu
from logic.tools.image_storage import storage


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


@user_blu.route("/pic_info", methods=["POST", "GET"])
@user_login_data
def pic_info():
    user = g.user
    user_avatar_url = "http://oyucyko3w.bkt.clouddn.com/"
    if request.method == "GET":
        return render_template("news/user_pic_info.html", data={"user": user.to_dict()})
    #  如果是POST请求则修改头像
    # 1. 获取参数
    try:
        avatar = request.files.get("avatar").read()
    except Exception as err:
        return jsonify(errno="3500", errmsg="参数错误")

    # 2.上传头像
    try:
        # 使用自己封装的上传图片的方法
        key = storage(avatar)
    except Exception as err:
        return jsonify(errno="5666", errmsg="上传失败")

    # 3. 保存头像地址
    user.avatar_url = key

    return jsonify(errno="2000", errmsg="OK", data={"avatar_url": user_avatar_url+key})
