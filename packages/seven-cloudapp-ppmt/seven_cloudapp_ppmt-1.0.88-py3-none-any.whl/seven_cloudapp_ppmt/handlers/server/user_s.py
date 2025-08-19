# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-05-12 20:04:54
@LastEditTime: 2023-02-13 17:30:50
@LastEditors: HuangJianYi
:description: 用户相关
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.enum import OperationType, SourceType
from seven_cloudapp.models.seven_model import PageInfo

from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.gear.gear_value_model import *
from seven_cloudapp.models.db_models.gear.gear_log_model import *
from seven_cloudapp.models.db_models.price.price_gear_model import *
from seven_cloudapp.models.db_models.coin.coin_order_model import *
from seven_cloudapp.models.db_models.machine.machine_value_model import *
from seven_cloudapp.models.db_models.lottery.lottery_value_log_model import *
from seven_cloudapp.models.db_models.prop.prop_log_model import *
from seven_cloudapp.models.db_models.user.user_detail_model import *

from seven_cloudapp.handlers.server.user_s import LoginHandler
from seven_cloudapp.handlers.server.user_s import UserStatusHandler
from seven_cloudapp.handlers.server.user_s import UserDetailHandler
from seven_cloudapp.handlers.server.user_s import PropLogHandler

from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *
from seven_cloudapp_ppmt.models.db_models.prop.prop_give_model import *


