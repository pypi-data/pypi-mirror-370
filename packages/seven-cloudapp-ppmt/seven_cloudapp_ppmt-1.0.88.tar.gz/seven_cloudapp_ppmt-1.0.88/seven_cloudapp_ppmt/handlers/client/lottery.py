# -*- coding: utf-8 -*-
"""
:Author: HuangJianYi
:Date: 2020-05-26 17:51:04
@LastEditTime: 2025-04-29 16:42:17
@LastEditors: HuangJianYi
:Description: 抽奖  （安全问题，后续废弃使用LotteryHandler、ShakeItHandler、NewShakeItPrizeListHandler、UsePerspectiveCardHandler）
"""
import operator
from seven_cloudapp.models.seven_model import *
from seven_cloudapp.handlers.task_base import *
from seven_cloudapp.handlers.top_base import *
from seven_cloudapp.models.behavior_model import *
from seven_cloudapp.models.db_models.user.user_info_model import *
from seven_cloudapp.models.db_models.prize.prize_order_model import *
from seven_cloudapp.models.db_models.gear.gear_value_model import *
from seven_cloudapp.models.db_models.price.price_gear_model import *
from seven_cloudapp.models.db_models.coin.coin_order_model import *
from seven_cloudapp.models.db_models.machine.machine_value_model import *
from seven_cloudapp.models.db_models.task.task_info_model import *
from seven_cloudapp.models.db_models.task.task_count_model import *
from seven_cloudapp.models.db_models.prop.prop_log_model import *
from seven_cloudapp.models.db_models.user.user_detail_model import *
from seven_cloudapp.models.db_models.endbox.endbox_order_model import *
from seven_cloudapp.models.db_models.surplus.surplus_queue_model import *

from seven_cloudapp_ppmt.models.db_models.act.act_info_model import *
from seven_cloudapp_ppmt.models.db_models.act.act_prize_model import *
from seven_cloudapp_ppmt.models.db_models.prize.prize_roster_model import *
from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *


class LotteryHandler(SevenBaseHandler):
    """
    :description: 抽奖(安全问题，后续废弃使用)
    """
    @filter_check_params("prize_id,login_token,act_id,real_name,telephone")
    def get_async(self):
        """
        :description: 抽奖
        :param prize_id:奖品id
        :param login_token:登录令牌
        :param act_id:活动id
        :param real_name:用户名
        :param telephone:电话
        :param province:省
        :param city:市
        :param county:区县
        :param street:街道
        :param address:地址
        :return: 抽奖
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        prize_id = int(self.get_param("prize_id", 0))
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        province = self.get_param("province")
        city = self.get_param("city")
        county = self.get_param("county")
        street = self.get_param("street")
        address = self.get_param("address")

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"), context=self)
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        gear_value_model = GearValueModel(db_transaction=db_transaction, context=self)
        prize_roster_model = PrizeRosterModel(db_transaction=db_transaction, context=self)
        act_prize_model = ActPrizeModel(db_transaction=db_transaction, context=self)
        coin_order_model = CoinOrderModel(db_transaction=db_transaction, context=self)
        surplus_queue_model = SurplusQueueModel(db_transaction=db_transaction, context=self)
        prize_order_model = PrizeOrderModel(db_transaction=db_transaction, context=self)
        machine_value_model = MachineValueModel(db_transaction=db_transaction, context=self)
        #请求太频繁限制
        check_post_key = f"Lottery_Post_{act_id}_{open_id}_{prize_id}"
        if self.check_post(check_post_key,60) == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("UserState", "对不起，你是黑名单用户,无法抽盲盒")
        if user_info.login_token != login_token:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽盲盒")

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity("id=%s and is_release=1", params=act_id)
        if not act_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "对不起，活动不存在")

        now_date = self.get_now_datetime()
        if TimeHelper.format_time_to_datetime(now_date) < TimeHelper.format_time_to_datetime(act_info.start_date):
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        if TimeHelper.format_time_to_datetime(now_date) > TimeHelper.format_time_to_datetime(act_info.end_date):
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "活动已结束")

        act_prize = act_prize_model.get_entity_by_id(prize_id)
        if not act_prize:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoPrize", "对不起，奖品不存在")

        surplus_queue = surplus_queue_model.get_entity("app_id=%s and open_id=%s and prize_id=%s", params=[app_id, open_id, prize_id])
        if not surplus_queue:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoPrize", "对不起，请重新选择盲盒")
        if act_prize.prize_total == 0:
            surplus_queue_model.del_entity("id=%s",params=[surplus_queue.id])
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoPrize", "请重新选择盒子")

        machine_info_model = MachineInfoModel(context=self)
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=act_prize.machine_id)
        if not machine_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")

        if machine_info.sale_type == 2:
            sale_date_str = str(machine_info.sale_date)
            sale_date = TimeHelper.format_time_to_datetime(sale_date_str if sale_date_str != "1900-01-01 00:00:00" else now_date)
            if TimeHelper.format_time_to_datetime(now_date) < sale_date:
                self.redis_init().delete(check_post_key)
                china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
                return self.reponse_json_error("NoStart", "该商品" + china_sale_date + "开售,敬请期待~")

        price_gear_model = PriceGearModel(context=self)
        price_gear = price_gear_model.get_entity("id=%s", params=machine_info.price_gears_id)
        if not price_gear:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoPriceGear", "对不起，价格档位不存在")
        gear_value = gear_value_model.get_entity("act_id=%s and open_id=%s and price_gears_id=%s", params=[act_id, open_id, price_gear.id])
        if not gear_value or gear_value.current_value <= 0:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoLotteryCount", "对不起，次数不足")
        prize_order_id = 0
        #抽奖
        try:
            #创建订单
            prize_order = PrizeOrder()
            prize_order.app_id = app_id
            prize_order.open_id = open_id
            prize_order.act_id = act_id
            prize_order.order_type = 1
            prize_order.user_nick = user_info.user_nick
            prize_order.real_name = real_name
            prize_order.telephone = telephone
            prize_order.province = province
            prize_order.city = city
            prize_order.county = county
            prize_order.street = street
            prize_order.adress = address
            prize_order.create_date = now_date
            prize_order.modify_date = now_date
            prize_order.order_no = self.create_order_id()
            prize_order_id = prize_order_model.add_entity(prize_order)
            if prize_order_id <= 0:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("Error", "对不起，请重新选择")

            #录入用户奖品
            prize_roster = PrizeRoster()
            prize_roster.app_id = app_id
            prize_roster.act_id = act_id
            prize_roster.open_id = open_id
            prize_roster.machine_id = act_prize.machine_id
            prize_roster.machine_name = machine_info.machine_name
            prize_roster.machine_price = machine_info.machine_price
            prize_roster.series_id = machine_info.series_id
            prize_roster.prize_pic = act_prize.unpack_pic
            prize_roster.toys_pic = act_prize.toys_pic
            prize_roster.prize_id = act_prize.id
            prize_roster.prize_name = act_prize.prize_name
            prize_roster.prize_price = act_prize.prize_price
            prize_roster.prize_detail = act_prize.prize_detail
            prize_roster.tag_id = act_prize.tag_id
            prize_roster.user_nick = user_info.user_nick
            prize_roster.is_sku = act_prize.is_sku
            prize_roster.goods_code = act_prize.goods_code
            prize_roster.goods_code_list = act_prize.goods_code_list
            prize_roster.prize_order_no = prize_order.order_no
            prize_roster.order_status = 0
            prize_roster.create_date = now_date

            machine_value = machine_value_model.get_entity("act_id=%s and machine_id=%s and open_id=%s", params=[act_id, act_prize.machine_id, open_id])

            #添加商家对帐记录
            coin_order = None
            coin_order_set = coin_order_model.get_entity("act_id=%s and price_gears_id=%s and open_id=%s and pay_order_id=0 and surplus_count>0", "id asc", params=[act_id, machine_info.price_gears_id, open_id])
            if coin_order_set:
                coin_order_set.surplus_count = coin_order_set.surplus_count - 1
                coin_order_set.prize_ids = coin_order_set.prize_ids + "," + str(act_prize.id) if len(coin_order_set.prize_ids) > 0 else str(act_prize.id)
                coin_order = coin_order_set
            else:
                coin_order_pay = coin_order_model.get_entity("act_id=%s and price_gears_id=%s and open_id=%s and pay_order_id>0 and surplus_count>0", "id asc", params=[act_id, machine_info.price_gears_id, open_id])
                if coin_order_pay:
                    coin_order_pay.surplus_count = coin_order_pay.surplus_count - 1
                    coin_order_pay.prize_ids = coin_order_pay.prize_ids + "," + str(act_prize.id) if len(coin_order_pay.prize_ids) > 0 else str(act_prize.id)
                    coin_order = coin_order_pay

            db_transaction.begin_transaction()
            #扣除用户次数
            gear_value.current_value -= 1
            gear_value.modify_date = now_date
            gear_value_model.update_entity(gear_value)

            #录入用户开盒次数
            if not machine_value:
                machine_value = MachineValue()
                machine_value.act_id = act_id
                machine_value.app_id = app_id
                machine_value.open_id = open_id
                machine_value.machine_id = act_prize.machine_id
                machine_value.open_value = 1
                machine_value.create_date = now_date
                machine_value.modify_date = now_date
                machine_value_model.add_entity(machine_value)
            else:
                machine_value.open_value += 1
                machine_value.modify_date = now_date
                machine_value_model.update_entity(machine_value)

            if coin_order != None:
                coin_order_model.update_entity(coin_order)
                prize_roster.main_pay_order_no = coin_order.main_pay_order_no
                prize_roster.order_no = coin_order.pay_order_no
                if coin_order.pay_order_no != "":
                    prize_roster.frequency_source = 0
                else:
                    prize_roster.frequency_source = 1

            prize_roster.prize_order_id = prize_order_id
            prize_roster_model.add_entity(prize_roster)
            #库存处理
            act_prize_model.update_table("hand_out=hand_out+1,prize_total=prize_total-1", "id=%s", act_prize.id)
            surplus_queue_model.del_entity("id=%s", params=[surplus_queue.id])
            result,message = db_transaction.commit_transaction(return_detail_tuple=True)
            if not result:
                raise Exception(message)
        except Exception as ex:
            self.logging_link_error("LotteryHandler:" + str(ex))
            if prize_order_id > 0:
                prize_order_model.del_entity("id=%s", params=prize_order_id)
                self.redis_init().delete(check_post_key)
            return self.reponse_json_error("Error", "当前人数过多,请重新选择")

        result_prize = {}
        result_prize["order_no"] = prize_order.order_no
        result_prize["prize_name"] = act_prize.prize_name
        result_prize["prize_id"] = act_prize.id
        result_prize["unpack_pic"] = act_prize.unpack_pic
        result_prize["tag_id"] = act_prize.tag_id
        result_prize["prize_detail"] = self.json_loads(act_prize.prize_detail)
        if user_info.user_nick:
            length = len(user_info.user_nick)
            if length > 2:
                result_prize["user_nick"] = user_info.user_nick[0:length - 2] + "**"
            else:
                result_prize["user_nick"] = user_info.user_nick[0:1] + "*"

        behavior_model = BehaviorModel(context=self)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'openUserCount_' + str(machine_info.id), 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'openCount_' + str(machine_info.id), 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'LotteryerCount', 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'LotteryCount', 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'LotteryMoneyCount', machine_info.machine_price)
        result_prize["integral"] = self.task_lottery_points(act_info.__dict__, user_info, machine_info.machine_name, 1)

        if int(result_prize["integral"]) > 0:
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryUserCount', 1)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryCount', 1)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryRewardCount', int(result_prize["integral"]))
        self.redis_init().delete(check_post_key)
        return self.reponse_json_success(result_prize)

    def task_lottery_points(self, act_dict, user_info, machine_name, lottery_num):
        """
        :description: 抽奖送积分任务
        :param act_dict:活动信息
        :param user_info:用户信息
        :param machine_name:机台名称
        :param lottery_num:抽奖次数（大于1代表端盒抽奖）
        :return:返回赠送的积分
        :last_editors: HuangJianYi
        """
        task_info_model = TaskInfoModel(context=self)
        task_type = 17  #任务类型
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_dict['id'], task_type])
        if not task_info or task_info.is_release == 0:
            return 0
        task_config = self.json_loads(task_info.task_config)
        if not task_config:
            return 0
        send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        send_num = send_num * lottery_num
        if send_num <= 0:
            return 0
        log_title = f"抽取{machine_name}盲盒"
        user_info.surplus_integral = user_info.surplus_integral + send_num
        update_sql = f"surplus_integral=surplus_integral+{send_num}"
        send_result = TaskBaseHandler(application=self.application, request=self.request).send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 217, 2)
        if send_result == False:
            return 0

        return send_num


class NewLotteryHandler(TopBaseHandler):
    """
    :description: 拆盒
    """
    @filter_check_params("serial_no,key_id,login_token,act_id,real_name,telephone")
    def get_async(self):
        """
        :description: 拆盒
        :param key_id:key_id
        :param serial_no:序号
        :param login_token:登录令牌
        :param act_id:活动id
        :param real_name:用户名
        :param telephone:电话
        :param province:省
        :param city:市
        :param county:区县
        :param street:街道
        :param address:地址
        :return: 抽奖
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        serial_no = int(self.get_param("serial_no", 1))
        key_id = self.get_param("key_id")
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        province = self.get_param("province")
        city = self.get_param("city")
        county = self.get_param("county")
        street = self.get_param("street")
        address = self.get_param("address")

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"), context=self)
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        gear_value_model = GearValueModel(db_transaction=db_transaction, context=self)
        prize_roster_model = PrizeRosterModel(db_transaction=db_transaction, context=self)
        act_prize_model = ActPrizeModel(db_transaction=db_transaction, context=self)
        coin_order_model = CoinOrderModel(db_transaction=db_transaction, context=self)
        surplus_queue_model = SurplusQueueModel(db_transaction=db_transaction, context=self)
        prize_order_model = PrizeOrderModel(db_transaction=db_transaction, context=self)
        machine_value_model = MachineValueModel(db_transaction=db_transaction, context=self)

        #请求太频繁限制
        check_post_key = f"Lottery_Post_{act_id}_{open_id}_{key_id}_{serial_no}"
        if self.check_post(check_post_key, 60) == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("UserState", "对不起，你是黑名单用户,无法抽盲盒")
        if user_info.login_token != login_token:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽盲盒")

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity("id=%s and is_release=1", params=act_id)
        if not act_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "活动不存在")

        now_date = self.get_now_datetime()
        if TimeHelper.format_time_to_datetime(now_date) < TimeHelper.format_time_to_datetime(act_info.start_date):
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        if TimeHelper.format_time_to_datetime(now_date) > TimeHelper.format_time_to_datetime(act_info.end_date):
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "活动已结束")

        redis_minmachinelist_key = f"minbox_list_{str(open_id)}_{str(key_id)}"
        min_machine_list = self.redis_init().get(redis_minmachinelist_key)
        min_machine_list = json.loads(min_machine_list) if min_machine_list != None else {}
        prize_id = min_machine_list[str(serial_no)] if str(serial_no) in min_machine_list.keys() else 0
        if prize_id <= 0:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("Error", "请重新选择盒子")

        act_prize = act_prize_model.get_entity_by_id(prize_id)
        if not act_prize:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoPrize", "对不起，奖品不存在")

        surplus_queue = surplus_queue_model.get_entity("open_id=%s and prize_id=%s and key_id=%s", params=[open_id, prize_id, key_id])
        if not surplus_queue:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoPrize", "请重新选择盒子")
        if act_prize.prize_total == 0:
            surplus_queue_model.del_entity("id=%s",params=[surplus_queue.id])
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoPrize", "请重新选择盒子")
        machine_info_model = MachineInfoModel(context=self)
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=act_prize.machine_id)
        if not machine_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoMachine", "盒子不存在")

        if machine_info.sale_type == 2:
            sale_date_str = str(machine_info.sale_date)
            sale_date = TimeHelper.format_time_to_datetime(sale_date_str if sale_date_str != "1900-01-01 00:00:00" else now_date)
            if TimeHelper.format_time_to_datetime(now_date) < sale_date:
                self.redis_init().delete(check_post_key)
                china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
                return self.reponse_json_error("NoStart", "该商品" + china_sale_date + "开售,敬请期待~")
        access_token = ""
        #判断是会员积分抽还是次数抽
        shop_member_integral = 0
        if machine_info.machine_type != 2:
            app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
            if app_info:
                access_token = app_info.access_token
            result = self.check_is_member(access_token)
            if not result:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("No_Member", "不是会员不能抽盒")
            invoke_result_data = self.get_crm_point_available(self.get_taobao_param().mix_nick, access_token)
            if invoke_result_data.success == False:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            shop_member_integral = invoke_result_data.data
            if shop_member_integral < int(machine_info.machine_price.split('.')[0]):
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("NoLotteryCount", "会员积分不足")
        else:

            price_gear_model = PriceGearModel(context=self)
            price_gear = price_gear_model.get_entity("id=%s", params=machine_info.price_gears_id)
            if not price_gear:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("NoPriceGear", "价格档位不存在")
            gear_value = gear_value_model.get_entity("act_id=%s and open_id=%s and price_gears_id=%s", params=[act_id, open_id, price_gear.id])
            if not gear_value or gear_value.current_value <= 0:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("NoLotteryCount", "次数不足")
        prize_order_id = 0
        #抽奖
        try:
            #创建订单
            prize_order = PrizeOrder()
            prize_order.app_id = app_id
            prize_order.open_id = open_id
            prize_order.act_id = act_id
            prize_order.order_type = 1
            prize_order.user_nick = user_info.user_nick
            prize_order.real_name = real_name
            prize_order.telephone = telephone
            prize_order.province = province
            prize_order.city = city
            prize_order.county = county
            prize_order.street = street
            prize_order.adress = address
            prize_order.create_date = now_date
            prize_order.modify_date = now_date
            prize_order.order_no = self.create_order_id()
            prize_order_id = prize_order_model.add_entity(prize_order)
            if prize_order_id <= 0:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("Error", "对不起，请重新选择")

            #录入用户奖品
            prize_roster = PrizeRoster()
            prize_roster.app_id = app_id
            prize_roster.act_id = act_id
            prize_roster.open_id = open_id
            prize_roster.machine_id = act_prize.machine_id
            prize_roster.machine_type = machine_info.machine_type
            prize_roster.machine_name = machine_info.machine_name
            prize_roster.machine_price = machine_info.machine_price
            prize_roster.series_id = machine_info.series_id
            prize_roster.prize_pic = act_prize.unpack_pic
            prize_roster.toys_pic = act_prize.toys_pic
            prize_roster.prize_id = act_prize.id
            prize_roster.prize_name = act_prize.prize_name
            prize_roster.prize_price = act_prize.prize_price
            prize_roster.prize_detail = act_prize.prize_detail
            prize_roster.tag_id = act_prize.tag_id
            prize_roster.user_nick = user_info.user_nick
            prize_roster.is_sku = act_prize.is_sku
            prize_roster.goods_code = act_prize.goods_code
            prize_roster.goods_code_list = act_prize.goods_code_list
            prize_roster.prize_order_no = prize_order.order_no
            prize_roster.order_status = 0
            prize_roster.create_date = now_date
            prize_roster.remark = self.json_dumps({"key_id": key_id, "serial_no": serial_no})

            machine_value = machine_value_model.get_entity("act_id=%s and machine_id=%s and open_id=%s", params=[act_id, act_prize.machine_id, open_id])

            #添加商家对帐记录
            coin_order = None
            if machine_info.machine_type == 2:
                coin_order_set = coin_order_model.get_entity("act_id=%s and price_gears_id=%s and open_id=%s and pay_order_id=0 and surplus_count>0", "pay_date asc", params=[act_id, machine_info.price_gears_id, open_id])
                if coin_order_set:
                    coin_order_set.surplus_count = coin_order_set.surplus_count - 1
                    coin_order_set.prize_ids = coin_order_set.prize_ids + "," + str(act_prize.id) if len(coin_order_set.prize_ids) > 0 else str(act_prize.id)
                    coin_order = coin_order_set
                else:
                    coin_order_pay = coin_order_model.get_entity("act_id=%s and price_gears_id=%s and open_id=%s and pay_order_id>0 and surplus_count>0", "pay_date asc", params=[act_id, machine_info.price_gears_id, open_id])
                    if coin_order_pay:
                        coin_order_pay.surplus_count = coin_order_pay.surplus_count - 1
                        coin_order_pay.prize_ids = coin_order_pay.prize_ids + "," + str(act_prize.id) if len(coin_order_pay.prize_ids) > 0 else str(act_prize.id)
                        coin_order = coin_order_pay

            if machine_info.machine_type != 2:
                invoke_result_data = self.change_crm_point(open_id, 1, 1, int(machine_info.machine_price.split('.')[0]), access_token, activity_id=act_info.id, activity_name=f"在线抽盒机-抽{machine_info.machine_name}盲盒", is_log=True)
                if invoke_result_data.success == False:
                    self.redis_init().delete(check_post_key)
                    return self.reponse_json_error("Error", invoke_result_data.error_message)
                lottery_value_log_model = LotteryValueLogModel(context=self)
                lottery_value_log = LotteryValueLog()
                lottery_value_log.app_id = user_info.app_id
                lottery_value_log.act_id = user_info.act_id
                lottery_value_log.open_id = user_info.open_id
                lottery_value_log.user_nick = user_info.user_nick
                lottery_value_log.log_title = f"抽{machine_info.machine_name}盲盒"
                lottery_value_log.log_info = {"record_id": invoke_result_data.data["record_id"], "machine_id": machine_info.id}
                lottery_value_log.currency_type = 4
                lottery_value_log.source_type = 4
                lottery_value_log.change_type = 402
                lottery_value_log.operate_type = 1
                lottery_value_log.current_value = -int(machine_info.machine_price.split('.')[0])
                lottery_value_log.history_value = 0
                lottery_value_log.create_date = self.get_now_datetime()
                lottery_value_log_model.add_entity(lottery_value_log)

            db_transaction.begin_transaction()

            if machine_info.machine_type == 2:
                #扣除用户次数
                gear_value_model.update_table("current_value=current_value-1,modify_date=%s","id=%s", params=[now_date, gear_value.id])

            #录入用户开盒次数
            if not machine_value:
                machine_value = MachineValue()
                machine_value.act_id = act_id
                machine_value.app_id = app_id
                machine_value.open_id = open_id
                machine_value.machine_id = act_prize.machine_id
                machine_value.open_value = 1
                machine_value.create_date = now_date
                machine_value.modify_date = now_date
                machine_value_model.add_entity(machine_value)
            else:
                machine_value.open_value += 1
                machine_value.modify_date = now_date
                machine_value_model.update_entity(machine_value)

            if coin_order != None:
                coin_order_model.update_entity(coin_order)
                prize_roster.main_pay_order_no = coin_order.main_pay_order_no
                prize_roster.order_no = coin_order.pay_order_no
                if coin_order.pay_order_no != "":
                    prize_roster.frequency_source = 0
                else:
                    prize_roster.frequency_source = 1

            prize_roster.prize_order_id = prize_order_id
            prize_roster_model.add_entity(prize_roster)
            #库存处理
            act_prize_model.update_table("hand_out=hand_out+1,prize_total=prize_total-1", "id=%s", act_prize.id)
            surplus_queue_model.del_entity("id=%s", params=[surplus_queue.id])
            result,message = db_transaction.commit_transaction(return_detail_tuple=True)
            if not result:
                raise Exception(message)
        except Exception as ex:
            self.logging_link_error("LotteryHandler:" + str(ex))
            if prize_order_id > 0:
                prize_order_model.del_entity("id=%s", params=prize_order_id)
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("Error", "当前人数过多,请重新选择")

        result_prize = {}
        result_prize["order_no"] = prize_order.order_no
        result_prize["prize_name"] = act_prize.prize_name
        result_prize["unpack_pic"] = act_prize.unpack_pic
        result_prize["tag_id"] = act_prize.tag_id
        result_prize["prize_detail"] = self.json_loads(act_prize.prize_detail)
        if user_info.user_nick:
            length = len(user_info.user_nick)
            if length > 2:
                result_prize["user_nick"] = user_info.user_nick[0:length - 2] + "**"
            else:
                result_prize["user_nick"] = user_info.user_nick[0:1] + "*"

        behavior_model = BehaviorModel(context=self)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'openUserCount_' + str(machine_info.id), 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'openCount_' + str(machine_info.id), 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'LotteryerCount', 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'LotteryCount', 1)
        if machine_info.machine_type == 2:
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'LotteryMoneyCount', machine_info.machine_price)
        result_prize["integral"], result_prize["currency_type"] = self.task_lottery_points(act_info.__dict__, user_info, machine_info.machine_name, 1)

        if int(result_prize["integral"]) > 0:
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryUserCount', 1)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryCount', 1)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryRewardCount', int(result_prize["integral"]))
        self.redis_init().delete(check_post_key)
        return self.reponse_json_success(result_prize)

    def task_lottery_points(self, act_dict, user_info, machine_name, lottery_num):
        """
        :description: 抽奖送积分任务
        :param act_dict:活动信息
        :param user_info:用户信息
        :param machine_name:机台名称
        :param lottery_num:抽奖次数（大于1代表端盒抽奖）
        :return:返回赠送的积分
        :last_editors: HuangJianYi
        """
        task_info_model = TaskInfoModel(context=self)
        task_type = 17  #任务类型
        task_base = TaskBaseHandler(application=self.application, request=self.request)
        currency_type = task_base.get_task_currency_type(act_dict['task_currency_type'], task_type)
        task_info = task_info_model.get_entity("act_id=%s and task_type=%s", params=[act_dict['id'], task_type])
        if not task_info or task_info.is_release == 0 or act_dict["is_task"] == 0:
            return 0,currency_type
        task_config = self.json_loads(task_info.task_config)
        if not task_config:
            return 0,currency_type
        send_num = int(task_config["reward_value"]) if task_config.__contains__("reward_value") else 0
        send_num = send_num * lottery_num
        if send_num <= 0:
            return 0,currency_type

        log_title = f"抽取{machine_name}盲盒"
        log_desc = ""
        update_sql = ""
        if currency_type == 4:
            app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=act_dict["app_id"])
            if app_info:
                access_token = app_info.access_token
            result = self.check_is_member(access_token)
            if not result:
                return 0,currency_type    
            invoke_result_data = self.change_crm_point(user_info.open_id, 1, 0, send_num, access_token, activity_id=act_dict['id'], activity_name=f"在线抽盒机-抽盒送积分", is_log=True)
            if invoke_result_data.success == False:
                log_desc = invoke_result_data.error_message
        else:
            user_info.surplus_integral = user_info.surplus_integral + send_num
            update_sql = f"surplus_integral=surplus_integral+{send_num}"
        send_result = task_base.send_lottery_value(log_title, user_info, update_sql, send_num, act_dict, 2, 217, currency_type, log_desc=log_desc)
        if send_result == False:
            return 0,currency_type

        return send_num,currency_type


