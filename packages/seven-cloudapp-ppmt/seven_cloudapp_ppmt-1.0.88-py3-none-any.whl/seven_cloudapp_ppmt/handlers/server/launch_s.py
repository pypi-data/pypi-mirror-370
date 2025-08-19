# -*- coding: utf-8 -*-
"""
@Author: ChenCheng
@Date: 2022-03-18 10:12:12
@LastEditTime: 2022-07-26 17:44:01
@LastEditors: HuangJianYi
@Description: 
"""
from seven_cloudapp.handlers.seven_base import *
from seven_cloudapp.handlers.top_base import *
from seven_cloudapp.models.seven_model import PageInfo
from seven_cloudapp_ppmt.models.db_models.act.act_info_model import *
from seven_cloudapp_ppmt.models.db_models.launch.launch_plan_model import *
from seven_cloudapp_ppmt.models.db_models.launch.launch_goods_model import *


class InitLaunchGoodsHandler(SevenBaseHandler):
    """
    :description: 初始化商品投放
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 初始化商品投放
        :param app_id：应用标识
        :param act_id：活动标识
        :return
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        act_id = int(self.get_param("act_id", 0))
        act_info_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        act_name = act_info_dict["act_name"] if act_info_dict else ""
        online_url = self.get_online_url(act_id, app_id)
        return self.reponse_json_success({"url": online_url, "act_name": act_name, "goods_list": []})


class ResetLaunchGoodsHandler(SevenBaseHandler):
    """
    :description: 重置商品投放 删除已投放的记录并将活动投放状态改为未投放
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 重置商品投放 删除已投放的记录并将活动投放状态改为未投放
        :param app_id：应用标识
        :param act_id：活动标识
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        act_id = int(self.get_param("act_id", 0))
        ActInfoModel(context=self).update_table("is_throw=0", "app_id=%s and id=%s", params=[app_id, act_id])
        LaunchGoodsModel(context=self).del_entity("app_id=%s and act_id=%s", params=[app_id, act_id])
        return self.reponse_json_success()


class InitLaunchGoodsCallBackHandler(SevenBaseHandler):
    """
    :description: 初始化投放商品回调接口
    """
    def get_async(self):
        """
        :description: 初始化投放商品回调接口
        :param app_id：应用标识
        :param act_id：活动标识
        :param close_goods_id：投放失败时关闭投放的商品ID  多个逗号,分隔
        :param tb_launch_plan 淘宝插件返回的信息
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        act_id = int(self.get_param("act_id", 0))
        close_goods_id = self.get_param("close_goods_id")
        call_back_info = self.get_param("call_back_info")

        try:
            if close_goods_id != "":
                close_goods_id_list = list(set(close_goods_id.split(",")))
                close_goods_id_str_list = ','.join(["'%s'" % str(item) for item in close_goods_id_list])
                LaunchGoodsModel(context=self).update_table("is_launch=0,launch_date=%s", "act_id=%s and " + f"goods_id in ({close_goods_id_str_list})", params=[self.get_now_datetime(), act_id])

            tb_launch_plan = None
            if call_back_info != "":
                call_back_info = self.json_loads(call_back_info)
                for cur_tb_launch_plan in call_back_info["putSuccessList"]:
                    if cur_tb_launch_plan["sceneInfo"]["id"] == 1:
                        tb_launch_plan = cur_tb_launch_plan
                        break

            if tb_launch_plan:
                ActInfoModel(context=self).update_table("is_throw=1", "id=%s", params=act_id)
                launch_plan_model = LaunchPlanModel(context=self)
                launch_plan = launch_plan_model.get_entity("tb_launch_id=%s", params=[tb_launch_plan["id"]])
                if not launch_plan:
                    launch_plan = LaunchPlan()
                    launch_plan.app_id = app_id
                    launch_plan.act_id = act_id
                    launch_plan.tb_launch_id = tb_launch_plan["id"]
                    launch_plan.launch_url = tb_launch_plan["previewUrl"]
                    launch_plan.start_date = tb_launch_plan["startTime"].replace('年', '-').replace('月', '-').replace('日', ' ') + tb_launch_plan["startTimeBottm"]
                    launch_plan.end_date = tb_launch_plan["endTime"].replace('年', '-').replace('月', '-').replace('日', ' ') + tb_launch_plan["endTimeBottom"]
                    if tb_launch_plan["status"] == "未开始":
                        launch_plan.status = 0
                    elif tb_launch_plan["status"] == "进行中":
                        launch_plan.status = 1
                    elif tb_launch_plan["status"] == "已结束":
                        launch_plan.status = 2
                    launch_plan.create_date = self.get_now_datetime()
                    launch_plan.modify_date = self.get_now_datetime()
                    launch_plan_model.add_entity(launch_plan)

            return self.reponse_json_success()

        except Exception as ex:
            self.logger_error.error("InitLaunchGoodsCallBackHandler:" + traceback.format_exc())
            return self.reponse_json_error("error", "请求失败")


class UpdateLaunchGoodsStatusHandler(SevenBaseHandler):
    """
    :description: 更改投放商品的状态
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 保存更改投放商品的状态
        :param app_id：应用标识
        :param 活动标识
        :param update_goods_id：更新商品ID（例：1）
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        act_id = int(self.get_param("act_id", 0))
        goods_id = self.get_param("update_goods_id")
        if goods_id != "":
            LaunchGoodsModel(context=self).update_table("is_launch=abs(is_launch-1),is_sync=0,launch_date=%s", "app_id=%s and act_id=%s and goods_id=%s", [self.get_now_datetime(), app_id, act_id, goods_id])
        return self.reponse_json_success()