class UserListHandler(SevenBaseHandler):
    """
    :description: 用户列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户列表
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param user_nick：用户昵称
        :return PageInfo
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        user_nick = self.get_param("nick_name")
        user_open_id = self.get_param("user_open_id")

        condition = "act_id=%s"
        params = [act_id]
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if user_open_id:
            condition += " AND open_id=%s"
            params.append(user_open_id)

        page_list, total = UserInfoModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        if page_list:
            where_machine_value = SevenHelper.get_condition_by_id_list("open_id", [i["open_id"] for i in page_list])
            where_gear_value = SevenHelper.get_condition_by_id_list("open_id", [i["open_id"] for i in page_list])
            price_gear_list = PriceGearModel(context=self).get_list("act_id=%s and is_del=1", params=[act_id])
            if price_gear_list:
                id_list_str = str([i.id for i in price_gear_list]).strip('[').strip(']')
                where_gear_value += f" and price_gears_id NOT IN({id_list_str})"
            dict_machine_value_list = MachineValueModel(context=self).get_dict_list(f"act_id={act_id} AND {where_machine_value}", "open_id", field="open_id,sum(open_value) as open_value")
            dict_gear_value_list = GearValueModel(context=self).get_dict_list(f"act_id={act_id} AND {where_gear_value}", "open_id", field="open_id,sum(current_value) as current_value")
            for i in range(0, len(dict_machine_value_list)):
                dict_machine_value_list[i]["open_value"] = int(dict_machine_value_list[i]["open_value"])
            for i in range(0, len(dict_gear_value_list)):
                dict_gear_value_list[i]["current_value"] = int(dict_gear_value_list[i]["current_value"]) if dict_gear_value_list[i]["current_value"] else 0
            new_dict_list = SevenHelper.merge_dict_list(page_list, "open_id", dict_machine_value_list, "open_id", "open_value")
            new_dict_list = SevenHelper.merge_dict_list(new_dict_list, "open_id", dict_gear_value_list, "open_id", "current_value")
            page_info = PageInfo(page_index, page_size, total, new_dict_list)

            return self.reponse_json_success(page_info)

        return self.reponse_json_success(PageInfo(page_index, page_size, total, page_list))


class UserMachineListHandler(SevenBaseHandler):
    """
    :description: 用户机台数据列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 用户机台数据列表
        :param act_id:活动id
        :param user_open_id:user_open_id
        :return: list
        :last_editors: HuangJingCan
        """
        act_id = int(self.get_param("act_id", 0))
        user_open_id = self.get_param("user_open_id")
        condition = "act_id=%s and open_id=%s"
        new_dict_list = []
        dict_machine_Info_list = MachineInfoModel(context=self).get_dict_list("act_id=%s and is_release=1", field="id,machine_name", params=act_id)
        dict_machine_value_list = MachineValueModel(context=self).get_dict_list(condition, params=[act_id, user_open_id])
        if len(dict_machine_Info_list) > 0:
            new_dict_list = SevenHelper.merge_dict_list(dict_machine_Info_list, "id", dict_machine_value_list, "machine_id", "open_value")
            return self.reponse_json_success(new_dict_list)

        return self.reponse_json_success(new_dict_list)


class GearValueHandler(SevenBaseHandler):
    """
    :description: 设置开盒次数
    """
    @filter_check_params("user_open_id,act_id")
    def post_async(self):
        """
        :description: 设置开盒次数
        :param user_open_id：用户唯一标识
        :param set_content_list：档位设置集合
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        user_open_id = self.get_param("user_open_id")
        set_content_list = self.get_param("set_content_list")
        act_id = int(self.get_param("act_id", 0))
        app_id = self.get_param("app_id")
        modify_date = self.get_now_datetime()

        user_info_model = UserInfoModel(context=self)
        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[user_open_id, act_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，找不到该用户")

        gear_value_model = GearValueModel(context=self)

        if act_id <= 0:
            return self.reponse_json_error_params()

        set_content_list = self.json_loads(set_content_list)

        for set_content in set_content_list:
            price_gears_id = set_content["price_gears_id"]
            current_value = set_content["current_value"]
            if not isinstance(current_value, int):
                return self.reponse_json_error("NoValue","对不起，拆盒次数请传入整数")

            result = False
            history_value = 0
            gear_value = gear_value_model.get_entity("act_id=%s AND open_id=%s AND price_gears_id=%s", params=[act_id, user_open_id, price_gears_id])
            if gear_value:
                history_value = gear_value.current_value
                if history_value != current_value:
                    result = gear_value_model.update_table("current_value=%s,modify_date=%s", "act_id=%s AND open_id=%s AND price_gears_id=%s", [current_value, modify_date, act_id, user_open_id, price_gears_id])
            else:
                gear_value = GearValue()
                gear_value.act_id = act_id
                gear_value.app_id = app_id
                gear_value.open_id = user_open_id
                gear_value.price_gears_id = price_gears_id
                gear_value.open_value = 0
                gear_value.current_value = current_value
                gear_value.modify_date = modify_date
                gear_value.create_date = modify_date
                result = gear_value_model.add_entity(gear_value)
                if result > 0:
                    result = True

            if result:
                gear_log = GearLog()
                gear_log.app_id = app_id
                gear_log.act_id = act_id
                gear_log.open_id = user_open_id
                gear_log.price_gears_id = price_gears_id
                gear_log.type_value = SourceType.手动配置.value
                gear_log.current_value = current_value - history_value
                gear_log.history_value = history_value
                gear_log.create_date = modify_date
                GearLogModel(context=self).add_entity(gear_log)

                #添加商家对帐记录
                coin_order_model = CoinOrderModel(context=self)
                if (current_value - history_value) > 0:
                    coin_order = CoinOrder()
                    coin_order.open_id = user_open_id
                    coin_order.app_id = app_id
                    coin_order.act_id = act_id
                    coin_order.price_gears_id = price_gears_id
                    coin_order.reward_type = 0
                    coin_order.nick_name = user_info.user_nick
                    coin_order.buy_count = current_value - history_value
                    coin_order.surplus_count = current_value - history_value
                    coin_order.create_date = self.get_now_datetime()
                    coin_order.modify_date = self.get_now_datetime()
                    coin_order_model.add_entity(coin_order)
                else:
                    del_count = history_value - current_value
                    update_coin_order_list = []
                    coin_order_set_list = coin_order_model.get_list("act_id=%s and open_id=%s and surplus_count>0 and price_gears_id=%s and pay_order_id=0", "id asc", params=[act_id, user_open_id, price_gears_id])

                    if len(coin_order_set_list) > 0:
                        for coin_order in coin_order_set_list:
                            if coin_order.surplus_count > del_count:
                                coin_order.surplus_count = coin_order.surplus_count - del_count
                                del_count = 0
                            else:
                                del_count = del_count - coin_order.surplus_count
                                coin_order.surplus_count = 0
                            update_coin_order_list.append(coin_order)
                            if del_count == 0:
                                break
                    if del_count > 0:
                        coin_order_pay_list = coin_order_model.get_list("act_id=%s and open_id=%s and surplus_count>0 and price_gears_id=%s and pay_order_id>0", "id asc", params=[act_id, user_open_id, price_gears_id])
                        if len(coin_order_pay_list) > 0:
                            for coin_order in coin_order_pay_list:
                                if coin_order.surplus_count > del_count:
                                    coin_order.surplus_count = coin_order.surplus_count - del_count
                                    del_count = 0
                                else:
                                    del_count = del_count - coin_order.surplus_count
                                    coin_order.surplus_count = 0
                                update_coin_order_list.append(coin_order)
                                if del_count == 0:
                                    break
                    for coin_order in update_coin_order_list:
                        coin_order_model.update_entity(coin_order)

        return self.reponse_json_success()


class GearLogHandler(SevenBaseHandler):
    """
    :description: 用户档位配置记录
    """
    def get_async(self):
        """
        :description: 用户档位配置记录
        :param act_id:活动id
        :param user_open_id:user_open_id
        :return list
        :last_editors: HuangJianYi
        """
        act_id = int(self.get_param("act_id", 0))
        user_open_id = self.get_param("user_open_id")

        price_gear_model = PriceGearModel(context=self)
        gear_value_model = GearValueModel(context=self)
        gear_log_model = GearLogModel(context=self)

        price_gear_list = price_gear_model.get_list("act_id=%s and is_del=0", params=act_id)
        gear_value_list = gear_value_model.get_list("act_id=%s and open_id=%s", params=[act_id, user_open_id])
        gear_log_list_dict = gear_log_model.get_dict_list("act_id=%s and open_id=%s", order_by='create_date desc', params=[act_id, user_open_id])

        gear_log_groups = []
        for price_gear in price_gear_list:
            gear_log_group = {}
            gear_log_group["gear_value_id"] = price_gear.id
            gear_log_group["gear_value_price"] = price_gear.price
            for gear_value in gear_value_list:
                if gear_value.price_gears_id == price_gear.id:
                    gear_log_group["surplus_value"] = gear_value.current_value
                    continue
            if "surplus_value" not in gear_log_group.keys():
                gear_log_group["surplus_value"] = 0
            gear_log_group["gear_log_list"] = [i for i in gear_log_list_dict if i["price_gears_id"] == price_gear.id]
            gear_log_groups.append(gear_log_group)

        return self.reponse_json_success(gear_log_groups)


class SurplusIntegralHandler(SevenBaseHandler):
    """
    :description: 设置心愿值
    """
    @filter_check_params("user_open_id,act_id")
    def get_async(self):
        """
        :description: 设置积分
        :param user_open_id：用户唯一标识
        :param integral:操作积分
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        user_open_id = self.get_param("user_open_id")
        integral = int(self.get_param("integral", 0))
        act_id = int(self.get_param("act_id", 0))

        user_info_model = UserInfoModel(context=self)
        lottery_value_log_model = LotteryValueLogModel(context=self)
        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[user_open_id, act_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，找不到该用户")

        history_integral = user_info.surplus_integral
        operate_integral = int(integral - history_integral)
        if operate_integral == 0:
            return self.reponse_json_error("No", "没有变动无需修改")

        #创建积分记录
        lottery_value_log = LotteryValueLog()
        lottery_value_log.app_id = user_info.app_id
        lottery_value_log.act_id = user_info.act_id
        lottery_value_log.open_id = user_info.open_id
        lottery_value_log.user_nick = user_info.user_nick
        lottery_value_log.log_title = f"手动配置"
        lottery_value_log.log_desc = ""
        lottery_value_log.log_info = {}
        lottery_value_log.currency_type = 2
        lottery_value_log.source_type = SourceType.手动配置.value
        lottery_value_log.change_type = 301 if operate_integral > 0 else 302
        lottery_value_log.operate_type = 0 if operate_integral > 0 else 1
        lottery_value_log.current_value = operate_integral
        lottery_value_log.history_value = history_integral
        lottery_value_log.create_date = self.get_now_datetime()

        result = user_info_model.update_table(f"surplus_integral=surplus_integral+{operate_integral}", "id=%s and surplus_integral=%s", params=[user_info.id, user_info.surplus_integral])
        if result == False:
            return self.reponse_json_error("No", "心愿值发生变动,无法保存,请刷新页面")
        lottery_value_log_model.add_entity(lottery_value_log)

        return self.reponse_json_success()


class LotteryValueLogHandler(SevenBaseHandler):
    """
    :description: 各种货币变动明细记录
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 各种货币变动明细记录
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param nick_name：淘宝名
        :param start_date：开始时间
        :param end_date：结束时间
        :param source_type：来源类型
        :param user_open_id：用户open_id
        :return list
        :last_editors: HuangJingCan
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        user_nick = self.get_param("nick_name")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        source_type = int(self.get_param("source_type", -1))
        user_open_id = self.get_param("user_open_id")
        currency_type = int(self.get_param("currency_type", 2))

        condition = "act_id=%s"
        params = [act_id]

        if source_type >= 0:
            condition += " AND source_type=%s"
            params.append(source_type)
        if currency_type >= 0:
            condition += " AND currency_type=%s"
            params.append(currency_type)
        if user_open_id:
            condition += " AND open_id=%s"
            params.append(user_open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)

        page_list, total = LotteryValueLogModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)


