# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-06-02 11:08:39
@LastEditTime: 2024-03-12 16:21:50
@LastEditors: HuangJianYi
:description: App相关
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.handlers.server.app_s import TelephoneHandler
from seven_cloudapp.handlers.server.app_s import AppUpdateHandler
from seven_cloudapp.handlers.server.app_s import AppInfoHandler

from seven_cloudapp.models.db_models.base.base_info_model import *
from seven_cloudapp.models.db_models.app.app_info_model import *

from seven_cloudapp_ppmt.models.db_models.cms.cms_info_model import *

#从Python SDK导入SMS配置管理模块以及安全认证模块
from baidubce.bce_client_configuration import BceClientConfiguration
from baidubce.auth.bce_credentials import BceCredentials
import baidubce.services.sms.sms_client as sms
import baidubce.exception as ex

class BaseInfoHandler(SevenBaseHandler):
    """
    :description: 基础信息处理
    """
    def get_async(self):
        """
        :description: 基础信息获取
        :param 
        :return: dict
        :last_editors: HuangJianYi
        """
        base_info = BaseInfoModel(context=self).get_entity()
        if not base_info:
            return self.reponse_json_error("BaseInfoError", "基础信息出错")

        # 左上角信息
        info = {}
        info["company"] = "天志互联"
        info["miniappName"] = base_info.product_name
        info["logo"] = base_info.product_icon

        # 左边菜单
        menu_list = []
        menu = {}
        menu["name"] = "创建活动"
        menu["key"] = "create_action"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "活动管理"
        menu["key"] = "act_manage"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "装修教程"
        menu["key"] = "decoration_poster"
        menu_list.append(menu)
        menu = {}
        menu["name"] = "版本更新"
        menu["key"] = "update_ver"
        menu_list.append(menu)

        # 左边底部菜单
        bottom_button_list = []
        bottom_button = {}
        bottom_button["title"] = "发票管理"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "billManage"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "配置教程"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "use_teaching"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "联系旺旺"
        bottom_button["handling_event"] = "outtarget"
        bottom_button["event_name"] = "http://amos.alicdn.com/getcid.aw?v=2&uid=%E5%A4%A9%E5%BF%97%E4%BA%92%E8%81%94&site=cntaobao&s=1&groupid=0&charset=utf-8"
        bottom_button_list.append(bottom_button)
        bottom_button = {}
        bottom_button["title"] = "号码绑定"
        bottom_button["handling_event"] = "popup"
        bottom_button["event_name"] = "bind_phone"
        bottom_button_list.append(bottom_button)

        # 右边使用指引
        use_point_list = []
        use_point = {}
        use_point["index"] = "1"
        use_point["title"] = "创建活动并配置完成"
        use_point_list.append(use_point)
        use_point = {}
        use_point["index"] = "2"
        use_point["title"] = "将淘宝小程序装修至店铺"
        use_point_list.append(use_point)
        use_point = {}
        use_point["index"] = "3"
        use_point["title"] = "正式运营淘宝小程序"
        use_point_list.append(use_point)

        default_box_style = {}
        default_box_style["title"] = "默认模板"
        default_box_style["pic_url"] = "https://isv.alibabausercontent.com/00000000/imgextra/i3/2206353354303/O1CN016E9TQD1heotGpXFkW_!!2206353354303-2-isvtu-00000000.png"

        helper_info = {}
        helper_info["phone"] = ""

        data = {}
        data["serverName"] = "在线拆盲盒模板"
        data["info"] = info
        data["menu"] = menu_list
        data["bottom_button"] = bottom_button_list
        data["use_point"] = use_point_list
        data["default_box_style"] = default_box_style
        store_user_nick = self.get_taobao_param().user_nick.split(':')[0]
        if store_user_nick:
            app_info_model = AppInfoModel(context=self)
            app_info = app_info_model.get_entity("store_user_nick=%s", params=store_user_nick)
            if app_info:
                helper_info["phone"] = app_info.app_telephone
        data["helper_info"] = helper_info
        if base_info:
            # 把string转成数组对象
            base_info.update_function = self.json_loads(base_info.update_function) if base_info.update_function else []
            base_info.price_gare = self.json_loads(base_info.price_gare) if base_info.price_gare else []
            base_info.product_price = self.json_loads(base_info.product_price) if base_info.product_price else []
            base_info.decoration_poster = self.json_loads(base_info.decoration_poster) if base_info.decoration_poster else []
            base_info.friend_link = self.json_loads(base_info.friend_link) if base_info.friend_link else []
            base_info.menu_config = self.json_loads(base_info.menu_config) if base_info.menu_config else []
            #指定账号升级
            user_nick = self.get_taobao_param().user_nick
            if user_nick:
                if user_nick == config.get_value("test_user_nick"):
                    base_info.client_ver = config.get_value("test_client_ver")
                    base_info.update_function = []
            base_info_dict = base_info.__dict__
            base_info_dict["is_force_phone"] = True if base_info.is_force_phone else config.get_value("is_force_phone",True)
            data["base_info"] = base_info_dict

        if base_info:
            return self.reponse_json_success(data)

        return self.reponse_json_error("BaseInfoError", "基础信息出错")