class LaunchGoodsListHandler(TopBaseHandler):
    """
    :description: 投放商品列表
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 投放商品列表
        :param app_id：应用标识
        :param act_id：活动标识
        :param page_index：页索引
        :param page_size：页大小
        :return 列表
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        act_id = int(self.get_param("act_id", 0))
        page_index = int(self.get_param("page_index", 0))
        page_size = int(self.get_param("page_size", 0))
        goods_id = self.get_param("goods_id")
        launch_status = int(self.get_param("launch_status", -1))
        invoke_result_data = self.get_launch_goods_list(app_id, act_id, page_size, page_index, self.get_param("access_token"), goods_id, launch_status)
        if invoke_result_data["success"] == False:
            return self.response_json_error(invoke_result_data["error_code"], invoke_result_data["error_message"])
        return self.reponse_json_success(invoke_result_data["data"])

    def get_launch_goods_list(self, app_id, act_id, page_size, page_index, access_token, goods_id, launch_status):
        """
        :description: 获取投放商品列表
        :param app_id:应用标识
        :param act_id:活动标识
        :param page_size:条数
        :param page_index:页数
        :param access_token:access_token
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = {"success":True,"error_code":"","error_message":""}
        launch_goods_list = []
        act_info_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        if not act_info_dict:
            invoke_result_data["success"] = False
            invoke_result_data["error_code"] = "error"
            invoke_result_data["error_message"] = "活动不存在"
            return invoke_result_data
        launch_goods_model = LaunchGoodsModel(context=self)

        condition = "app_id=%s and act_id=%s"
        params = [app_id, act_id]
        if goods_id != "":
            condition += " and goods_id =%s"
            params.append(goods_id)
        if launch_status > -1:
            condition += " and is_launch=%s"
            params.append(launch_status)

        launch_goods_list, total = launch_goods_model.get_dict_page_list("*", page_index, page_size, condition, "", "id desc", params=params)

        #获取商品信息
        goods_list = []
        if len(launch_goods_list) > 0:
            for launch_goods in launch_goods_list:
                launch_goods["goods_id"] = int(launch_goods["goods_id"])
            goods_ids = ",".join([str(launch_goods["goods_id"]) for launch_goods in launch_goods_list])

            resq = self.get_goods_list_for_goodsids(goods_ids, access_token)
            if "items_seller_list_get_response" in resq.keys():
                if "item" in resq["items_seller_list_get_response"]["items"].keys():
                    goods_list = resq["items_seller_list_get_response"]["items"]["item"]
            else:
                invoke_result_data["data"] = {"is_launch": act_info_dict['is_throw'], "page_info": {}}
                return invoke_result_data
        if len(goods_list) > 0:
            launch_goods_list = SevenHelper.merge_dict_list(launch_goods_list, "goods_id", goods_list, "num_iid", "pic_url,title")
        page_info = PageInfo(page_index, page_size, total, launch_goods_list)
        invoke_result_data["data"] = {"is_launch": act_info_dict['is_throw'], "page_info": page_info.__dict__}
        return invoke_result_data