class PropHandler(SevenBaseHandler):
    """
    :description:  设置用户道具卡数   
    """
    @filter_check_params("user_open_id,act_id,prop_type")
    def get_async(self):
        """
        :description: 设置用户道具卡数
        :param user_open_id：用户唯一标识
        :param prop_num:操作道具数量
        :param prop_type:道具类型(2透视卡3提示卡4重抽卡)
        :return: reponse_json_success
        :last_editors: HuangJianYi
        """
        user_open_id = self.get_param("user_open_id")
        prop_num = int(self.get_param("prop_num", 0))
        act_id = int(self.get_param("act_id", 0))
        prop_type = int(self.get_param("prop_type", 0))

        user_info_model = UserInfoModel(context=self)
        prop_log_model = PropLogModel(context=self)
        user_detail_model = UserDetailModel(context=self)
        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[user_open_id, act_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，找不到该用户")

        history_value = 0
        user_detail = user_detail_model.get_entity("open_id=%s and act_id=%s", params=[user_open_id, act_id])
        if not user_detail:
            user_detail = UserDetail()
            if prop_type == 2:
                user_detail.perspective_card_count = prop_num
                user_detail.tips_card_count = 0
                user_detail.redraw_card_count = 0
            elif prop_type == 3:
                user_detail.perspective_card_count = 0
                user_detail.tips_card_count = prop_num
                user_detail.redraw_card_count = 0
            else:
                user_detail.perspective_card_count = 0
                user_detail.tips_card_count = 0
                user_detail.redraw_card_count = prop_num
            user_detail.app_id = user_info.app_id
            user_detail.act_id = act_id
            user_detail.open_id = user_open_id
            user_detail.create_date = self.get_now_datetime()
            user_detail_model.add_entity(user_detail)
        else:
            if prop_type == 2:
                history_value = user_detail.perspective_card_count
                operate_value = int(prop_num - history_value)
                if operate_value == 0:
                    return self.reponse_json_error("No", "没有变动无需修改")
                user_detail_model.update_table(f"perspective_card_count=perspective_card_count+{operate_value}", "open_id=%s and act_id=%s", params=[user_open_id, act_id])
            elif prop_type == 3:
                history_value = user_detail.tips_card_count
                operate_value = int(prop_num - history_value)
                if operate_value == 0:
                    return self.reponse_json_error("No", "没有变动无需修改")
                user_detail_model.update_table(f"tips_card_count=tips_card_count+{operate_value}", "open_id=%s and act_id=%s", params=[user_open_id, act_id])
            else:
                history_value = user_detail.redraw_card_count
                operate_value = int(prop_num - history_value)
                if operate_value == 0:
                    return self.reponse_json_error("No", "没有变动无需修改")
                user_detail_model.update_table(f"redraw_card_count=redraw_card_count+{operate_value}", "open_id=%s and act_id=%s", params=[user_open_id, act_id])

        #创建道具记录
        prop_log = PropLog()
        prop_log.app_id = user_info.app_id
        prop_log.act_id = act_id
        prop_log.open_id = user_open_id
        prop_log.user_nick = user_info.user_nick
        prop_log.change_type = 1
        prop_log.operate_type = 0 if operate_value > 0 else 1
        prop_log.prop_type = prop_type
        prop_log.machine_name = ""
        prop_log.specs_type = 0
        prop_log.operate_value = operate_value
        prop_log.history_value = history_value
        prop_log.title = "手动配置"
        prop_log.create_date_int = SevenHelper.get_now_day_int()
        prop_log.create_date = self.get_now_datetime()
        prop_log_model.add_entity(prop_log)

        return self.reponse_json_success()


class PropGiveListHandler(SevenBaseHandler):
    """
    :description: 道具赠送记录列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 道具赠送记录列表
        :param page_index：页索引
        :param page_size：页大小
        :param act_id：活动id
        :param user_open_id：赠送人open_id
        :param nick_name：赠送人淘宝名
        :param draw_open_id：领取人open_id
        :param draw_nick_name：领取人淘宝名
        :param start_date：开始时间
        :param end_date：结束时间
        :param give_status：赠送状态(0未领取1已领取2已失效)
        :return list
        :last_editors: HuangJianYi
        """
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 20))
        act_id = int(self.get_param("act_id", 0))
        user_nick = self.get_param("nick_name")
        user_open_id = self.get_param("user_open_id")
        draw_user_nick = self.get_param("draw_nick_name")
        draw_open_id = self.get_param("draw_open_id")
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")
        give_status = int(self.get_param("give_status", -1))

        condition = "act_id=%s"
        params = [act_id]

        if give_status >= 0:
            condition += " AND give_status=%s"
            params.append(give_status)
        if user_open_id:
            condition += " AND open_id=%s"
            params.append(user_open_id)
        if user_nick:
            condition += " AND user_nick=%s"
            params.append(user_nick)
        if draw_open_id:
            condition += " AND draw_open_id=%s"
            params.append(draw_open_id)
        if draw_user_nick:
            condition += " AND draw_user_nick=%s"
            params.append(draw_user_nick)
        if start_date:
            condition += " AND create_date>=%s"
            params.append(start_date)
        if end_date:
            condition += " AND create_date<=%s"
            params.append(end_date)

        page_list, total = PropGiveModel(context=self).get_dict_page_list("*", page_index, page_size, condition, order_by="id desc", params=params)

        page_info = PageInfo(page_index, page_size, total, page_list)

        return self.reponse_json_success(page_info)