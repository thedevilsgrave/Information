from flask import request, abort, current_app, make_response, json, jsonify
from logic.tools.captcha.captcha import captcha
from logic.libs.yuntongxun.sms import CCP
from . import logter_blu
from logic import redis_store
from logic import constants
import re, random


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
        redis_store.set("imageCodeID_"+image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as err:
        current_app.logger.error(err)
        abort(500)
    # 5.把图片返回，并修改返回图片类型
    response = make_response(picture)
    response.headers["Content-Type"] = "image/jpg"
    return response


@logter_blu.route("/sms_code", method=["POST"])
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
    if not re.match('1[3589]//d{9}', mobile):
        return jsonify(errno="4105", errmsg="参数错误")

    # 3. 从redis中取出对应的图片验证码准确的内容
    try:
        real_code = redis_store.get("ImageCodeId"+image_code_id)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="4110", errmsg="图片验证码已过期")

    # 4. 与用户输入的验证码对比
    if real_code.upper() != image_code.upper():
        return jsonify(errno="4200", errmsg="验证码输入错误")

    # 5. 如果验证通过，生成短信验证码
    # 随机数字，并保证有6位数长度
    sms_code_str = "%06d" % random.randint(0, 99999)

    # 将验证码保存到redis中
    try:
        redis_store.set("SMS_"+mobile, sms_code_str, 300)
    except Exception as err:
        current_app.logger.error(err)
        return jsonify(errno="4008", errmsg="数据保存失败")

    # 6. 通过第三方平台将验证码发给用户，并告知发送结果
    result = CCP.send_template_sms('18799791353', [sms_code_str, 5], 1)
    if result != 0:
        return jsonify(errno="4003", errmsg="发送短信失败！")

    return jsonify(errno="2000", errmsg="发送成功！")