class LotteryAllHandler(TopBaseHandler):
    """
    :description: 端盒抽奖
    """
    @filter_check_params("machine_id,login_token,act_id,real_name,telephone")
    def get_async(self):
        """
        :description: 端盒抽奖
        :param login_token:登录令牌
        :param act_id:活动id
        :param machine_id:中盒id
        :param real_name:用户名
        :param telephone:电话
        :param province:省
        :param city:市
        :param county:区县
        :param street:街道
        :param address:地址
        :return: 抽奖
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        machine_id = int(self.get_param("machine_id", 0))
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        real_name = self.get_param("real_name")
        telephone = self.get_param("telephone")
        province = self.get_param("province")
        city = self.get_param("city")
        county = self.get_param("county")
        street = self.get_param("street")
        address = self.get_param("address")

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"), context=self)
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        gear_value_model = GearValueModel(db_transaction=db_transaction, context=self)
        prize_roster_model = PrizeRosterModel(db_transaction=db_transaction, context=self)
        act_prize_model = ActPrizeModel(db_transaction=db_transaction, context=self)
        coin_order_model = CoinOrderModel(db_transaction=db_transaction, context=self)
        prize_order_model = PrizeOrderModel(db_transaction=db_transaction, context=self)
        machine_value_model = MachineValueModel(db_transaction=db_transaction, context=self)
        endbox_order_model = EndboxOrderModel(db_transaction=db_transaction, context=self)

        #请求太频繁限制
        check_post_key = f"LotteryAll_Post_{act_id}_{str(open_id)}_{str(machine_id)}"
        if self.check_post(check_post_key,60) == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("UserState", "对不起，你是黑名单用户,无法抽盲盒")
        if user_info.login_token != login_token:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽盲盒")

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity("id=%s and is_release=1", params=act_id)
        if not act_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "对不起，活动不存在")

        now_date = self.get_now_datetime()
        if TimeHelper.format_time_to_datetime(now_date) < TimeHelper.format_time_to_datetime(act_info.start_date):
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        if TimeHelper.format_time_to_datetime(now_date) > TimeHelper.format_time_to_datetime(act_info.end_date):
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoAct", "活动已结束")
        machine_info_model = MachineInfoModel(context=self)
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=machine_id)
        if not machine_info:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")
        if machine_info.is_buy_endbox == 0:
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("NoOpen", "对不起，未开启购买端盒")
        if machine_info.sale_type == 2:
            sale_date_str = str(machine_info.sale_date)
            sale_date = TimeHelper.format_time_to_datetime(sale_date_str if sale_date_str != "1900-01-01 00:00:00" else now_date)
            if TimeHelper.format_time_to_datetime(now_date) < sale_date:
                self.redis_init().delete(check_post_key)
                china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
                return self.reponse_json_error("NoStart", "该商品" + china_sale_date + "开售,敬请期待~")
        access_token = ""
        #判断是会员积分抽还是次数抽
        shop_member_integral = 0
        if machine_info.machine_type != 2:
            app_info = AppInfoModel(context=self).get_entity("app_id=%s", params=app_id)
            if app_info:
                access_token = app_info.access_token
            result = self.check_is_member(access_token)
            if not result:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("No_Member", "不是会员，不能抽盒")
            invoke_result_data = self.get_crm_point_available(self.get_taobao_param().mix_nick, access_token)
            if invoke_result_data.success == False:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error(invoke_result_data.error_code, invoke_result_data.error_message)
            shop_member_integral = invoke_result_data.data
            if shop_member_integral < int(machine_info.machine_price.split('.')[0]) * machine_info.specs_type:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("NoLotteryCount", "对不起，会员积分不足")
        else:
            price_gear_model = PriceGearModel(context=self)
            price_gear = price_gear_model.get_entity("id=%s", params=machine_info.price_gears_id)
            if not price_gear:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("NoPriceGear", "对不起，价格档位不存在")
            gear_value = gear_value_model.get_entity("act_id=%s and open_id=%s and price_gears_id=%s", params=[act_id, open_id, price_gear.id])
            if not gear_value or gear_value.current_value < machine_info.specs_type:
                self.redis_init().delete(check_post_key)
                return self.reponse_json_error("NoLotteryCount", "对不起，次数不足")

        queue_name = f"PrizeList_Queue_{str(machine_id)}"
        identifier = self.acquire_lock(queue_name)
        if isinstance(identifier, bool):
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("UserLimit", "当前人数过多,请稍后再来")
        condition = "act_id=%s AND machine_id=%s AND is_release=1 AND surplus>0 AND probability>0"
        act_prize_list = act_prize_model.get_list(condition, params=[act_id, machine_id])
        if len(act_prize_list) <= 0:
            self.redis_init().delete(check_post_key)
            self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoPrize", "对不起，该盲盒已售罄")
        if len(act_prize_list) < machine_info.specs_type:
            self.redis_init().delete(check_post_key)
            self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoPrize", "对不起，库存不足")
        act_prize_id_list = []
        random_Prize_dict_list = {}
        for act_prize in act_prize_list:
            random_Prize_dict_list[act_prize.id] = act_prize.probability
        for i in range(machine_info.specs_type):
            prize_id = self.random_weight(random_Prize_dict_list)
            act_prize_id_list.append(prize_id)
            del random_Prize_dict_list[prize_id]
        act_prize_process_list = [act_prize for act_prize in act_prize_list if act_prize.id in act_prize_id_list] if len(act_prize_id_list) > 0 else []
        if len(act_prize_process_list) <= 0:
            self.redis_init().delete(check_post_key)
            self.release_lock(queue_name, identifier)
            return self.reponse_json_error("NoPrize", "对不起，库存不足")
        gear_value_result = None
        #抽奖
        try:
            if machine_info.machine_type == 2:
                #扣除用户次数
                gear_value_result = gear_value_model.update_table(f"current_value=current_value-{machine_info.specs_type}", "id=%s and current_value=%s", params=[gear_value.id, gear_value.current_value])
                if gear_value_result == False:
                    self.redis_init().delete(check_post_key)
                    self.release_lock(queue_name, identifier)
                    return self.reponse_json_error("Error", "当前人数过多,请重新购买端盒")
            else:
                invoke_result_data = self.change_crm_point(open_id, 1, 1, int(machine_info.machine_price.split('.')[0]) * machine_info.specs_type, access_token, activity_id=act_info.id, activity_name=f"在线抽盒机-抽{machine_info.machine_name}盲盒", is_log=True)
                if invoke_result_data.success == False:
                    self.redis_init().delete(check_post_key)
                    self.release_lock(queue_name, identifier)
                    return self.reponse_json_error("Error", invoke_result_data.error_message)
                lottery_value_log_model = LotteryValueLogModel(context=self)
                lottery_value_log = LotteryValueLog()
                lottery_value_log.app_id = user_info.app_id
                lottery_value_log.act_id = user_info.act_id
                lottery_value_log.open_id = user_info.open_id
                lottery_value_log.user_nick = user_info.user_nick
                lottery_value_log.log_title = f"抽{machine_info.machine_name}盲盒"
                lottery_value_log.log_info = {"record_id": invoke_result_data.data["record_id"], "machine_id": machine_info.id}
                lottery_value_log.currency_type = 4
                lottery_value_log.source_type = 4
                lottery_value_log.change_type = 402
                lottery_value_log.operate_type = 1
                lottery_value_log.current_value = -int(machine_info.machine_price.split('.')[0]) * machine_info.specs_type
                lottery_value_log.history_value = 0
                lottery_value_log.create_date = self.get_now_datetime()
                lottery_value_log_model.add_entity(lottery_value_log)

            #创建订单
            prize_order = PrizeOrder()
            prize_order.app_id = app_id
            prize_order.open_id = open_id
            prize_order.act_id = act_id
            prize_order.order_type = 2
            prize_order.user_nick = user_info.user_nick
            prize_order.real_name = real_name
            prize_order.telephone = telephone
            prize_order.province = province
            prize_order.city = city
            prize_order.county = county
            prize_order.street = street
            prize_order.adress = address
            prize_order.create_date = now_date
            prize_order.modify_date = now_date
            prize_order.order_no = self.create_order_id()
            prize_order_id = prize_order_model.add_entity(prize_order)
            if prize_order_id <= 0:
                self.redis_init().delete(check_post_key)
                self.release_lock(queue_name, identifier)
                return self.reponse_json_error("Error", "对不起，请重新选择")

            coin_order_id_list = []
            coin_order_list = []
            if machine_info.machine_type == 2:
                coin_order_list = coin_order_model.get_list("act_id=%s and price_gears_id=%s and open_id=%s and surplus_count>0", order_by="pay_date asc", params=[act_id, machine_info.price_gears_id, open_id])
                if len(coin_order_list) > 0:
                    count = 0
                    for coin_order in coin_order_list:
                        for i in range(coin_order.surplus_count):
                            if count == len(act_prize_process_list):
                                break
                            count += 1
                            coin_order_id_list.append(coin_order.id)
            #录入用户奖品
            coin_id_prize_id_dict = {}
            prize_roster_list = []
            result_prize_list = []
            for act_prize in act_prize_process_list:
                act_prize.surplus = act_prize.surplus - 1
                act_prize.prize_total = act_prize.prize_total - 1
                prize_roster = PrizeRoster()
                prize_roster.app_id = app_id
                prize_roster.act_id = act_id
                prize_roster.open_id = open_id
                prize_roster.machine_id = act_prize.machine_id
                prize_roster.machine_type = machine_info.machine_type
                prize_roster.machine_name = machine_info.machine_name
                prize_roster.machine_price = machine_info.machine_price
                prize_roster.series_id = machine_info.series_id
                prize_roster.prize_pic = act_prize.unpack_pic
                prize_roster.toys_pic = act_prize.toys_pic
                prize_roster.prize_id = act_prize.id
                prize_roster.prize_name = act_prize.prize_name
                prize_roster.prize_price = act_prize.prize_price
                prize_roster.prize_detail = act_prize.prize_detail
                prize_roster.tag_id = act_prize.tag_id
                prize_roster.user_nick = user_info.user_nick
                prize_roster.is_sku = act_prize.is_sku
                prize_roster.goods_code = act_prize.goods_code
                prize_roster.goods_code_list = act_prize.goods_code_list
                prize_roster.prize_order_id = prize_order_id
                prize_roster.prize_order_no = prize_order.order_no
                prize_roster.order_status = 0
                prize_roster.create_date = now_date

                if len(coin_order_id_list) > 0:
                    now_coin_order_id = coin_order_id_list.pop(0)
                    # self.logging_link_error("coin_order_id:" + str(now_coin_order_id))
                    coin_orders = [coin_order for coin_order in coin_order_list if coin_order.id == now_coin_order_id]
                    if len(coin_orders) > 0:
                        prize_roster.main_pay_order_no = coin_orders[0].main_pay_order_no
                        prize_roster.order_no = coin_orders[0].pay_order_no
                        prize_roster.frequency_source = 0 if coin_orders[0].pay_order_no != "" else 1

                        if str(coin_orders[0].id) in coin_id_prize_id_dict.keys():
                            coin_id_prize_id_dict[str(coin_orders[0].id)].append(str(act_prize.id))
                        else:
                            coin_id_prize_id_dict[str(coin_orders[0].id)] = [str(act_prize.id)]

                prize_roster_list.append(prize_roster)

                result_prize = {}
                result_prize["order_no"] = prize_order.order_no
                result_prize["prize_name"] = act_prize.prize_name
                result_prize["prize_id"] = act_prize.id
                result_prize["unpack_pic"] = act_prize.unpack_pic
                result_prize["tag_id"] = act_prize.tag_id
                result_prize["prize_detail"] = self.json_loads(act_prize.prize_detail)
                if user_info.user_nick:
                    result_prize["user_nick"] = user_info.user_nick[0:len(user_info.user_nick) - 2] + "**" if len(user_info.user_nick) > 2 else user_info.user_nick[0:1] + "*"
                result_prize_list.append(result_prize)

            #添加对账单对应的奖品
            if coin_order_list and len(coin_order_list) > 0:
                for coin_order in coin_order_list:
                    if str(coin_order.id) in coin_id_prize_id_dict.keys():
                        coin_order.surplus_count = coin_order.surplus_count - len(coin_id_prize_id_dict[str(coin_order.id)])
                        prize_ids = ','.join(str(prize_id) for prize_id in coin_id_prize_id_dict[str(coin_order.id)])
                        coin_order.prize_ids = coin_order.prize_ids + "," + prize_ids if len(coin_order.prize_ids) > 0 else prize_ids

            machine_value = machine_value_model.get_entity("act_id=%s and machine_id=%s and open_id=%s", params=[act_id, act_prize.machine_id, open_id])

            endbox_order = EndboxOrder()
            endbox_order.order_no = prize_order.order_no
            endbox_order.app_id = app_id
            endbox_order.act_id = act_id
            endbox_order.open_id = open_id
            endbox_order.user_nick = user_info.user_nick
            endbox_order.series_id = machine_info.series_id
            endbox_order.machine_id = machine_info.id
            endbox_order.machine_type = machine_info.machine_type
            endbox_order.machine_name = machine_info.machine_name
            endbox_order.specs_type = machine_info.specs_type
            endbox_order.endbox_price = round(machine_info.specs_type * decimal.Decimal(machine_info.machine_price), 2)
            endbox_order.create_date = now_date
            endbox_order.modify_date = now_date

            db_transaction.begin_transaction()
            #录入用户开盒次数
            if not machine_value:
                machine_value = MachineValue()
                machine_value.act_id = act_id
                machine_value.app_id = app_id
                machine_value.open_id = open_id
                machine_value.machine_id = act_prize.machine_id
                machine_value.open_value = machine_info.specs_type
                machine_value.create_date = now_date
                machine_value.modify_date = now_date
                machine_value_model.add_entity(machine_value)
            else:
                machine_value.open_value += machine_info.specs_type
                machine_value.modify_date = now_date
                machine_value_model.update_entity(machine_value)

            act_prize_model.update_list(act_prize_process_list, "surplus,prize_total")

            if len(coin_order_list) > 0:
                coin_order_model.update_list(coin_order_list, "surplus_count,prize_ids")

            endbox_order_model.add_entity(endbox_order)

            prize_roster_model.add_list(prize_roster_list)

            result, message = db_transaction.commit_transaction(return_detail_tuple=True)
            if not result:
                raise Exception(message)
        except Exception as ex:
            self.logging_link_error("LotteryAllHandler:" + str(ex))
            self.release_lock(queue_name, identifier)
            if prize_order_id > 0:
                prize_order_model.del_entity("id=%s", params=prize_order_id)
            if gear_value_result:
                gear_value_model.update_table(f"current_value=current_value+{machine_info.specs_type}", "id=%s", params=[gear_value.id])
            self.redis_init().delete(check_post_key)
            return self.reponse_json_error("Error", "当前人数过多,请重新购买端盒")

        behavior_model = BehaviorModel(context=self)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'EndBoxLotteryerCount', 1)
        behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'EndBoxLotteryCount', 1)
        if machine_info.machine_type == 2:
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'EndBoxLotteryMoneyCount', endbox_order.endbox_price)

        result = {}
        result["prize_list"] = sorted(result_prize_list, key=operator.itemgetter('tag_id'), reverse=True)
        result["integral"],result["currency_type"] = NewLotteryHandler(application=self.application, request=self.request).task_lottery_points(act_info.__dict__, user_info, machine_info.machine_name, machine_info.specs_type)

        if int(result["integral"]) > 0:
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryUserCount', 1)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryCount', 1)
            behavior_model.report_behavior_log(app_id, act_id, open_id, act_info.owner_open_id, 'TaskLotteryRewardCount', int(result["integral"]))
        self.release_lock(queue_name, identifier)
        self.redis_init().delete(check_post_key)
        return self.reponse_json_success(result)


class ShakeItHandler(SevenBaseHandler):
    """
    :description: 晃一晃(安全问题，后续废弃使用)
    """
    @filter_check_params("prize_id,key_id,login_token,act_id")
    def get_async(self):
        """
        :description: 晃一晃
        :param prize_id:奖品id
        :param key_id:key_id
        :param login_token:登录令牌
        :param act_id:活动id
        :param serial_no:serial_no
        :param is_use_prop:是否使用提示卡
        :return: dict
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        prize_id = int(self.get_param("prize_id", 0))
        key_id = int(self.get_param("key_id", 0))
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        serial_no = int(self.get_param("serial_no", 0))
        is_use_prop = int(self.get_param("is_use_prop", 0))

        user_info_model = UserInfoModel(context=self)
        act_info_model = ActInfoModel(context=self)
        act_prize_model = ActPrizeModel(context=self)
        surplus_queue_model = SurplusQueueModel(context=self)
        user_detail_model = UserDetailModel(context=self)
        prop_log_model = PropLogModel(context=self)
        # self.logging_link_info(str(serial_no) + "【serial_no】")
        info = {}
        info["prize_name"] = ""
        info["prize_id"] = ""
        info["tips"] = ""
        info["is_limit"] = 1

        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.reponse_json_error("UserState", "对不起，你是黑名单用户,无法拆盒子")
        if user_info.login_token != login_token:
            return self.reponse_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽盲盒")

        user_detail = None
        if is_use_prop == 1:
            user_detail = user_detail_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
            if not user_detail or user_detail.tips_card_count <= 0:
                return self.reponse_json_error("Error", "提示卡数量不足")
            use_perspectivecard = self.redis_init().get(f"use_perspectivecard:{str(open_id)}_{str(key_id)}_{str(serial_no)}")
            if use_perspectivecard:
                return self.reponse_json_error("Error", "您已使用透视卡,不要浪费噢~")

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity("id=%s and is_release=1", params=[act_id])
        if not act_info:
            return self.reponse_json_error("NoAct", "对不起，活动不存在")

        now_date = self.get_now_datetime()
        if TimeHelper.format_time_to_datetime(now_date) < TimeHelper.format_time_to_datetime(act_info.start_date):
            return self.reponse_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        if TimeHelper.format_time_to_datetime(now_date) > TimeHelper.format_time_to_datetime(act_info.end_date):
            return self.reponse_json_error("NoAct", "活动已结束")

        act_prize = act_prize_model.get_entity_by_id(prize_id)
        if not act_prize:
            return self.reponse_json_error("NoPrize", "对不起，奖品不存在")

        surplus_queue = surplus_queue_model.get_entity("open_id=%s and prize_id=%s", params=[open_id, prize_id])
        if not surplus_queue or act_prize.prize_total == 0:
            return self.reponse_json_error("NoPrize", "对不起，请重新选择盲盒")

        machine_info_model = MachineInfoModel(context=self)
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=act_prize.machine_id)
        if not machine_info:
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")
        if machine_info.sale_type == 2:
            sale_date = TimeHelper.format_time_to_datetime(machine_info.sale_date)
            if TimeHelper.format_time_to_datetime(now_date) < sale_date:
                china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
                return self.reponse_json_error("NoStart", "该商品" + china_sale_date + "开售,敬请期待~")
        if config.get_value("check_prop",False) == True:
            price_gear_model = PriceGearModel(context=self)
            gear_value_model = GearValueModel(context=self)
            price_gear = price_gear_model.get_entity("id=%s", params=machine_info.price_gears_id)
            if not price_gear:
                return self.reponse_json_error("NoPriceGear", "对不起，价格档位不存在")
            gear_value = gear_value_model.get_entity("act_id=%s and open_id=%s and price_gears_id=%s", params=[act_id, open_id, price_gear.id])
            if not gear_value or gear_value.current_value <= 0:
                return self.reponse_json_error("NoLotteryCount", "对不起，次数不足,请先购买")
        shakebox_tips_list = self.json_loads(act_info.shakebox_tips)
        if len(shakebox_tips_list) <= 0:
            info["tips"] = act_info.exceed_tips
            return self.reponse_json_success(info)

        incre_key = str(prize_id) + "-" + str(serial_no)
        redis_num_key = "shakebox_tipsnumlist_" + str(open_id) + "_" + str(act_prize.machine_id) + "_" + str(key_id)
        shakebox_tipsnumlist = self.redis_init().get(redis_num_key)
        redis_useprop_key = f"shakebox_usepropcount_{str(open_id)}_{str(act_prize.machine_id)}_{str(key_id)}"
        shakebox_useproplist = self.redis_init().get(redis_useprop_key)

        shakebox_tipsnumlist = self.json_loads(shakebox_tipsnumlist) if shakebox_tipsnumlist != None else {}
        shakebox_useproplist = self.json_loads(shakebox_useproplist) if shakebox_useproplist != None else {}
        ran_num = 0
        if is_use_prop == 1:
            useprop_num = shakebox_useproplist[incre_key] if incre_key in shakebox_useproplist.keys() else 0
            if int(useprop_num) > 0:
                return self.reponse_json_error("Error", "只能使用一张提示卡")
            ran_num = 0
        else:
            num = shakebox_tipsnumlist[incre_key] if incre_key in shakebox_tipsnumlist.keys() else 0
            if int(num) >= int(act_info.shakebox_tips_num):
                info["tips"] = act_info.exceed_tips
                return self.reponse_json_success(info)
            ran_num_list = []
            for i in range(len(shakebox_tips_list)):
                if i == 0:
                    for j in range(7):
                        ran_num_list.append(i)
                else:
                    ran_num_list.append(i)
            ran_num = random.randint(0, int(len(ran_num_list) - 1))
            ran_num = int(ran_num_list[ran_num])

        # self.logging_link_info(str(ran_num_list)+"--" + str(ran_num) + "【ran_num_list】")
        if ran_num == 0:
            redis_prizelist_key = "shakebox_tipsprizelist_" + str(open_id) + "_" + str(act_prize.machine_id) + "_" + str(key_id)
            shakebox_tipsprizelist = self.redis_init().get(redis_prizelist_key)
            if shakebox_tipsprizelist != None:
                shakebox_tipsprizelist = self.json_loads(shakebox_tipsprizelist)
            else:
                shakebox_tipsprizelist = {}
            prize_list = shakebox_tipsprizelist[incre_key] if incre_key in shakebox_tipsprizelist.keys() else []
            cur_prize = None
            exclude_Prizeid_list = [prize_id]
            if len(prize_list) > 0:
                exclude_Prizeid_list.extend(prize_list)
            exclude_Prizeid_ids = ','.join(str(prize_id) for prize_id in exclude_Prizeid_list)
            condition = f"machine_id={act_prize.machine_id} and id not in ({exclude_Prizeid_ids}) and is_release=1 and tag_id=1"
            cur_prize = act_prize_model.get_entity(condition, order_by="RAND()")
            if cur_prize is not None:
                info["tips"] = shakebox_tips_list[0].replace("XX", cur_prize.prize_name)
                info["prize_name"] = cur_prize.prize_name
                info["prize_id"] = cur_prize.id
                info["is_limit"] = 0
                prize_list.append(cur_prize.id)
                if is_use_prop == 0:
                    shakebox_tipsnumlist[incre_key] = int(num + 1)
                    self.redis_init().set(redis_num_key, self.json_dumps(shakebox_tipsnumlist), ex=3600 * 1)
                else:
                    prop_log = PropLog()
                    prop_log.app_id = app_id
                    prop_log.act_id = act_id
                    prop_log.open_id = open_id
                    prop_log.user_nick = user_info.user_nick
                    prop_log.change_type = 3
                    prop_log.operate_type = 1
                    prop_log.prop_type = 3
                    prop_log.machine_name = machine_info.machine_name
                    prop_log.specs_type = machine_info.specs_type
                    prop_log.operate_value = 1
                    prop_log.history_value = user_detail.tips_card_count
                    prop_log.title = f"使用提示卡排除奖品:{cur_prize.prize_name}"
                    prop_log.remark = info
                    prop_log.create_date_int = SevenHelper.get_now_day_int()
                    prop_log.create_date = self.get_now_datetime()
                    prop_log_model.add_entity(prop_log)
                    user_detail_model.update_table("tips_card_count=tips_card_count-1", "open_id=%s and act_id=%s", params=[open_id, act_id])
                    shakebox_useproplist[incre_key] = int(useprop_num + 1)
                    self.redis_init().set(redis_useprop_key, self.json_dumps(shakebox_useproplist), ex=3600 * 1)

                shakebox_tipsprizelist[incre_key] = prize_list
                self.redis_init().set(redis_prizelist_key, self.json_dumps(shakebox_tipsprizelist), ex=3600 * 1)
            else:
                info["tips"] = act_info.exceed_tips
        else:
            info["tips"] = shakebox_tips_list[ran_num]
            info["is_limit"] = 0

        return self.reponse_json_success(info)


