# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2021-04-14 15:51:04
@LastEditTime: 2022-02-24 17:34:21
@LastEditors: HuangJianYi
:Description: 用户权限相关
"""
from seven_cloudapp.handlers.seven_base import *
from seven_cloudapp_ppmt.models.power_base_model import *


class GetPowerMenuHandler(SevenBaseHandler):
    """
    :description: 获取权限菜单列表
    """
    @filter_check_params("app_id")
    def get_async(self):
        """
        :description: 获取权限菜单列表
        :return: dict
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")

        data = self.get_power_menu(app_id)

        return self.reponse_json_success(data)


class GetHighPowerListHandler(SevenBaseHandler):
    """
    :description: 商家权限配置处理
    """
    def get_async(self):
        """
        :description: 获取商家权限配置
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        user_nick = self.get_taobao_param().user_nick
        if not user_nick:
            return self.reponse_json_error("Error", "对不起,请先授权登录")
        store_user_nick = user_nick.split(':')[0]
        power_base_model = PowerBaseModel(context=self)
        app_key, app_secret = self.get_app_key_secret()
        self.reponse_json_success(power_base_model.get_server_config_data(store_user_nick, self.get_taobao_param().access_token, app_key, app_secret))
