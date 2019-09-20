from flask import request, abort, current_app, make_response, json, jsonify, session
from logic.tools.captcha.captcha import captcha
from logic.libs.yuntongxun.sms import CCP
from . import logter_blu
from logic import redis_store
from logic import constants
import re, random
from logic.models import *


@logter_blu.route("/image_code")
def get_image_code():
    """生成图片验证吗并返回"""
    # 1.取到请求发过来带的参数
    image_code_id = request.args.get("imageCodeID", None)
    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3.生成图片验证码
    name, text, picture = captcha.generate_captcha()
    # 4.保存图片验证码和带过来的参数到redis
    try:
        redis_store.setex("imageCodeID_"+image_code_id, 300, text)
    except Exception as err:
        current_app.logger.error(err)
        abort(500)
    # 5.把图片返回，并修改返回图片类型
    response = make_response(picture)
    response.headers["Content-Type"] = "image/jpg"
    return response


@logter_blu.route("/sms_code", methods=["POST"])
def send_sms_code():
    """发送短信验证码并返回"""
    # 1. 接收浏览器请求过来的参数：手机号，图片验证码编号，用户输入的图片验证码的内容

    # 将请求过来的json格式数据转换成字典格式
    parameter_dict = request.json
    mobile = parameter_dict.get("mobile")
    image_code = parameter_dict.get("image_code")
    image_code_id = parameter_dict.get("image_code_id")

    # 2. 验证参数是否符合规则，判断是否有值
    if not all([mobile, image_code, image_code_id]):
        return jsonify(errno="4100", errmsg="参数错误")
    # 校验手机号是否输入正确
    if not re.match("^1[3578][0-9]{9}$", mobile):
        return jsonify(errno="4105", errmsg="参数错误")

    # 3. 从redis中取出对应的图片验证码准确的内容
    try:
        real_code = redis_store.get("imageCodeID_"+image_code_id)
    except Exception as err:
        current_app.logger.error(err)

    # 判断验证码是否已过期
    if not real_code:
        return jsonify(errno="4110", errmsg="图片验证码已过期")

    # 4. 与用户输入的验证码对比
    if real_code.lower() != image_code.lower():
        return jsonify(errno="4200", errmsg="验证码输入错误")

    # 5. 如果验证通过，生成短信验证码
    # 随机数字，并保证有6位数长度
    sms_code_str = "%06d" % random.randint(0, 99999)
    current_app.logger.debug("短信验证码的内容是 %s" % sms_code_str)

    # 将验证码保存到redis中
    try:
        redis_store.set("SMS_"+mobile, sms_code_str, 300)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="4008", errmsg="数据保存失败")

    # 6. 通过第三方平台将验证码发给用户，并告知发送结果
    # result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")
    # if result != 0:
    #     return jsonify(errno="4003", errmsg="发送短信失败！")

    return jsonify(errno="2000", errmsg="发送成功！")


@logter_blu.route("/register", methods=["POST"])
def register():
    """注册逻辑"""

    # 1. 获取参数
    parameter_dict = request.json
    mobile = parameter_dict.get("mobile")
    smscode = parameter_dict.get("smscode")
    password = parameter_dict.get("password")

    # 2. 校验参数
    if not all([mobile, smscode, password]):
        return jsonify(errno="4100", errmsg="参数错误")

    # 3. 获取数据库中保存的短信验证码
    try:
        real_sms_code = redis_store.get("SMS_"+mobile)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="4005", errmsg="数据查询失败")
    if not real_sms_code:
        return jsonify(errno="4110", errmsg="图片验证码已过期")

    # 4. 校验验证码
    if real_sms_code != smscode:
        return jsonify(errno="4200", errmsg="验证码输入错误")

    # 5. 初始化用户模型，并赋值
    user = User()
    user.mobile = mobile
    user.last_login = datetime.now()
    # 对密码做处理
    user.password = password

    # 用户昵称默认为手机号
    user.nick_name = mobile

    # 6. 将用户模型添加到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as err:
        current_app.logger.error(err)
        db.session.rollback()
        return jsonify(errno="4008", errmsg="数据保存失败")
    # 注册成功后自动登录
    session["user_id"] = user.id
    session["user_phone"] = user.mobile
    session["user_name"] = user.nick_name

    # 7. 返回响应
    return jsonify(errno="2000", errmsg="注册成功！")