class NewShakeItHandler(SevenBaseHandler):
    """
    :description: 新版晃一晃
    """
    @filter_check_params("key_id,serial_no,login_token,act_id")
    def get_async(self):
        """
        :description: 晃一晃
        :param key_id:key_id
        :param serial_no:serial_no
        :param login_token:登录令牌
        :param act_id:活动id
        :param is_use_prop:是否使用提示卡
        :return: dict
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        key_id = int(self.get_param("key_id", 0))
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        serial_no = int(self.get_param("serial_no", 0))
        is_use_prop = int(self.get_param("is_use_prop", 0))

        user_info_model = UserInfoModel(context=self)
        act_info_model = ActInfoModel(context=self)
        act_prize_model = ActPrizeModel(context=self)
        surplus_queue_model = SurplusQueueModel(context=self)
        user_detail_model = UserDetailModel(context=self)
        prop_log_model = PropLogModel(context=self)
        # self.logging_link_info(str(serial_no) + "【serial_no】")
        info = {}
        info["prize_name"] = ""
        info["tips"] = ""
        info["is_limit"] = 1

        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.reponse_json_error("UserState", "对不起，你是黑名单用户,无法拆盒子")
        if user_info.login_token != login_token:
            return self.reponse_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽盲盒")

        user_detail = None
        if is_use_prop == 1:
            user_detail = user_detail_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
            if not user_detail or user_detail.tips_card_count <= 0:
                return self.reponse_json_error("Error", "提示卡数量不足")
            use_perspectivecard = self.redis_init().get(f"use_perspectivecard:{str(open_id)}_{str(key_id)}_{str(serial_no)}")
            if use_perspectivecard:
                return self.reponse_json_error("Error", "您已使用透视卡,不要浪费噢~")

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity("id=%s and is_release=1", params=[act_id])
        if not act_info:
            return self.reponse_json_error("NoAct", "对不起，活动不存在")

        now_date = self.get_now_datetime()
        if TimeHelper.format_time_to_datetime(now_date) < TimeHelper.format_time_to_datetime(act_info.start_date):
            return self.reponse_json_error("NoAct", "活动将在" + act_info.start_date + "开启")
        if TimeHelper.format_time_to_datetime(now_date) > TimeHelper.format_time_to_datetime(act_info.end_date):
            return self.reponse_json_error("NoAct", "活动已结束")

        redis_minmachinelist_key = f"minbox_list_{str(open_id)}_{str(key_id)}"
        min_machine_list = self.redis_init().get(redis_minmachinelist_key)
        if min_machine_list != None:
            min_machine_list = json.loads(min_machine_list)
        else:
            min_machine_list = {}
        prize_id = min_machine_list[str(serial_no)] if str(serial_no) in min_machine_list.keys() else 0

        act_prize = act_prize_model.get_entity_by_id(prize_id)
        if not act_prize:
            return self.reponse_json_error("NoPrize", "对不起，奖品不存在")

        surplus_queue = surplus_queue_model.get_entity("open_id=%s and prize_id=%s and key_id=%s", params=[open_id, prize_id, key_id])
        if not surplus_queue or act_prize.prize_total == 0:
            return self.reponse_json_error("NoPrize", "对不起，请重新选择盲盒")

        machine_info_model = MachineInfoModel(context=self)
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=act_prize.machine_id)
        if not machine_info:
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")
        if machine_info.sale_type == 2:
            sale_date = TimeHelper.format_time_to_datetime(machine_info.sale_date)
            if TimeHelper.format_time_to_datetime(now_date) < sale_date:
                china_sale_date = str(sale_date.month) + "月" + str(sale_date.day) + "日" + str(sale_date.hour) + "点"
                return self.reponse_json_error("NoStart", "该商品" + china_sale_date + "开售,敬请期待~")
        if config.get_value("check_prop",False) == True:
            price_gear_model = PriceGearModel(context=self)
            gear_value_model = GearValueModel(context=self)
            price_gear = price_gear_model.get_entity("id=%s", params=machine_info.price_gears_id)
            if not price_gear:
                return self.reponse_json_error("NoPriceGear", "对不起，价格档位不存在")
            gear_value = gear_value_model.get_entity("act_id=%s and open_id=%s and price_gears_id=%s", params=[act_id, open_id, price_gear.id])
            if not gear_value or gear_value.current_value <= 0:
                return self.reponse_json_error("NoLotteryCount", "对不起，次数不足,请先购买")
        shakebox_tips_list = self.json_loads(act_info.shakebox_tips)
        if len(shakebox_tips_list) <= 0:
            info["tips"] = act_info.exceed_tips
            return self.reponse_json_success(info)

        incre_key = str(prize_id) + "-" + str(serial_no)
        redis_num_key = "shakebox_tipsnumlist_" + str(open_id) + "_" + str(act_prize.machine_id) + "_" + str(key_id)
        shakebox_tipsnumlist = self.redis_init().get(redis_num_key)
        redis_useprop_key = f"shakebox_usepropcount_{str(open_id)}_{str(act_prize.machine_id)}_{str(key_id)}"
        shakebox_useproplist = self.redis_init().get(redis_useprop_key)

        shakebox_tipsnumlist = self.json_loads(shakebox_tipsnumlist) if shakebox_tipsnumlist != None else {}
        shakebox_useproplist = self.json_loads(shakebox_useproplist) if shakebox_useproplist != None else {}
        ran_num = 0
        if is_use_prop == 1:
            useprop_num = shakebox_useproplist[incre_key] if incre_key in shakebox_useproplist.keys() else 0
            if int(useprop_num) > 0:
                return self.reponse_json_error("Error", "只能使用一张提示卡")
            ran_num = 0
        else:
            num = shakebox_tipsnumlist[incre_key] if incre_key in shakebox_tipsnumlist.keys() else 0
            if int(num) >= int(act_info.shakebox_tips_num):
                info["tips"] = act_info.exceed_tips
                return self.reponse_json_success(info)
            ran_num_list = []
            for i in range(len(shakebox_tips_list)):
                if i == 0:
                    for j in range(7):
                        ran_num_list.append(i)
                else:
                    ran_num_list.append(i)
            ran_num = random.randint(0, int(len(ran_num_list) - 1))
            ran_num = int(ran_num_list[ran_num])

        # self.logging_link_info(str(ran_num_list)+"--" + str(ran_num) + "【ran_num_list】")
        if ran_num == 0:
            redis_prizelist_key = "shakebox_tipsprizelist_" + str(open_id) + "_" + str(act_prize.machine_id) + "_" + str(key_id)
            shakebox_tipsprizelist = self.redis_init().get(redis_prizelist_key)
            if shakebox_tipsprizelist != None:
                shakebox_tipsprizelist = self.json_loads(shakebox_tipsprizelist)
            else:
                shakebox_tipsprizelist = {}
            prize_list = shakebox_tipsprizelist[incre_key] if incre_key in shakebox_tipsprizelist.keys() else []
            cur_prize = None
            exclude_Prizeid_list = [prize_id]
            if len(prize_list) > 0:
                exclude_Prizeid_list.extend(prize_list)
            exclude_Prizeid_ids = ','.join(str(prize_id) for prize_id in exclude_Prizeid_list)
            condition = f"machine_id={act_prize.machine_id} and id not in ({exclude_Prizeid_ids}) and is_release=1 and tag_id=1"
            cur_prize = act_prize_model.get_entity(condition, order_by="RAND()")
            if cur_prize is not None:
                info["tips"] = shakebox_tips_list[0].replace("XX", cur_prize.prize_name)
                info["prize_name"] = cur_prize.prize_name
                # info["prize_id"] = cur_prize.id
                info["is_limit"] = 0
                prize_list.append(cur_prize.id)
                if is_use_prop == 0:
                    shakebox_tipsnumlist[incre_key] = int(num + 1)
                    self.redis_init().set(redis_num_key, self.json_dumps(shakebox_tipsnumlist), ex=3600 * 1)
                else:
                    prop_log = PropLog()
                    prop_log.app_id = app_id
                    prop_log.act_id = act_id
                    prop_log.open_id = open_id
                    prop_log.user_nick = user_info.user_nick
                    prop_log.change_type = 3
                    prop_log.operate_type = 1
                    prop_log.prop_type = 3
                    prop_log.machine_name = machine_info.machine_name
                    prop_log.specs_type = machine_info.specs_type
                    prop_log.operate_value = 1
                    prop_log.history_value = user_detail.tips_card_count
                    prop_log.title = f"使用提示卡排除奖品:{cur_prize.prize_name}"
                    prop_log.remark = info
                    prop_log.create_date_int = SevenHelper.get_now_day_int()
                    prop_log.create_date = self.get_now_datetime()
                    prop_log_model.add_entity(prop_log)
                    user_detail_model.update_table("tips_card_count=tips_card_count-1", "open_id=%s and act_id=%s", params=[open_id, act_id])
                    shakebox_useproplist[incre_key] = int(useprop_num + 1)
                    self.redis_init().set(redis_useprop_key, self.json_dumps(shakebox_useproplist), ex=3600 * 1)

                shakebox_tipsprizelist[incre_key] = prize_list
                self.redis_init().set(redis_prizelist_key, self.json_dumps(shakebox_tipsprizelist), ex=3600 * 1)
            else:
                info["tips"] = act_info.exceed_tips
        else:
            info["tips"] = shakebox_tips_list[ran_num]
            info["is_limit"] = 0

        return self.reponse_json_success(info)


class ShakeItPrizeListHandler(SevenBaseHandler):
    """
    :description: 晃一晃奖品列表(安全问题，后续废弃使用)
    """
    @filter_check_params("prize_id,key_id,machine_id")
    def get_async(self):
        """
        :description: 晃一晃奖品列表
        :param prize_id:奖品id
        :param key_id:key_id
        :param machine_id:机台id
        :param serial_no:serial_no
        :return list
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        prize_id = int(self.get_param("prize_id", 0))
        key_id = int(self.get_param("key_id", 0))
        machine_id = int(self.get_param("machine_id", 0))
        serial_no = int(self.get_param("serial_no", 0))

        machine_info_model = MachineInfoModel(context=self)
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=machine_id)
        if not machine_info:
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")
        incre_key = incre_key = str(prize_id) + "-" + str(serial_no)
        result_act_prize_list_dict = []

        redis_prizelist_key = "shakebox_tipsprizelist_" + str(open_id) + "_" + str(machine_id) + "_" + str(key_id)
        shakebox_tipsprizelist = self.redis_init().get(redis_prizelist_key)
        if shakebox_tipsprizelist != None:
            shakebox_tipsprizelist = self.json_loads(shakebox_tipsprizelist)
        else:
            shakebox_tipsprizelist = {}
        exclude_prize_list = shakebox_tipsprizelist[incre_key] if incre_key in shakebox_tipsprizelist.keys() else []

        perspectivecard_prize_id = self.redis_init().get(f"use_perspectivecard:{str(open_id)}_{str(key_id)}_{str(serial_no)}")
        perspectivecard_prize_id = int(perspectivecard_prize_id.decode()) if perspectivecard_prize_id else 0

        act_prize_list_dict = ActPrizeModel(context=self).get_dict_list("machine_id=%s and is_release=1", order_by="tag_id desc,sort_index desc", params=[machine_id])
        for i in range(len(act_prize_list_dict)):

            result_act_prize = {}
            result_act_prize["prize_id"] = act_prize_list_dict[i]["id"]
            result_act_prize["prize_name"] = act_prize_list_dict[i]["prize_name"]
            result_act_prize["prize_pic"] = act_prize_list_dict[i]["prize_pic"]
            result_act_prize["tag_id"] = act_prize_list_dict[i]["tag_id"]
            result_act_prize["is_perspectivecard"] = False
            if perspectivecard_prize_id > 0:
                result_act_prize["is_perspectivecard"] = True
                if act_prize_list_dict[i]["id"] == perspectivecard_prize_id:
                    result_act_prize["is_exclude"] = False
                else:
                    result_act_prize["is_exclude"] = True
            else:
                exclude_prize_id = [prize_id for prize_id in exclude_prize_list if prize_id == act_prize_list_dict[i]["id"]]
                result_act_prize["is_exclude"] = True if exclude_prize_id else False

            result_act_prize_list_dict.append(result_act_prize)

        return self.reponse_json_success(result_act_prize_list_dict)


