# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-06-02 13:44:17
@LastEditTime: 2023-11-01 15:20:57
@LastEditors: HuangJianYi
:description: 奖品相关
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.enum import OperationType
from seven_cloudapp.models.seven_model import PageInfo

from seven_cloudapp.handlers.server.prize_s import PrizeDelHandler
from seven_cloudapp.handlers.server.prize_s import PrizeReleaseHandler

from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *
from seven_cloudapp_ppmt.models.db_models.act.act_prize_model import *


class PrizeListHandler(SevenBaseHandler):
    """
    :description: 奖品列表
    """
    @filter_check_params("machine_id")
    def get_async(self):
        """
        :description: 奖品列表
        :param act_id:活动id
        :param page_index:页索引
        :param page_size:页大小
        :param machine_id:机台id
        :return: 
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))
        machine_id = int(self.get_param("machine_id", 0))

        condition = "machine_id=%s"
        if machine_id <= 0:
            return self.reponse_json_error_params()

        act_prize_model = ActPrizeModel(context=self)
        machine_info_model = MachineInfoModel(context=self)

        # 奖品总件数
        prize_all_count = act_prize_model.get_total("machine_id=%s", params=machine_id)
        # 库存不足奖品件数
        prize_surplus_count = act_prize_model.get_total("machine_id=%s AND prize_total=0", params=machine_id)
        # 可被抽中奖品件数
        prize_lottery_count = act_prize_model.get_total("machine_id=%s AND probability>0 AND prize_total>0 AND is_release=1", params=machine_id)
        #奖品总权重
        sum_probability = act_prize_model.get_dict("machine_id=%s and is_release=1", field="sum(probability) as probability", params=machine_id)

        #开启端盒提示信息
        machine_info = machine_info_model.get_entity_by_id(machine_id)
        lottery_hidden_prize_tip = ""
        lottery_buy_endbox_tip = ""
        if machine_info and machine_info.is_release == 1 and machine_info.is_buy_endbox == 1:
            lottery_buy_endbox_prize_count = act_prize_model.get_total("machine_id=%s", params=machine_id)
            if lottery_buy_endbox_prize_count < machine_info.specs_type:
                lottery_buy_endbox_tip = "本中盒已开启端盒购买功能,但奖品池中商品总件数<端盒规格数，用户购买端盒时将提示库存不足，请调整奖品配置"
            lottery_hidden_prize_count = act_prize_model.get_total("machine_id=%s AND tag_id in(2,3)", params=machine_id)
            lottery_common_prize_count = act_prize_model.get_total("machine_id=%s AND tag_id=1", params=machine_id)
            if lottery_hidden_prize_count > 0 and lottery_common_prize_count < machine_info.specs_type:
                lottery_hidden_prize_tip = "本中盒存在隐藏款盲盒,且普通款奖品件数＜端盒规格数,用户购买整套端盒必中隐藏款,请调整商品配置"

        page_list, total = act_prize_model.get_dict_page_list("*", page_index, page_size, condition, "", "sort_index desc", params=machine_id)

        for i in range(len(page_list)):
            # page_list[i]["prize_detail"] = self.json_loads(page_list[i]["prize_detail"])
            if page_list[i]["goods_code_list"] == "":
                page_list[i]["goods_code_list"] = "[]"
            page_list[i]["goods_code_list"] = self.json_loads(page_list[i]["goods_code_list"])

        page_info = PageInfo(page_index, page_size, total, page_list)
        page_info.prize_all_count = prize_all_count
        page_info.prize_surplus_count = prize_surplus_count
        page_info.prize_lottery_count = prize_lottery_count
        page_info.lottery_buy_endbox_tip = lottery_buy_endbox_tip
        page_info.lottery_hidden_prize_tip = lottery_hidden_prize_tip
        if sum_probability["probability"]:
            page_info.prize_sum_probability = int(sum_probability["probability"])
        else:
            page_info.prize_sum_probability = 0

        return self.reponse_json_success(page_info)


class PrizeHandler(SevenBaseHandler):
    """
    :description: 奖品保存
    """
    @filter_check_params("app_id,act_id,machine_id")
    def post_async(self):
        """
        :description: 奖品保存
        :param prize_id：奖品id
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        prize_id = int(self.get_param("prize_id", 0))
        machine_id = int(self.get_param("machine_id", 0))
        prize_type = int(self.get_param("prize_type", 0))
        tag_id = int(self.get_param("tag_id", 1))
        sort_index = int(self.get_param("sort_index", 0))
        prize_pic = self.get_param("prize_pic")
        unpack_pic = self.get_param("unpack_pic")
        toys_pic = self.get_param("toys_pic")
        prize_name = self.get_param("prize_name")
        prize_price = self.get_param("prize_price")
        surplus = int(self.get_param("surplus", 0))
        prize_total = int(self.get_param("prize_total", 0))
        is_surplus = int(self.get_param("is_surplus", 0))
        probability = int(self.get_param("probability", 0))
        prize_limit = int(self.get_param("prize_limit", 0))
        prize_detail = self.get_param("prize_detail")
        is_release = int(self.get_param("is_release", 1))
        is_prize_notice = int(self.get_param("is_prize_notice", 1))
        is_sku = int(self.get_param("is_sku", 0))
        goods_id = int(self.get_param("goods_id", 0))
        goods_code = self.get_param("goods_code")
        goods_code_list = self.get_param("goods_code_list")
        app_id = self.get_param("app_id")
        owner_open_id = self.get_param("owner_open_id")

        if act_id <= 0:
            return self.reponse_json_error_params()

        act_prize_model = ActPrizeModel(context=self)
        act_prize = None
        old_act_prize = None
        if prize_id > 0:
            act_prize = act_prize_model.get_entity_by_id(prize_id)

        if not act_prize:
            act_prize = ActPrize()
        else:
            old_act_prize = deepcopy(act_prize)

        act_prize.act_id = act_id
        act_prize.app_id = app_id
        act_prize.owner_open_id = owner_open_id
        act_prize.machine_id = machine_id
        act_prize.prize_type = prize_type
        act_prize.tag_id = tag_id
        act_prize.sort_index = sort_index
        act_prize.prize_pic = prize_pic if prize_pic != "" else unpack_pic
        act_prize.unpack_pic = unpack_pic
        act_prize.toys_pic = toys_pic
        act_prize.prize_name = prize_name
        act_prize.prize_price = prize_price
        act_prize.is_surplus = is_surplus
        act_prize.probability = probability
        act_prize.prize_limit = prize_limit
        act_prize.prize_detail = prize_detail if prize_detail != "" else json.dumps([])
        act_prize.modify_date = self.get_now_datetime()
        act_prize.is_release = is_release
        act_prize.is_prize_notice = is_prize_notice
        act_prize.is_sku = is_sku
        act_prize.goods_id = goods_id
        act_prize.goods_code = goods_code
        act_prize.goods_code_list = goods_code_list

        if prize_id > 0:
            act_prize_model.update_entity(act_prize, exclude_field_list=["prize_total","surplus","hand_out"])
            self.create_operation_log(OperationType.update.value, act_prize.__str__(), "PrizeHandler", old_act_prize, act_prize)
            if surplus == 0:
                operate_num = prize_total - act_prize.prize_total
            else:
                operate_num = surplus
            try:
                act_prize_model.update_table(f"surplus=surplus+{operate_num},prize_total=prize_total+{operate_num}", "id=%s", act_prize.id)
            except Exception as ex:
                self.logging_link_error("保存奖品异常:" + str(ex))
                return self.reponse_json_error("error", "保存失败,请调整库存")
        else:
            act_prize.create_date = act_prize.modify_date
            act_prize.surplus = surplus if surplus > 0 else prize_total
            act_prize.prize_total = prize_total
            act_prize.id = act_prize_model.add_entity(act_prize)
            self.create_operation_log(OperationType.add.value, act_prize.__str__(), "PrizeHandler", None, act_prize)

        return self.reponse_json_success(act_prize.id)

    @filter_check_params("app_id,act_id,machine_id")
    def get_async(self):
        """
        :description: 奖品保存
        :param prize_id：奖品id
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        prize_id = int(self.get_param("prize_id", 0))
        machine_id = int(self.get_param("machine_id", 0))
        prize_type = int(self.get_param("prize_type", 0))
        tag_id = int(self.get_param("tag_id", 0))
        sort_index = int(self.get_param("sort_index", 0))
        prize_pic = self.get_param("prize_pic")
        unpack_pic = self.get_param("unpack_pic")
        toys_pic = self.get_param("toys_pic")
        prize_name = self.get_param("prize_name")
        prize_price = self.get_param("prize_price")
        surplus = int(self.get_param("surplus", 0))
        prize_total = int(self.get_param("prize_total", 0))
        is_surplus = int(self.get_param("is_surplus", 0))
        probability = int(self.get_param("probability", 0))
        prize_limit = int(self.get_param("prize_limit", 0))
        prize_detail = self.get_param("prize_detail")
        is_release = int(self.get_param("is_release", 1))
        is_sku = int(self.get_param("is_sku", 0))
        goods_id = int(self.get_param("goods_id", 0))
        goods_code = self.get_param("goods_code")
        goods_code_list = self.get_param("goods_code_list")
        app_id = self.get_param("app_id")
        owner_open_id = self.get_param("owner_open_id")

        if act_id <= 0:
            return self.reponse_json_error_params()

        act_prize_model = ActPrizeModel(context=self)
        act_prize = None
        old_act_prize = None
        if prize_id > 0:
            act_prize = act_prize_model.get_entity_by_id(prize_id)

        if not act_prize:
            act_prize = ActPrize()
        else:
            old_act_prize = act_prize

        act_prize.act_id = act_id
        act_prize.app_id = app_id
        act_prize.owner_open_id = owner_open_id
        act_prize.machine_id = machine_id
        act_prize.prize_type = prize_type
        act_prize.tag_id = tag_id
        act_prize.sort_index = sort_index
        act_prize.prize_pic = prize_pic if prize_pic != "" else unpack_pic
        act_prize.unpack_pic = unpack_pic
        act_prize.toys_pic = toys_pic
        act_prize.prize_name = prize_name
        act_prize.prize_price = prize_price
        act_prize.is_surplus = is_surplus
        act_prize.probability = probability
        act_prize.prize_limit = prize_limit
        act_prize.prize_detail = prize_detail if prize_detail != "" else json.dumps([])
        act_prize.modify_date = self.get_now_datetime()
        act_prize.is_release = is_release
        act_prize.is_sku = is_sku
        act_prize.goods_id = goods_id
        act_prize.goods_code = goods_code
        act_prize.goods_code_list = goods_code_list

        if prize_id > 0:
            act_prize_model.update_entity(act_prize, exclude_field_list=["prize_total", "surplus", "hand_out"])
            self.create_operation_log(OperationType.update.value, act_prize.__str__(), "PrizeHandler", old_act_prize, act_prize)
            if surplus == 0:
                operate_num = prize_total - act_prize.prize_total
            else:
                operate_num = surplus
            try:
                act_prize_model.update_table(f"surplus=surplus+{operate_num},prize_total=prize_total+{operate_num}", "id=%s", act_prize.id)
            except Exception as ex:
                self.logging_link_error("保存奖品异常:" + str(ex))
                return self.reponse_json_error("error", "保存失败,请调整库存")
        else:
            act_prize.create_date = act_prize.modify_date
            act_prize.surplus = surplus if surplus > 0 else prize_total
            act_prize.prize_total = prize_total
            act_prize.id = act_prize_model.add_entity(act_prize)
            self.create_operation_log(OperationType.add.value, act_prize.__str__(), "PrizeHandler", None, act_prize)

        return self.reponse_json_success(act_prize.id)