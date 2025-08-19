# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-28 18:03:59
@LastEditTime: 2022-10-08 15:06:16
@LastEditors: HuangJianYi
:description: 主题皮肤
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.db_models.theme.theme_info_model import *
from seven_cloudapp.models.db_models.skin.skin_info_model import *

from seven_cloudapp_ppmt.models.db_models.act.act_info_model import *
from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *

from seven_cloudapp.handlers.server.theme_s import SkinListHandler


class ThemeListHandler(SevenBaseHandler):
    """
    :description: 主题列表
    """
    def get_async(self):
        """
        :description: 主题列表
        :param 
        :return: 列表
        :last_editors: HuangJianYi
        """
        app_id = self.get_app_id()
        where = "is_release=1"
        params = []
        power_menu_list = self.get_power_menu(app_id)
        if len(power_menu_list)>0:
            for i in power_menu_list:
                if i in ['322922329844087484', '500255366806462773', '-5761699449051843501']:
                    where += " and app_id=%s"
                    params.append(app_id)
                    break
        if len(params)<=0:
            where += " and app_id=''"
        dict_list = ThemeInfoModel(context=self).get_dict_list(where, params=params)

        for dict_info in dict_list:
            dict_info["client_json"] = self.json_loads(dict_info["client_json"]) if dict_info["client_json"] else {}
            dict_info["server_json"] = self.json_loads(dict_info["server_json"]) if dict_info["server_json"] else {}

        self.reponse_json_success(dict_list)


class ThemeUpdate(SevenBaseHandler):
    """
    :description: 小程序主题更新
    """
    @filter_check_params("act_id,theme_id")
    def get_async(self):
        """
        :description: 小程序主题更新
        :param act_id：活动id
        :param theme_id：主题id
        :return: 
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        act_id = self.get_param("act_id")
        theme_id = int(self.get_param("theme_id", 0))
        is_machine = int(self.get_param("is_machine", 1))

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity("id=%s", params=act_id)
        if not act_info:
            return self.reponse_json_error("NoAct", "对不起，找不到该活动")
        if act_info.theme_id == theme_id:
            return self.reponse_json_error("NoAct", "对不起，主题未改变")

        skin_info = SkinInfoModel(context=self).get_entity("theme_id=%s", params=theme_id)
        if not skin_info:
            return self.reponse_json_error("NoAct", "对不起，主题没有皮肤")

        act_info_model.update_table("theme_id=%s", "id=%s", [theme_id, act_id])

        if is_machine == 1:
            MachineInfoModel(context=self).update_table("skin_id=%s", "act_id=%s", [skin_info.id, act_id])

        self.reponse_json_success()