class AsyncLaunchGoodsHandler(TopBaseHandler):
    """
    :description: 同步投放商品（小程序投放-商品绑定/解绑）
    """
    @filter_check_params("app_id,act_id")
    def get_async(self):
        """
        :description: 同步投放商品（小程序投放-商品绑定/解绑）
        :param app_id：应用标识
        :param act_id：活动标识
        :param machine_id：机台ID
        :return 
        :last_editors: HuangJianYi
        """
        app_id = self.get_param("app_id")
        act_id = int(self.get_param("act_id", 0))
        machine_id = int(self.get_param("machine_id", 0))

        online_url = self.get_online_url(act_id, app_id, machine_id)
        launch_plan_model = LaunchPlanModel(context=self)
        launch_plan = launch_plan_model.get_entity("act_id=%s", order_by="id desc", params=[act_id])
        if launch_plan:
            invoke_result_data = self.async_launch_goods(app_id, act_id, launch_plan.launch_url)
        else:
            invoke_result_data = self.async_launch_goods(app_id, act_id, online_url)
        if invoke_result_data["success"] == False:
            return self.reponse_json_error(invoke_result_data["error_code"], invoke_result_data["error_message"])
        return self.reponse_json_success()

    def async_launch_goods(self, app_id, act_id, online_url):
        """
        :description: 同步投放商品（小程序投放-商品绑定/解绑）
        :param app_id：应用标识
        :param act_id：活动标识
        :param online_url:投放地址
        :return 
        :last_editors: HuangJianYi
        """
        invoke_result_data = {"success":True,"error_code":"","error_message":""}
        act_info_dict = ActInfoModel(context=self).get_dict_by_id(act_id)
        if not act_info_dict:
            invoke_result_data["success"] = False
            invoke_result_data["error_code"] = "error"
            invoke_result_data["error_message"] = "活动不存在"
            return invoke_result_data
        launch_goods_model = LaunchGoodsModel(context=self)
        launch_goods_list = launch_goods_model.get_list("app_id=%s and act_id=%s and is_sync=0 and is_launch=1", params=[app_id,act_id])
        no_launch_goods_list = launch_goods_model.get_list("app_id=%s and act_id=%s and is_sync=0 and is_launch=0", params=[app_id,act_id])
        # 同步不投放的商品
        if len(no_launch_goods_list) > 0:

            no_launch_goods_id_list = [str(no_launch_goods.goods_id) for no_launch_goods in no_launch_goods_list]
            no_launch_goods_id_list = list(set(no_launch_goods_id_list))
            no_launch_goods_ids = ",".join(no_launch_goods_id_list)

            update_no_launch_goods_list = []
            # 淘宝top接口
            resp = self.change_throw_goods_list_status(no_launch_goods_ids, online_url, 'false')
            if "error_message" in resp.keys():
                invoke_result_data["success"] = False
                invoke_result_data["error_code"] = "error"
                invoke_result_data["error_message"] = resp["error_message"]
                return invoke_result_data
            async_result = resp["miniapp_distribution_items_bind_response"]["model_list"]["distribution_order_bind_target_entity_open_result_dto"][0]["bind_result_list"]["distribution_order_bind_base_dto"]
            for async_result_info in async_result:
                no_launch_goods = [no_launch_goods for no_launch_goods in no_launch_goods_list if str(no_launch_goods.goods_id) == async_result_info["target_entity_id"]]
                if len(no_launch_goods) > 0:
                    if async_result_info["success"] == True:
                        no_launch_goods[0].is_sync = 1
                        no_launch_goods[0].sync_date = self.get_now_datetime()
                    else:
                        no_launch_goods[0].error_message = async_result_info["fail_msg"]
                    update_no_launch_goods_list.append(no_launch_goods[0])

            launch_goods_model.update_list(update_no_launch_goods_list)

        # 同步投放的商品
        if len(launch_goods_list) > 0:
            launch_goods_id_list = [str(launch_goods.goods_id) for launch_goods in launch_goods_list]
            launch_goods_id_list = list(set(launch_goods_id_list))
            launch_goods_ids = ",".join(launch_goods_id_list)

            update_launch_goods_list = []
            # 淘宝top接口
            resp = self.change_throw_goods_list_status(launch_goods_ids, online_url, 'true')
            if "error_message" in resp.keys():
                invoke_result_data["success"] = False
                invoke_result_data["error_code"] = "error"
                invoke_result_data["error_message"] = resp["error_message"]
                return invoke_result_data
            async_result = resp["miniapp_distribution_items_bind_response"]["model_list"]["distribution_order_bind_target_entity_open_result_dto"][0]["bind_result_list"]["distribution_order_bind_base_dto"]
            for async_result_info in async_result:
                launch_goods = [launch_goods for launch_goods in launch_goods_list if str(launch_goods.goods_id) == async_result_info["target_entity_id"]]
                if len(launch_goods) > 0:
                    if async_result_info["success"] == True:
                        launch_goods[0].is_sync = 1
                        launch_goods[0].sync_date = self.get_now_datetime()
                    else:
                        launch_goods[0].is_launch = 0
                        launch_goods[0].is_sync = 1
                        launch_goods[0].error_message = async_result_info["fail_msg"]
                    update_launch_goods_list.append(launch_goods[0])

            launch_goods_model.update_list(update_launch_goods_list)

        return invoke_result_data


