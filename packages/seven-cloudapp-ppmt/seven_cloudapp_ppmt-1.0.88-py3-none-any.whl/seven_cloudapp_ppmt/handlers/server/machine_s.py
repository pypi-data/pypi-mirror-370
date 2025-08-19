# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-05-29 09:40:42
@LastEditTime: 2022-02-17 15:33:23
@LastEditors: HuangJianYi
:description: 机台（盒子）
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.enum import OperationType
from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.behavior_model import *
from seven_cloudapp.models.db_models.machine.machine_value_model import *
from seven_cloudapp.models.db_models.price.price_gear_model import *

from seven_cloudapp.handlers.server.machine_s import MachineReleaseHandler
from seven_cloudapp.handlers.server.machine_s import CheckBuyEndboxHandler

from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *
from seven_cloudapp_ppmt.models.db_models.act.act_prize_model import *
from seven_cloudapp_ppmt.models.db_models.act.act_info_model import *


class MachineHandler(SevenBaseHandler):
    """
    :description: 保存机台
    """
    @filter_check_params("app_id,act_id,machine_name")
    def post_async(self):
        """
        :description: 保存机台
        :param machine_id：机台id
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        machine_id = int(self.get_param("machine_id", 0))
        act_id = int(self.get_param("act_id", 0))
        machine_name = self.get_param("machine_name")
        machine_type = int(self.get_param("machine_type", 0))
        goods_id = self.get_param("goods_id")
        sku_id = self.get_param("sku_id")
        skin_id = int(self.get_param("skin_id", 0))
        price_gears_id = int(self.get_param("price_gears_id", 0))
        series_id = int(self.get_param("series_id", 0))
        specs_type = int(self.get_param("specs_type", 0))
        index_pic = self.get_param("index_pic")
        machine_bg_pic = self.get_param("machine_bg_pic")
        goods_detail = self.get_param("goods_detail")
        box_style_type = int(self.get_param("box_style_type", 0))
        box_style_detail = self.get_param("box_style_detail")
        sale_type = int(self.get_param("sale_type", 0))
        sale_date = self.get_param("sale_date", "1900-01-01 00:00:00")
        sort_index = int(self.get_param("sort_index", 0))
        is_release = int(self.get_param("is_release", 0))
        is_false_prize = int(self.get_param("is_false_prize", 0))
        single_lottery_price = int(self.get_param("single_lottery_price", 0))
        many_lottery_price = int(self.get_param("many_lottery_price", 0))
        many_lottery_num = int(self.get_param("many_lottery_num", 0))
        machine_price = decimal.Decimal(self.get_param("machine_price", "0.00"))
        is_repeat_prize = int(self.get_param("is_repeat_prize", 0))
        is_buy_endbox = int(self.get_param("is_buy_endbox", 0))

        if act_id <= 0:
            return self.reponse_json_error_params()

        machine_info = None
        machine_info_model = MachineInfoModel(context=self)
        if machine_id > 0:
            machine_info = machine_info_model.get_entity_by_id(machine_id)

        is_add = False
        if not machine_info:
            is_add = True
            machine_info = MachineInfo()

        old_machine_info = deepcopy(machine_info)

        machine_info.act_id = act_id
        machine_info.app_id = app_id
        machine_info.machine_name = machine_name
        machine_info.goods_id = goods_id
        machine_info.sku_id = sku_id
        machine_info.skin_id = skin_id
        machine_info.price_gears_id = price_gears_id
        machine_info.series_id = series_id
        machine_info.specs_type = specs_type
        machine_info.index_pic = index_pic
        machine_info.machine_bg_pic = machine_bg_pic
        machine_info.goods_detail = goods_detail if goods_detail != "" else self.json_dumps([])
        machine_info.box_style_type = box_style_type
        machine_info.box_style_detail = box_style_detail if box_style_detail != "" else self.json_dumps({})
        machine_info.sale_type = sale_type
        machine_info.sale_date = sale_date
        machine_info.sort_index = sort_index
        machine_info.is_release = is_release
        machine_info.is_false_prize = is_false_prize
        machine_info.single_lottery_price = single_lottery_price
        machine_info.many_lottery_price = many_lottery_price
        machine_info.many_lottery_num = many_lottery_num
        machine_info.machine_price = decimal.Decimal(machine_price)
        machine_info.is_repeat_prize = is_repeat_prize
        machine_info.is_buy_endbox = is_buy_endbox
        machine_info.goods_modify_date = self.get_now_datetime()
        machine_info.modify_date = machine_info.goods_modify_date

        if is_add:
            machine_info.machine_type = machine_type
            machine_info.create_date = machine_info.modify_date
            machine_info.id = machine_info_model.add_entity(machine_info)
            
            # 增加行为映射数据
            orm_infos = []
            for i in range(0, 2):
                behavior_orm = BehaviorOrm()
                if i == 0:
                    behavior_orm.is_repeat = 0
                    behavior_orm.key_value = machine_info.machine_name + "拆开次数"
                    behavior_orm.key_name = "openCount_" + str(machine_info.id)
                else:
                    behavior_orm.is_repeat = 1
                    behavior_orm.repeat_type = 1
                    behavior_orm.key_value = machine_info.machine_name + "拆开人数"
                    behavior_orm.key_name = "openUserCount_" + str(machine_info.id)
                behavior_orm.orm_type = 1
                behavior_orm.group_name = ""
                behavior_orm.is_common = 0
                behavior_orm.sort_index = 1
                behavior_orm.app_id = app_id
                behavior_orm.act_id = act_id
                behavior_orm.create_date = self.get_now_datetime()
                orm_infos.append(behavior_orm)
            behavior_orm_model = BehaviorOrmModel(context=self)
            behavior_orm_model.add_list(orm_infos)
            # 记录日志
            self.create_operation_log(OperationType.add.value, machine_info.__str__(), "MachineHandler", None, self.json_dumps(machine_info))
        else:
            machine_info_model.update_entity(machine_info)
            self.create_operation_log(OperationType.update.value, machine_info.__str__(), "MachineHandler", self.json_dumps(old_machine_info), self.json_dumps(machine_info))

        return self.reponse_json_success(machine_info.id)


class MachineListHandler(SevenBaseHandler):
    """
    :description: 机台信息
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取机台列表
        :param act_id：活动id
        :param series_id：IP系列id
        :param is_release：是否发布
        :param page_index：页索引
        :param page_size：页大小
        :return: list
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        series_id = int(self.get_param("series_id", 0))
        is_release = int(self.get_param("is_release", -1))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 10))

        condition = "act_id=%s"
        params = [act_id]
        if series_id > 0:
            condition += " and series_id=%s"
            params.append(series_id)
        if is_release >= 0:
            condition += " and is_release=%s"
            params.append(is_release)

        page_list, total = MachineInfoModel(context=self).get_dict_page_list("*", page_index, page_size, condition, "", "sort_index desc", params=params)

        for page in page_list:
            page["goods_detail"] = self.json_loads(page['goods_detail'])
            page["box_style_detail"] = self.json_loads(page['box_style_detail'])

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class MachineDelHandler(SevenBaseHandler):
    """
    :description: 删除机台
    """
    @filter_check_params("machine_id")
    def get_async(self):
        """
        :description: 删除机台
        :param machine_id：机台id
        :return: reponse_json_success
        :last_editors: HuangJingCan
        """
        machine_id = int(self.get_param("machine_id", 0))

        if machine_id <= 0:
            return self.reponse_json_error_params()

        ActPrizeModel(context=self).del_entity("machine_id=%s", machine_id)

        MachineInfoModel(context=self).del_entity("id=%s", machine_id)

        MachineValueModel(context=self).del_entity("machine_id=%s", machine_id)

        BehaviorOrmModel(context=self).del_entity("key_name='openUserCount_" + str(machine_id) + "' or key_name='openCount_" + str(machine_id) + "'")

        self.create_operation_log(OperationType.delete.value, "machine_info_tb", "MachineDelHandler", None, machine_id)

        return self.reponse_json_success()


