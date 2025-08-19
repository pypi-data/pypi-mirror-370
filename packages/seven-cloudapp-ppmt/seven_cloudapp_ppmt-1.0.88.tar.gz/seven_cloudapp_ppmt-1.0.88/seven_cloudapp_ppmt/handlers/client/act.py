# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-05-26 15:26:32
@LastEditTime: 2023-11-02 18:21:48
@LastEditors: HuangJianYi
:Description: 活动处理
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp.models.db_models.app.app_info_model import *
from seven_cloudapp.models.db_models.surplus.surplus_queue_model import *

from seven_cloudapp.handlers.client.act import ActInfoHandler

from seven_cloudapp_ppmt.models.db_models.act.act_info_model import *
from seven_cloudapp_ppmt.models.db_models.act.act_prize_model import *
from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *


class MachineListHandler(SevenBaseHandler):
    """
    :description: 首页盲盒列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 获取盲盒列表
        :param act_id:活动id
        :param page_index:页索引
        :param page_size:页大小
        :param price_gear_id:价格档位id
        :param integral_gear_id:会员积分档位id
        :param series_id:卖家ID
        :return: 
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        price_gear_id = int(self.get_param("price_gear_id", 0))
        integral_gear_id = int(self.get_param("integral_gear_id", 0))
        series_id = int(self.get_param("series_id", 0))
        now_date = self.get_now_datetime()

        machine_info_model = MachineInfoModel(context=self)
        act_prize_model = ActPrizeModel(context=self)

        condition = "act_id=%s AND is_release=1"
        params = [act_id]

        if price_gear_id > 0:
            condition += " AND price_gears_id=%s AND machine_type=2"
            params.append(price_gear_id)
        if integral_gear_id > 0:
            condition += " AND machine_price=%s AND machine_type=3"
            params.append(str(integral_gear_id) + ".00")
        if series_id > 0:
            condition += " AND series_id=%s"
            params.append(series_id)

        machine_info_page_list, total = machine_info_model.get_dict_page_list("*", page_index, page_size, condition, order_by="sort_index desc", params=params)

        surplus_list = []
        surplus_filter_list = []
        if len(machine_info_page_list) > 0:
            id_list = [str(machine_info["id"]) for machine_info in machine_info_page_list]
            if len(id_list) > 0:
                machine_info_ids = ",".join(id_list)
                surplus_list = act_prize_model.get_dict_list(f"machine_id in ({machine_info_ids}) AND is_release=1 AND surplus>0 AND probability>0", "machine_id", field="machine_id,sum(surplus) as surplus")
            for i in range(len(machine_info_page_list)):
                machine_info_page_list[i]["tag_name"] = ""
                machine_info_page_list[i]["tag_type"] = 0
                surplus_filter_list = [surplus for surplus in surplus_list if surplus["machine_id"] == machine_info_page_list[i]["id"]]
                if int(machine_info_page_list[i]["sale_type"]) == 2:
                    sale_date_str = str(machine_info_page_list[i]["sale_date"])
                    sale_date = TimeHelper.format_time_to_datetime(sale_date_str if sale_date_str != "1900-01-01 00:00:00" else now_date)
                    if TimeHelper.format_time_to_datetime(now_date) < sale_date:
                        machine_info_page_list[i]["tag_name"] = "代售"
                        machine_info_page_list[i]["tag_type"] = 1
                    elif len(surplus_filter_list) == 0:
                        machine_info_page_list[i]["tag_name"] = "售罄"
                        machine_info_page_list[i]["tag_type"] = 2
                    elif int(surplus_filter_list[0]["surplus"]) <= 0:
                        machine_info_page_list[i]["tag_name"] = "售罄"
                        machine_info_page_list[i]["tag_type"] = 2
                else:
                    if len(surplus_filter_list) == 0:
                        machine_info_page_list[i]["tag_name"] = "售罄"
                        machine_info_page_list[i]["tag_type"] = 2
                    elif int(surplus_filter_list[0]["surplus"]) <= 0:
                        machine_info_page_list[i]["tag_name"] = "售罄"
                        machine_info_page_list[i]["tag_type"] = 2

        page_info = PageInfo(page_index, page_size, total, machine_info_page_list)

        return self.reponse_json_success(page_info)


class PrizeListHandler(SevenBaseHandler):
    """
    :description: 分配的奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 分配的奖品列表
        :param act_id:活动id
        :param machine_id:机台id
        :param ver:版本
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", "0"))
        machine_id = int(self.get_param("machine_id", "0"))
        ver_no = self.get_param("ver", "")
        #self.logging_link_info("分配的奖品列表1111-" + str(self.request_params))

        #请求太频繁限制
        if self.check_post(f"PrizeList_Post_{str(open_id)}_{str(machine_id)}") == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")

        #入队列
        queue_name = f"PrizeList_Queue_{str(machine_id)}"
        identifier = None
        is_lock = False
        if self.check_lpush(queue_name, open_id) == False:
            identifier = self.acquire_lock(queue_name)
            is_lock = True
        if isinstance(identifier, bool):
            return self.reponse_json_error("UserLimit", "当前人数过多,请稍后再来")

        machine_info_model = MachineInfoModel(context=self)
        act_prize_model = ActPrizeModel(context=self)
        surplus_queue_model = SurplusQueueModel(context=self)
        machine_info = machine_info_model.get_entity_by_id(machine_id)
        if not machine_info or machine_info.is_release == 0:
            self.lpop(queue_name)
            self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoMachine", "对不起，找不到该盲盒")
        specs_type = machine_info.specs_type
        if specs_type == 3:
            ran_num = random.randint(1, 3)
        elif specs_type == 5:
            ran_num = random.randint(3, 5)
        elif specs_type == 6:
            ran_num = random.randint(3, 6)
        elif specs_type == 7:
            ran_num = random.randint(3, 7)
        elif specs_type == 8:
            ran_num = random.randint(4, 8)
        elif specs_type == 9:
            ran_num = random.randint(5, 9)
        elif specs_type == 10:
            ran_num = random.randint(6, 10)
        elif specs_type == 12:
            ran_num = random.randint(7, 12)
        else:
            ran_num = random.randint(9, 16)

        condition = "act_id=%s AND machine_id=%s AND is_release=1 AND surplus>0 AND probability>0"
        act_prize_list = act_prize_model.get_list(condition, params=[act_id, machine_id])
        if len(act_prize_list) <= 0:
            self.lpop(queue_name)
            if is_lock:
                self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoPrize", "对不起，该盲盒已售罄")
        if ran_num > len(act_prize_list):
            ran_num = len(act_prize_list)
        act_prize_id_list = []
        random_Prize_dict_list = {}
        for act_prize in act_prize_list:
            random_Prize_dict_list[act_prize.id] = act_prize.probability
        for i in range(ran_num):
            prize_id = self.random_weight(random_Prize_dict_list)
            act_prize_id_list.append(prize_id)
            if machine_info.is_repeat_prize == 0 or ver_no == "1.0.0":
                del random_Prize_dict_list[prize_id]
        act_prize_process_list = []
        if len(act_prize_id_list) > 0:
            if machine_info.is_repeat_prize == 0 or ver_no == "1.0.0":
                act_prize_process_list = [act_prize for act_prize in act_prize_list if act_prize.id in act_prize_id_list]
            else:
                for prize_id in act_prize_id_list:
                    filter_act_prize = [act_prize for act_prize in act_prize_list if act_prize.id == prize_id]
                    if len(filter_act_prize) > 0:
                        act_prize_process_list.extend(filter_act_prize)
        else:
            self.lpop(queue_name)
            if is_lock:
                self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoPrize", "对不起，该盲盒已售罄")

        key_id = self.create_order_id()
        result_info = {}
        act_prize_result_list = []
        for act_prize in act_prize_process_list:
            update_result = act_prize_model.update_table("surplus=surplus-1", "id=%s AND surplus>0", params=[act_prize.id])
            # self.logging_link_info("update_result-" + str(update_result) + str(act_prize.id))
            if update_result == True:
                #预扣队列
                surplus_queue = SurplusQueue()
                surplus_queue.app_id = app_id
                surplus_queue.act_id = act_id
                surplus_queue.machine_id = machine_id
                surplus_queue.prize_id = act_prize.id
                surplus_queue.key_id = key_id
                surplus_queue.open_id = open_id
                surplus_queue.withhold_value = 1
                surplus_queue.create_date = self.get_now_datetime()
                surplus_queue.expire_date = TimeHelper.add_hours_by_format_time(hour=1)
                surplus_queue.ProcessType = 2
                surplus_queue_model.add_entity(surplus_queue)
                act_prize_dict = {}
                act_prize_dict["prize_id"] = act_prize.id
                act_prize_dict["prize_name"] = act_prize.prize_name
                act_prize_dict["prize_pic"] = act_prize.prize_pic
                act_prize_dict["prize_detail"] = self.json_loads(act_prize.prize_detail)
                act_prize_dict["unpack_pic"] = act_prize.unpack_pic
                act_prize_dict["toys_pic"] = act_prize.toys_pic
                act_prize_dict["tag_id"] = act_prize.tag_id
                act_prize_dict["surplus"] = act_prize.surplus
                act_prize_dict["is_surplus"] = act_prize.is_surplus
                act_prize_dict["prize_price"] = act_prize.prize_price
                act_prize_result_list.append(act_prize_dict)
        self.lpop(queue_name)
        if is_lock:
            self.release_lock(queue_name, identifier)
        if len(act_prize_result_list) <= 0:
            return self.reponse_json_error("NoPrize", "对不起，该盲盒已售罄")
        result_info["key_id"] = key_id
        result_info["prize_list"] = act_prize_result_list

        return self.reponse_json_success(result_info)