class GetLaunchPlanStatusHandler(TopBaseHandler):
    """
    @description: 获取投放计划状态
    @param {*} self
    @return {*}
    @last_editors: CaiYouBin
    """
    @filter_check_params("act_id")
    def get_async(self):
        act_id = int(self.get_param("act_id", 0))
        access_token = self.get_param("access_token")
        launch_status = 1  #投放状态，0:未开始， 1：进行中，2/3:已结束，其他为平台状态
        launch_plan_model = LaunchPlanModel(context=self)
        launch_plan = launch_plan_model.get_entity("act_id=%s", order_by="id desc", params=[act_id])

        act_info_model = ActInfoModel(context=self)
        act_info = act_info_model.get_entity("id=%s", params=[act_id])

        if not launch_plan:
            if act_info:
                if act_info.is_throw == 1:
                    return self.reponse_json_success(launch_status)
                else:
                    return self.reponse_json_success(0)
            else:
                return self.reponse_json_success(0)

        invoke_result_data = self.get_launch_action_info(launch_plan.tb_launch_id, access_token)
        if invoke_result_data["success"] == False:
            return self.reponse_json_error(invoke_result_data["error_code"], invoke_result_data["error_message"])

        tb_launch_status = invoke_result_data["data"]["miniapp_distribution_order_get_response"]["model"]["distribution_order_open_biz_dto"][0]["status"]
        if tb_launch_status == 0:
            tb_launch_status = 1

        if tb_launch_status == 2 and act_info.is_throw == 0:
            tb_launch_status = 0
        launch_status = tb_launch_status
        return self.reponse_json_success(launch_status)

    def get_launch_action_info(self, order_id, access_token):

        invoke_result_data = {"success":True,"error_code":"","error_message":""}
        app_key, app_secret = self.get_app_key_secret()
        try:

            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.MiniappDistributionOrderGetRequest()
            req.order_id_request = {}
            req.order_id_request["order_id_list"] = [order_id]

            resp = req.getResponse(access_token)
            invoke_result_data["data"] = resp
            return invoke_result_data

        except Exception as ex:
            self.logging_link_error("GetLaunchActionInfo:" + traceback.format_exc())
            invoke_result_data["success"] = False
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        invoke_result_data["error_code"] = "no_power"
                        invoke_result_data["error_message"] = content[len("submsg="):]
                        return invoke_result_data
                    if "submsg=" in content:
                        invoke_result_data["error_code"] = "error"
                        invoke_result_data["error_message"] = content[len("submsg="):]
                        return invoke_result_data
            return invoke_result_data


class AsyncLaunchGoodsStatusHandler(SevenBaseHandler):
    """
    @description: 同步投放商品（小程序投放-商品绑定/解绑）
    @param {*} self
    @return {*}
    @last_editors: CaiYouBin
    """
    @filter_check_params("act_id")
    def get_async(self):
        act_id = int(self.get_param("act_id", 0))
        redis_init = self.redis_init(decode_responses=True)
        redis_init.rpush("queue_async_lauch", act_id)
        return self.reponse_json_success()


class AddLaunchGoodsListHandler(SevenBaseHandler):
    """
    @description: 添加投放商品
    @param {*} self
    @return {*}
    @last_editors: CaiYouBin
    """
    @filter_check_params("app_id,act_id")
    def get_async(self):
        app_id = self.get_param("app_id")
        act_id = int(self.get_param("act_id", 0))
        goods_ids = self.get_param("goods_ids")

        if goods_ids != "":
            launch_goods_model = LaunchGoodsModel(context=self)
            goods_id_list = goods_ids.split(',')
            for goods_id in goods_id_list:
                launch_goods = launch_goods_model.get_entity("goods_id=%s", params=[goods_id])
                if not launch_goods:
                    launch_goods = LaunchGoods()
                    launch_goods.app_id = app_id
                    launch_goods.act_id = act_id
                    launch_goods.goods_id = goods_id
                    launch_goods.is_launch = 0
                    launch_goods.is_sync = 0
                    launch_goods.error_message = ""
                    launch_goods.create_date = self.get_now_datetime()
                    launch_goods.launch_date = self.get_now_datetime()
                    launch_goods_model.add_entity(launch_goods)

        return self.reponse_json_success()


