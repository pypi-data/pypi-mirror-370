# -*- coding: utf-8 -*-
"""
:Author: 投放相关
:Date: 2020-06-01 14:07:23
:LastEditTime: 2021-04-15 15:22:28
:LastEditors: HuangJingCan
:description: 投放相关
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.throw_model import *
from seven_cloudapp.models.seven_model import PageInfo

from seven_cloudapp.handlers.server.throw_s import InitThrowGoodsCallBackHandler
from seven_cloudapp.handlers.server.throw_s import SaveThrowGoodsStatusHandler
from seven_cloudapp.handlers.server.throw_s import ThrowGoodsListHandler
from seven_cloudapp.handlers.server.throw_s import AsyncThrowGoodsHandler

from seven_cloudapp.models.db_models.price.price_gear_model import *
from seven_cloudapp.models.db_models.throw.throw_goods_model import *

from seven_cloudapp_ppmt.models.db_models.act.act_info_model import *


class InitThrowGoodsListHandler(SevenBaseHandler):
    """
    :description: 初始化活动投放
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 初始化活动投放
        :param act_id:活动id
        :param app_id:app_id
        :return 
        :last_editors: HuangJingCan
        """
        app_id = self.get_param("app_id")
        act_id = int(self.get_param("act_id", 0))

        act_info = ActInfoModel(context=self).get_dict_by_id(act_id)

        if not act_info:
            return self.reponse_json_error("NoAct", "对不起，活动不存在")

        gear_goods_id_list = PriceGearModel(context=self).get_dict_list("act_id=%s and goods_id!='' and is_del=0", field="goods_id", params=act_id)
        goods_id_list = []

        if len(gear_goods_id_list) > 0:
            goods_id_list += [int(goods_id["goods_id"]) for goods_id in gear_goods_id_list]

        goods_id_list = list(set(goods_id_list))
        online_url = self.get_online_url(act_id, app_id)
        if len(goods_id_list) == 0:
            result_data = {"url": online_url, "act_name": act_info["act_name"], "goods_list": []}
            return self.reponse_json_success(result_data)

        result_data = ThrowModel(context=self).init_throw_goods_list(act_id, app_id, act_info["act_name"], online_url, goods_id_list, self.get_now_datetime())

        return self.reponse_json_success(result_data)