class UpdateMachinePriceByGearIdHandler(SevenBaseHandler):
    """
    :description: 更新机台价格，通过档位id
    """
    def get_async(self):
        """
        :description: 更新机台价格，通过档位id
        :param act_id：活动id
        :param gear_id：档位id
        :return: reponse_json_success
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        gear_id = int(self.get_param("gear_id", 0))

        if act_id <= 0 or gear_id <= 0:
            return self.reponse_json_error_params()

        price_gear_model = PriceGearModel(context=self)
        price_gear = price_gear_model.get_dict_by_id(gear_id)
        if not price_gear or price_gear["act_id"] != act_id:
            return self.reponse_json_error("Error", "价格档位不存在")

        machine_info_model = MachineInfoModel(context=self)
        machine_info_model.update_table("machine_price=%s", "act_id=%s and price_gears_id=%s", params=[price_gear["price"], act_id, gear_id])

        return self.reponse_json_success()


class CheckingPriceGearHandler(SevenBaseHandler):
    """
    :description: 验证价格档位
    """
    @filter_check_params("goods_id,act_id")
    def get_async(self):
        """
        :description: 验证价格档位
        :param goods_id：商品id
        :param act_id：活动id
        :param price_gear_id：价格档位id
        :return: reponse_json_success
        :last_editors: WangQiang
        """

        app_id = self.get_param("app_id")
        goods_id = self.get_param("goods_id", "")
        sku_id = self.get_param("sku_id", "")  #不传，则为无SKU绑定
        act_id = int(self.get_param("act_id", "0"))
        price_gear_id = int(self.get_param("price_gear_id", "0"))
        price_gear_model = PriceGearModel(context=self)
        condtion = "app_id=%s and goods_id=%s"
        params = [app_id, goods_id]
        if price_gear_id > 0:
            condtion += " and id!=%s"
            params.append(price_gear_id)
        price_gear_dict_list = price_gear_model.get_dict_list(condtion, params=params)
        is_fail = False
        bind_act_id = 0
        if price_gear_dict_list:
            if not sku_id:
                is_fail = True
                bind_act_id = price_gear_dict_list[0]["act_id"]
            else:
                for price_gear_dict in price_gear_dict_list:
                    if price_gear_dict["relation_type"] == 1 or price_gear_dict["sku_id"] == sku_id:
                        is_fail = True
                        bind_act_id = int(price_gear_dict["act_id"])
                        break
        #验证失败
        if is_fail == True:
            if act_id == bind_act_id:
                return self.reponse_json_error("Bound", "对不起,该商品已绑定其他价格档位")
            else:
                act_info = ActInfoModel(context=self).get_entity_by_id(bind_act_id)
                if act_info:
                    return self.reponse_json_error("Bound", "对不起,该商品已绑定" + act_info.act_name + "活动")
        self.reponse_json_success()