class CanLaunchGoodsListHandler(TopBaseHandler):
    """
    :description: 获取可投放商品列表（获取当前会话用户出售中的商品列表）
    """
    def get_async(self):
        """
        :description: 导入商品列表（获取当前会话用户出售中的商品列表）
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param page_index：页索引
        :param page_size：页大小
        :return: 列表
        :last_editors: HuangJianYi
        """
        access_token = self.get_param("access_token")
        goods_name = self.get_param("goods_name")
        order_tag = self.get_param("order_tag", "list_time")
        order_by = self.get_param("order_by", "desc")
        page_index = int(self.get_param("page_index", 0))
        page_size = self.get_param("page_size", 20)

        resp = self.get_goods_list(page_index, page_size, goods_name, order_tag, order_by, access_token)
        if "items_onsale_get_response" not in resp or "items" not in resp["items_onsale_get_response"]:
            return self.reponse_json_success([])

        goods_id_list = [str(goods["num_iid"]) for goods in resp["items_onsale_get_response"]["items"]["item"]]
        goods_id_str_list = ','.join(["'%s'" % str(item) for item in goods_id_list])
        goods_id_in_condition = f"goods_id in ({goods_id_str_list})"
        launch_goods_model = LaunchGoodsModel(context=self)
        launch_goods_list = launch_goods_model.get_list(goods_id_in_condition)
        act_id_list = [launch_goods.act_id for launch_goods in launch_goods_list]
        act_id_list = list(set(act_id_list))
        act_id_in_condition = SevenHelper.get_condition_by_id_list("id",act_id_list)

        act_info_model = ActInfoModel(context=self)
        act_info_list = act_info_model.get_list(act_id_in_condition)

        for goods in resp["items_onsale_get_response"]["items"]["item"]:
            launch_goods = query(launch_goods_list).first_or_default(None, lambda x: x.goods_id == str(goods["num_iid"]))

            if launch_goods:
                goods["is_select"] = 1
                goods["bind_act_id"] = launch_goods.act_id
                act_info = query(act_info_list).first_or_default(None, lambda x: x.id == goods["bind_act_id"])
                if act_info:
                    goods["bind_act_name"] = act_info.act_name
                else:
                    goods["bind_act_name"] = ""
            else:
                goods["is_select"] = 0
                goods["bind_act_id"] = 0
                goods["bind_act_name"] = ""


        return self.reponse_json_success(resp)

    def get_goods_list(self, page_index, page_size, goods_name, order_tag, order_by, access_token):
        """
        :description: 导入商品列表（获取当前会话用户出售中的商品列表）
        :param page_index：页索引
        :param page_size：页大小
        :param goods_name：商品名称
        :param order_tag：order_tag
        :param order_by：排序类型
        :param access_token：access_token
        :return 
        :last_editors: HuangJingCan
        """
        try:
            app_key, app_secret = self.get_app_key_secret()
            top.setDefaultAppInfo(app_key, app_secret)
            req = top.api.ItemsOnsaleGetRequest()

            req.fields = "num_iid,title,nick,price,input_str,property_alias,sku,props_name,pic_url"
            req.page_no = page_index + 1
            req.page_size = page_size
            if goods_name != "":
                req.q = goods_name
            req.order_by = order_tag + ":" + order_by

            resp = req.getResponse(access_token)
            if resp:
                resp["pageSize"] = page_size
                resp["pageIndex"] = page_index

            self.logging_link_info(str(resp) + "【access_token】：" + self.get_taobao_param().access_token)
            return resp
        except Exception as ex:
            self.logging_link_error(traceback.format_exc())
            if "submsg" in str(ex):
                content_list = str(ex).split()
                for content in content_list:
                    if "submsg=该子帐号无此操作权限" in content:
                        return self.return_dict_error("NoPower", content[len("submsg="):])
                    if "submsg=" in content:
                        return self.return_dict_error("Error", content[len("submsg="):])


class GetLaunchProgressHandler(SevenBaseHandler):
    """
    @description: 获取投放进度
    @param {*} self
    @return {*}
    @last_editors: CaiYouBin
    """
    @filter_check_params("act_id")
    def get_async(self):
        act_id = int(self.get_param("act_id", 0))
        redis_init = self.redis_init(decode_responses=True)
        redis_data = redis_init.lrange("queue_async_lauch",0,-1)

        progress = 0 #投放进度  0未完成  1：已完成
        if not redis_data:
            progress = 1
        elif len(redis_data)==0:
            progress = 1
        else:
            for data in redis_data:
                if str(act_id) == data:
                    progress = 0
                    break

        return self.reponse_json_success(progress)