class MinboxListHandler(SevenBaseHandler):
    """
    :description: 小盒子奖品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 小盒子奖品列表
        :param act_id:活动id
        :param machine_id:机台id
        :param ver:版本
        :return: 
        :last_editors: HuangJianYi
        """
        app_id = self.get_taobao_param().source_app_id
        open_id = self.get_taobao_param().open_id
        act_id = int(self.get_param("act_id", "0"))
        machine_id = int(self.get_param("machine_id", "0"))
        #self.logging_link_info("分配的奖品列表1111-" + str(self.request_params))

        #请求太频繁限制
        if self.check_post(f"PrizeList_Post_{str(open_id)}_{str(machine_id)}") == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")

        #入队列
        queue_name = f"PrizeList_Queue_{str(machine_id)}"
        identifier = None
        is_lock = False
        if self.check_lpush(queue_name, open_id) == False:
            identifier = self.acquire_lock(queue_name)
            is_lock = True
        if isinstance(identifier, bool):
            return self.reponse_json_error("UserLimit", "当前人数过多,请稍后再来")

        machine_info_model = MachineInfoModel(context=self)
        act_prize_model = ActPrizeModel(context=self)
        surplus_queue_model = SurplusQueueModel(context=self)
        machine_info = machine_info_model.get_entity_by_id(machine_id)
        if not machine_info or machine_info.is_release == 0:
            self.lpop(queue_name)
            self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoMachine", "对不起，找不到该盲盒")
        specs_type = machine_info.specs_type
        if specs_type == 3:
            ran_num = random.randint(1, 3)
        elif specs_type == 5:
            ran_num = random.randint(3, 5)
        elif specs_type == 6:
            ran_num = random.randint(3, 6)
        elif specs_type == 7:
            ran_num = random.randint(3, 7)
        elif specs_type == 8:
            ran_num = random.randint(4, 8)
        elif specs_type == 9:
            ran_num = random.randint(5, 9)
        elif specs_type == 10:
            ran_num = random.randint(6, 10)
        elif specs_type == 12:
            ran_num = random.randint(7, 12)
        else:
            ran_num = random.randint(9, 16)

        condition = "act_id=%s AND machine_id=%s AND is_release=1 AND surplus>0 AND probability>0"
        act_prize_list = act_prize_model.get_list(condition, params=[act_id, machine_id])
        if len(act_prize_list) <= 0:
            self.lpop(queue_name)
            if is_lock:
                self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoPrize", "对不起，该盲盒已售罄")
        if ran_num > len(act_prize_list):
            ran_num = len(act_prize_list)
        act_prize_id_list = []
        random_Prize_dict_list = {}
        for act_prize in act_prize_list:
            random_Prize_dict_list[act_prize.id] = act_prize.probability
        for i in range(ran_num):
            prize_id = self.random_weight(random_Prize_dict_list)
            act_prize_id_list.append(prize_id)
            if machine_info.is_repeat_prize == 0:
                del random_Prize_dict_list[prize_id]
        act_prize_process_list = []
        if len(act_prize_id_list) > 0:
            if machine_info.is_repeat_prize == 0:
                act_prize_process_list = [act_prize for act_prize in act_prize_list if act_prize.id in act_prize_id_list]
            else:
                for prize_id in act_prize_id_list:
                    filter_act_prize = [act_prize for act_prize in act_prize_list if act_prize.id == prize_id]
                    if len(filter_act_prize) > 0:
                        act_prize_process_list.extend(filter_act_prize)
        else:
            self.lpop(queue_name)
            if is_lock:
                self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoPrize", "对不起，该盲盒已售罄")

        key_id = self.create_order_id()
        result_info = {}
        result_list = []
        redis_prize_dict = {}
        serial_no = 0
        random.shuffle(act_prize_process_list)
        for act_prize in act_prize_process_list:
            update_result = act_prize_model.update_table("surplus=surplus-1", "id=%s AND surplus>0", params=[act_prize.id])
            # self.logging_link_info("update_result-" + str(update_result) + str(act_prize.id))
            if update_result == True:
                serial_no = int(serial_no) + 1
                #预扣队列
                surplus_queue = SurplusQueue()
                surplus_queue.app_id = app_id
                surplus_queue.act_id = act_id
                surplus_queue.machine_id = machine_id
                surplus_queue.prize_id = act_prize.id
                surplus_queue.key_id = key_id
                surplus_queue.open_id = open_id
                surplus_queue.withhold_value = 1
                surplus_queue.create_date = self.get_now_datetime()
                surplus_queue.expire_date = TimeHelper.add_hours_by_format_time(hour=1)
                surplus_queue.ProcessType = 2
                surplus_queue_model.add_entity(surplus_queue)

                prize_dict = {}
                prize_dict["serial_no"] = serial_no
                result_list.append(prize_dict)
                redis_prize_dict[str(serial_no)] = act_prize.id
        self.lpop(queue_name)
        if is_lock:
            self.release_lock(queue_name, identifier)
        if len(result_list) <= 0:
            return self.reponse_json_error("NoPrize", "对不起，该盲盒已售罄")
        result_info["key_id"] = key_id
        result_info["specs_type"] = specs_type
        result_info["min_machine_list"] = result_list

        self.redis_init().set(f"minbox_list_{str(open_id)}_{str(key_id)}", self.json_dumps(redis_prize_dict), ex=3600 * 1)

        return self.reponse_json_success(result_info)


class CrmIntegralGearlListHandler(SevenBaseHandler):
    """
    :description: 会员积分档位列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description:  会员积分档位列表
        :return: 分页列表信息
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        condition = "is_release=1 AND act_id=%s AND machine_type=3"
        params = [act_id]
        integra_gear_list = []
        machine_info_list_dict = MachineInfoModel(context=self).get_dict_list(condition, order_by="sort_index desc", field="machine_price", params=params)
        for machine_info_dict in machine_info_list_dict:
            if int(machine_info_dict["machine_price"]) not in integra_gear_list:
                integra_gear_list.append(int(machine_info_dict["machine_price"]))
        return self.reponse_json_success(integra_gear_list)