class CheckGmPowerHandler(SevenBaseHandler):
    """
    :description: 校验是否有GM工具权限
    """
    def get_async(self):
        """
        :description: 校验是否有GM工具权限
        :param 
        :return: True是 False否
        :last_editors: HuangJianYi
        """
        is_power = False
        store_user_nick = self.get_taobao_param().user_nick.split(':')[0]
        if not store_user_nick:
            return self.reponse_json_success(is_power)
        app_info = AppInfoModel(context=self).get_entity("store_user_nick=%s", params=store_user_nick)
        if not app_info:
            is_power = False
        else:
            if app_info.is_custom == 1:
                is_power = True
        return self.reponse_json_success(is_power)


class GetAppidByGmHandler(SevenBaseHandler):
    """
    :description: 获取应用标识
    """
    @filter_check_params("store_name")
    def get_async(self):
        """
        :description: 获取应用标识
        :param store_name:店铺名称
        :return app_id
        :last_editors: HuangJianYi
        """
        app_id = ""
        store_name = self.get_param("store_name")
        store_user_nick = self.get_taobao_param().user_nick.split(':')[0]
        if not store_user_nick:
            return self.reponse_json_success(app_id)
        is_power = False
        app_info = AppInfoModel(context=self).get_entity("store_user_nick=%s", params=store_user_nick)
        if app_info and app_info.is_custom == 1:
            is_power = True
        if is_power == True:
            app_info_dict = AppInfoModel(context=self).get_dict("store_name=%s", field="app_id", params=[store_name])
            if app_info_dict:
                app_id = app_info_dict["app_id"]
        return self.reponse_json_success(app_id)


class SendSmsHandler(SevenBaseHandler):
    """
    :description: 发送短信
    """
    def get_async(self):
        """
        :description: 发送短信
        :param telephone：电话号码
        :return 
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        telephone = self.get_param("telephone")
        result_code = str(random.randint(100000, 999999))
        #设置SmsClient的Host，Access Key ID和Secret Access Key
        sms_bce_config = config.get_value("sms_bce_config",{"host":"","ak":"","sk":"","signature_id":"","template_id":""})
        sms_config = BceClientConfiguration(credentials=BceCredentials(sms_bce_config["ak"], sms_bce_config["sk"]), endpoint=sms_bce_config["host"])
        #新建SmsClient
        sms_client = sms.SmsClient(sms_config)
        try:
            response = sms_client.send_message(signature_id=sms_bce_config["signature_id"], template_id=sms_bce_config["template_id"], mobile=telephone, content_var_dict={'code': result_code, 'time': '30'})
            #记录验证码
            self.redis_init().set("user_" + open_id + "_bind_phone_code", result_code, ex=300)
            return self.reponse_json_success()
        except ex.BceHttpClientError as e:
            if isinstance(e.last_error, ex.BceServerError):
                self.logger_error.error(f"发送短信失败。Response:{e.last_error.status_code},code:{e.last_error.code},request_id:{e.last_error.request_id}")
            else:
                self.logger_error.error(f"发送短信失败。Unknown exception:{e}")
            return self.reponse_json_error("error","发送失败")


class LeftAdListHandler(SevenBaseHandler):
    """
    @description: 左侧广告
    @param {*} self
    @return {*}
    @last_editors: HuangJianYi
    """
    def get_async(self):
        cms_info_model = CmsInfoModel(context=self.context)
        page_list, total = cms_info_model.get_dict_page_list(field="id,place_id,target_url,min_pic", page_index=0, page_size=1, where="place_id=1 and is_release=1", group_by="", order_by="id desc", params=[])
        return self.response_json_success(page_list)