class NewShakeItPrizeListHandler(SevenBaseHandler):
    """
    :description: 晃一晃奖品列表
    """
    @filter_check_params("key_id,machine_id")
    def get_async(self):
        """
        :description: 晃一晃奖品列表
        :param key_id:key_id
        :param machine_id:机台id
        :param serial_no:serial_no
        :return list
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        key_id = int(self.get_param("key_id", 0))
        machine_id = int(self.get_param("machine_id", 0))
        serial_no = int(self.get_param("serial_no", 0))

        machine_info_model = MachineInfoModel(context=self)
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=machine_id)
        if not machine_info:
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")

        redis_minmachinelist_key = f"minbox_list_{str(open_id)}_{str(key_id)}"
        min_machine_list = self.redis_init().get(redis_minmachinelist_key)
        if min_machine_list != None:
            min_machine_list = json.loads(min_machine_list)
        else:
            min_machine_list = {}
        prize_id = min_machine_list[str(serial_no)] if str(serial_no) in min_machine_list.keys() else 0
        incre_key = incre_key = str(prize_id) + "-" + str(serial_no)
        result_act_prize_list_dict = []

        redis_prizelist_key = "shakebox_tipsprizelist_" + str(open_id) + "_" + str(machine_id) + "_" + str(key_id)
        shakebox_tipsprizelist = self.redis_init().get(redis_prizelist_key)
        if shakebox_tipsprizelist != None:
            shakebox_tipsprizelist = self.json_loads(shakebox_tipsprizelist)
        else:
            shakebox_tipsprizelist = {}
        exclude_prize_list = shakebox_tipsprizelist[incre_key] if incre_key in shakebox_tipsprizelist.keys() else []

        perspectivecard_prize_id = self.redis_init().get(f"use_perspectivecard:{str(open_id)}_{str(key_id)}_{str(serial_no)}")
        perspectivecard_prize_id = int(perspectivecard_prize_id.decode()) if perspectivecard_prize_id else 0

        act_prize_list_dict = ActPrizeModel(context=self).get_dict_list("machine_id=%s and is_release=1", order_by="tag_id desc,sort_index desc", params=[machine_id])
        for i in range(len(act_prize_list_dict)):

            result_act_prize = {}
            result_act_prize["prize_id"] = act_prize_list_dict[i]["id"]
            result_act_prize["prize_name"] = act_prize_list_dict[i]["prize_name"]
            result_act_prize["prize_pic"] = act_prize_list_dict[i]["prize_pic"]
            result_act_prize["tag_id"] = act_prize_list_dict[i]["tag_id"]
            result_act_prize["is_perspectivecard"] = False
            if perspectivecard_prize_id > 0:
                result_act_prize["is_perspectivecard"] = True
                if act_prize_list_dict[i]["id"] == perspectivecard_prize_id:
                    result_act_prize["is_exclude"] = False
                else:
                    result_act_prize["is_exclude"] = True
            else:
                exclude_prize_id = [prize_id for prize_id in exclude_prize_list if prize_id == act_prize_list_dict[i]["id"]]
                result_act_prize["is_exclude"] = True if exclude_prize_id else False

            result_act_prize_list_dict.append(result_act_prize)

        return self.reponse_json_success(result_act_prize_list_dict)


class RecoverHandler(SevenBaseHandler):
    """
    :description: 回收预分配的奖品
    """
    @filter_check_params("machine_id,login_token,act_id,key_id")
    def get_async(self):
        """
        :description: 回收预分配的奖品
        :param login_token:登录令牌
        :param act_id:活动id
        :param machine_id:机台id
        :param key_id:key_id
        :param ver:版本
        :return reponse_json_success
        :last_editors: HuangJingCan
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        machine_id = int(self.get_param("machine_id", 0))
        key_id = self.get_param("key_id")
        ver_no = self.get_param("ver")

        user_info_model = UserInfoModel(context=self)
        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"), context=self)
        act_prize_model = ActPrizeModel(db_transaction=db_transaction, context=self)
        surplus_queue_model = SurplusQueueModel(db_transaction=db_transaction, context=self)

        #请求太频繁限制
        if self.check_post(f"Recover_Post_{str(open_id)}_{str(machine_id)}_{str(key_id)}", 120) == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")
        #删除小盒子历史产生的数据
        redis_num_key = "shakebox_tipsnumlist_" + str(open_id) + "_" + str(machine_id) + "_" + str(key_id)
        redis_prizelist_key = "shakebox_tipsprizelist_" + str(open_id) + "_" + str(machine_id) + "_" + str(key_id)
        self.redis_init().delete(redis_num_key)
        self.redis_init().delete(redis_prizelist_key)
        user_info = user_info_model.get_entity("act_id=%s and open_id=%s", params=[act_id, open_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.reponse_json_error("UserState", "对不起，你是黑名单用户")
        if user_info.login_token != login_token:
            return self.reponse_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法操作")
        surplus_queue_list = surplus_queue_model.get_list("act_id=%s and open_id=%s and key_id=%s", params=[act_id, open_id, key_id])
        if len(surplus_queue_list) > 0:
            for surplus_queue in surplus_queue_list:
                if str(TimeHelper.add_minutes_by_format_time(minute=5)) > str(surplus_queue.expire_date):
                    continue
                try:
                    db_transaction.begin_transaction()
                    surplus_queue_model.del_entity("id=%s", params=[surplus_queue.id])
                    act_prize_model.update_table("surplus=surplus+1", "id=%s and (surplus+1)<=prize_total", params=[surplus_queue.prize_id])
                    result, message = db_transaction.commit_transaction(True)
                    if result == False:
                        self.logging_link_error("【回收预分配的奖品事务执行异常】" + message)
                except Exception as ex:
                    self.logging_link_error("回收预分配的奖品异常:" + str(ex))                   
        return self.reponse_json_success()


class UsePerspectiveCardHandler(SevenBaseHandler):
    """
    :description: 使用透视卡(安全问题，后续废弃使用)
    """
    @filter_check_params("prize_id,key_id,login_token,act_id")
    def get_async(self):
        """
        :description: 使用透视卡
        :param prize_id:奖品id
        :param key_id:用户进入中盒自动分配的唯一标识
        :param serial_no:小盒子编号
        :param login_token:登录令牌
        :param act_id:活动id
        :return: 奖品名称
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        prize_id = int(self.get_param("prize_id", 0))
        key_id = int(self.get_param("key_id", 0))
        serial_no = int(self.get_param("serial_no", 0))
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        user_info_model = UserInfoModel(context=self)
        user_detail_model = UserDetailModel(context=self)
        act_prize_model = ActPrizeModel(context=self)
        prop_log_model = PropLogModel(context=self)
        machine_info_model = MachineInfoModel(context=self)
        #请求太频繁限制
        if self.check_post(f"UsePerspectiveCard_Post_{str(open_id)}_{str(key_id)}") == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")
        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.reponse_json_error("UserState", "对不起，你是黑名单用户,无法拆盒子")
        if user_info.login_token != login_token:
            return self.reponse_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽盲盒")

        prop_redis_key = f"use_perspectivecard:{str(open_id)}_{str(key_id)}_{str(serial_no)}"
        use_perspectivecard = self.redis_init().get(prop_redis_key)
        if use_perspectivecard:
            return self.reponse_json_error("Error", "只能使用一张透视卡")
        user_detail = user_detail_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
        if not user_detail:
            return self.reponse_json_error("Error", "透视卡数量不足")
        if user_detail.perspective_card_count <= 0:
            return self.reponse_json_error("Error", "透视卡数量不足")
        act_prize = act_prize_model.get_entity_by_id(prize_id)
        if not act_prize:
            return self.reponse_json_error("Error", "对不起，奖品不存在")
        if act_prize.is_release == 0:
            return self.reponse_json_error("Error", "对不起，奖品不存在")
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=act_prize.machine_id)
        if not machine_info:
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")

        if config.get_value("check_prop",False) == True:
            price_gear_model = PriceGearModel(context=self)
            gear_value_model = GearValueModel(context=self)
            price_gear = price_gear_model.get_entity("id=%s", params=machine_info.price_gears_id)
            if not price_gear:
                return self.reponse_json_error("NoPriceGear", "对不起，价格档位不存在")
            gear_value = gear_value_model.get_entity("act_id=%s and open_id=%s and price_gears_id=%s", params=[act_id, open_id, price_gear.id])
            if not gear_value or gear_value.current_value <= 0:
                return self.reponse_json_error("NoLotteryCount", "对不起，次数不足,请先购买")

        prop_log = PropLog()
        prop_log.app_id = app_id
        prop_log.act_id = act_id
        prop_log.open_id = open_id
        prop_log.user_nick = user_info.user_nick
        prop_log.change_type = 3
        prop_log.operate_type = 1
        prop_log.prop_type = 2
        prop_log.machine_name = machine_info.machine_name
        prop_log.specs_type = machine_info.specs_type
        prop_log.operate_value = 1
        prop_log.history_value = user_detail.perspective_card_count
        prop_log.title = f"使用透视卡查看奖品:{act_prize.prize_name}"
        info = {}
        info["machine_id"] = act_prize.machine_id
        info["prize_id"] = act_prize.id
        info["prize_name"] = act_prize.prize_name
        info["key_id"] = key_id
        info["serial_no"] = serial_no
        prop_log.remark = info
        prop_log.create_date_int = SevenHelper.get_now_day_int()
        prop_log.create_date = self.get_now_datetime()

        update_result = user_detail_model.update_table("perspective_card_count=perspective_card_count-1", "open_id=%s and act_id=%s and perspective_card_count>0", params=[open_id, act_id])
        if update_result == False:
            return self.reponse_json_error("Error", "透视卡数量不足")
        prop_log_model.add_entity(prop_log)
        self.redis_init().set(prop_redis_key, act_prize.id, ex=3600 * 1)

        result = {}
        result["prize_id"] = act_prize.id
        result["prize_name"] = act_prize.prize_name
        result["prize_pic"] = act_prize.prize_pic
        result["prize_price"] = act_prize.prize_price

        return self.reponse_json_success(result)


class NewUsePerspectiveCardHandler(SevenBaseHandler):
    """
    :description: 使用透视卡
    """
    @filter_check_params("key_id,serial_no,login_token,act_id")
    def get_async(self):
        """
        :description: 使用透视卡
        :param key_id:用户进入中盒自动分配的唯一标识
        :param serial_no:小盒子编号
        :param login_token:登录令牌
        :param act_id:活动id
        :return: 奖品名称
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        key_id = int(self.get_param("key_id", 0))
        serial_no = int(self.get_param("serial_no", 0))
        login_token = self.get_param("login_token")
        act_id = int(self.get_param("act_id", 0))
        user_info_model = UserInfoModel(context=self)
        user_detail_model = UserDetailModel(context=self)
        act_prize_model = ActPrizeModel(context=self)
        prop_log_model = PropLogModel(context=self)
        machine_info_model = MachineInfoModel(context=self)
        #请求太频繁限制
        if self.check_post(f"UsePerspectiveCard_Post_{str(open_id)}_{str(key_id)}") == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")
        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
        if not user_info:
            return self.reponse_json_error("NoUser", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.reponse_json_error("UserState", "对不起，你是黑名单用户,无法拆盒子")
        if user_info.login_token != login_token:
            return self.reponse_json_error("ErrorToken", "对不起，已在另一台设备登录,当前无法抽盲盒")

        prop_redis_key = f"use_perspectivecard:{str(open_id)}_{str(key_id)}_{str(serial_no)}"
        use_perspectivecard = self.redis_init().get(prop_redis_key)
        if use_perspectivecard:
            return self.reponse_json_error("Error", "只能使用一张透视卡")
        user_detail = user_detail_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
        if not user_detail:
            return self.reponse_json_error("Error", "透视卡数量不足")
        if user_detail.perspective_card_count <= 0:
            return self.reponse_json_error("Error", "透视卡数量不足")
        redis_minmachinelist_key = f"minbox_list_{str(open_id)}_{str(key_id)}"
        min_machine_list = self.redis_init().get(redis_minmachinelist_key)
        if min_machine_list != None:
            min_machine_list = json.loads(min_machine_list)
        else:
            min_machine_list = {}
        prize_id = min_machine_list[str(serial_no)] if str(serial_no) in min_machine_list.keys() else 0
        act_prize = act_prize_model.get_entity_by_id(prize_id)
        if not act_prize:
            return self.reponse_json_error("Error", "对不起，奖品不存在")
        if act_prize.is_release == 0:
            return self.reponse_json_error("Error", "对不起，奖品不存在")
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=act_prize.machine_id)
        if not machine_info:
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")
        
        if config.get_value("check_prop",False) == True:
            price_gear_model = PriceGearModel(context=self)
            gear_value_model = GearValueModel(context=self)
            price_gear = price_gear_model.get_entity("id=%s", params=machine_info.price_gears_id)
            if not price_gear:
                return self.reponse_json_error("NoPriceGear", "对不起，价格档位不存在")
            gear_value = gear_value_model.get_entity("act_id=%s and open_id=%s and price_gears_id=%s", params=[act_id, open_id, price_gear.id])
            if not gear_value or gear_value.current_value <= 0:
                return self.reponse_json_error("NoLotteryCount", "对不起，次数不足,请先购买")

        prop_log = PropLog()
        prop_log.app_id = app_id
        prop_log.act_id = act_id
        prop_log.open_id = open_id
        prop_log.user_nick = user_info.user_nick
        prop_log.change_type = 3
        prop_log.operate_type = 1
        prop_log.prop_type = 2
        prop_log.machine_name = machine_info.machine_name
        prop_log.specs_type = machine_info.specs_type
        prop_log.operate_value = 1
        prop_log.history_value = user_detail.perspective_card_count
        prop_log.title = f"使用透视卡查看奖品:{act_prize.prize_name}"
        info = {}
        info["machine_id"] = act_prize.machine_id
        info["prize_id"] = act_prize.id
        info["prize_name"] = act_prize.prize_name
        info["key_id"] = key_id
        info["serial_no"] = serial_no
        prop_log.remark = info
        prop_log.create_date_int = SevenHelper.get_now_day_int()
        prop_log.create_date = self.get_now_datetime()

        update_result = user_detail_model.update_table("perspective_card_count=perspective_card_count-1", "open_id=%s and act_id=%s and perspective_card_count>0", params=[open_id, act_id])
        if update_result == False:
            return self.reponse_json_error("Error", "透视卡数量不足")
        prop_log_model.add_entity(prop_log)
        self.redis_init().set(prop_redis_key, act_prize.id, ex=3600 * 1)

        result = {}
        result["prize_id"] = act_prize.id
        result["prize_name"] = act_prize.prize_name
        result["prize_pic"] = act_prize.prize_pic
        result["prize_price"] = act_prize.prize_price

        return self.reponse_json_success(result)


class UseResetCardHandler(SevenBaseHandler):
    """
    :description: 使用重抽卡
    """
    @filter_check_params("order_no,login_token,act_id,key_id")
    def get_async(self):
        """
        :description: 使用重抽卡
        :param order_no:订单号
        :param key_id:中盒分配唯一标识
        :param login_token:登录令牌
        :param act_id:活动id
        :return:
        :last_editors: HuangJianYi
        """
        open_id = self.get_taobao_param().open_id
        app_id = self.get_taobao_param().source_app_id
        login_token = self.get_param("login_token")
        order_no = self.get_param("order_no")
        key_id = self.get_param("key_id")
        act_id = int(self.get_param("act_id", 0))

        db_transaction = DbTransaction(db_config_dict=config.get_value("db_cloudapp"))
        user_info_model = UserInfoModel(db_transaction=db_transaction, context=self)
        user_detail_model = UserDetailModel(db_transaction=db_transaction, context=self)
        prop_log_model = PropLogModel(db_transaction=db_transaction, context=self)
        surplus_queue_model = SurplusQueueModel(db_transaction=db_transaction, context=self)
        act_prize_model = ActPrizeModel(db_transaction=db_transaction, context=self)
        prize_roster_model = PrizeRosterModel(db_transaction=db_transaction, context=self)
        prize_order_model = PrizeOrderModel(db_transaction=db_transaction, context=self)
        prize_order_model = PrizeOrderModel(db_transaction=db_transaction, context=self)
        machine_info_model = MachineInfoModel(context=self)
        #请求太频繁限制
        if self.check_post(f"ResetCard_Post_{str(act_id)}_{str(open_id)}") == False:
            return self.reponse_json_error("HintMessage", "对不起，请求太频繁")
        user_info = user_info_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
        if not user_info or user_info.act_id != act_id:
            return self.reponse_json_error("Error", "对不起，用户不存在")
        if user_info.user_state == 1:
            return self.reponse_json_error("UserState", "账号异常，请联系客服处理")
        if user_info.login_token != login_token:
            return self.reponse_json_error("Error", "对不起，已在另一台设备登录,当前无法操作")
        user_detail = user_detail_model.get_entity("open_id=%s and act_id=%s", params=[open_id, act_id])
        if not user_detail:
            return self.reponse_json_error("Error", "重抽卡数量不足")
        if user_detail.redraw_card_count <= 0:
            return self.reponse_json_error("Error", "重抽卡数量不足")
        new_surplus_queue = surplus_queue_model.get_entity("open_id=%s and act_id=%s and key_id=%s", order_by="RAND()", params=[open_id, act_id, key_id])
        if not new_surplus_queue:
            return self.reponse_json_error("Error", "无法使用重抽卡")
        act_prize = act_prize_model.get_entity_by_id(new_surplus_queue.prize_id)
        if not act_prize:
            return self.reponse_json_error("Error", "对不起，奖品不存在")
        if act_prize.is_release == 0:
            return self.reponse_json_error("Error", "对不起，奖品不存在")
        machine_info = machine_info_model.get_entity("id=%s and is_release=1", params=act_prize.machine_id)
        if not machine_info:
            return self.reponse_json_error("NoMachine", "对不起，盒子不存在")
        prize_order = prize_order_model.get_entity("order_no=%s", params=[order_no])
        if not prize_order or prize_order.open_id != open_id or prize_order.act_id != act_id:
            return self.reponse_json_error("Error", "无法使用重抽卡")
        prize_roster = prize_roster_model.get_entity("prize_order_no=%s", params=[order_no])
        if not prize_roster or prize_roster.open_id != open_id or prize_roster.act_id != act_id:
            return self.reponse_json_error("Error", "无法使用重抽卡")

        old_prize_id = prize_roster.prize_id
        old_prize_name = prize_roster.prize_name
        #录入用户奖品
        prize_roster.prize_pic = act_prize.unpack_pic
        prize_roster.toys_pic = act_prize.toys_pic
        prize_roster.prize_id = act_prize.id
        prize_roster.prize_name = act_prize.prize_name
        prize_roster.prize_price = act_prize.prize_price
        prize_roster.prize_detail = act_prize.prize_detail
        prize_roster.tag_id = act_prize.tag_id
        prize_roster.is_sku = act_prize.is_sku
        prize_roster.goods_code = act_prize.goods_code
        prize_roster.goods_code_list = act_prize.goods_code_list
        prize_roster.use_redrawcard_count = prize_roster.use_redrawcard_count + 1

        #预扣队列
        new_surplus_queue.prize_id = old_prize_id

        prop_log = PropLog()
        prop_log.app_id = app_id
        prop_log.act_id = act_id
        prop_log.open_id = open_id
        prop_log.user_nick = user_info.user_nick
        prop_log.change_type = 3
        prop_log.operate_type = 1
        prop_log.prop_type = 4
        prop_log.machine_name = machine_info.machine_name
        prop_log.specs_type = machine_info.specs_type
        prop_log.operate_value = 1
        prop_log.history_value = user_detail.redraw_card_count
        prop_log.title = "使用重抽卡重置奖品"
        prop_log.create_date_int = SevenHelper.get_now_day_int()
        prop_log.create_date = self.get_now_datetime()
        info = {}
        info["order_no"] = order_no
        info["machine_id"] = prize_roster.machine_id
        info["old_prize_id"] = old_prize_id
        info["old_prize_name"] = old_prize_name
        info["new_prize_id"] = act_prize.id
        info["new_prize_name"] = act_prize.prize_name
        prop_log.remark = info

        try:
            db_transaction.begin_transaction()
            prop_log_model.add_entity(prop_log)  #添加使用道具记录
            user_detail_model.update_table("redraw_card_count=redraw_card_count-1", "open_id=%s and act_id=%s", params=[open_id, act_id])  #扣除重抽卡数
            act_prize_model.update_table("hand_out=hand_out-1,prize_total=prize_total+1", "id=%s", old_prize_id)  #旧商品扣除已发数补上总数
            act_prize_model.update_table("hand_out=hand_out+1,prize_total=prize_total-1", "id=%s", act_prize.id)  #新商品补上已发数扣除总数
            prize_roster_model.update_entity(prize_roster)  #旧商品更新成新商品
            surplus_queue_model.update_entity(new_surplus_queue, "prize_id")  #旧商品加到预扣队列，回补预扣库存
            db_transaction.commit_transaction()

        except Exception as ex:
            db_transaction.rollback_transaction()
            self.logging_link_error("UseResetCardHandler:" + str(ex))
            return self.reponse_json_error("Error", "系统繁忙,请稍后再试")

        result_prize = {}
        result_prize["order_no"] = order_no
        result_prize["prize_name"] = act_prize.prize_name
        result_prize["prize_id"] = act_prize.id
        result_prize["unpack_pic"] = act_prize.unpack_pic
        result_prize["tag_id"] = act_prize.tag_id
        result_prize["prize_detail"] = self.json_loads(act_prize.prize_detail)
        if user_info.user_nick:
            length = len(user_info.user_nick)
            if length > 2:
                result_prize["user_nick"] = user_info.user_nick[0:length - 2] + "**"
            else:
                result_prize["user_nick"] = user_info.user_nick[0:1] + "*"

        return self.reponse_json_success(result_prize)