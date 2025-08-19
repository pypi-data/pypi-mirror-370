# -*- coding: utf-8 -*-
"""
:Author: CaiYouBin
:Date: 2020-06-05 17:27:26
:LastEditTime: 2021-04-15 15:20:11
:LastEditors: HuangJingCan
:description: 
"""
from seven_cloudapp.handlers.seven_base import *

from seven_cloudapp.models.db_models.behavior.behavior_log_model import *
from seven_cloudapp.models.db_models.behavior.behavior_orm_model import *
from seven_cloudapp.models.db_models.behavior.behavior_report_model import *

from seven_cloudapp_ppmt.models.db_models.machine.machine_info_model import *


class ReportInfoListHandler(SevenBaseHandler):
    """
    :description: 数据列表2.0版本
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 报表信息
        :param act_id：活动id
        :param start_date：开始时间
        :param end_date：结束时间
        :return: 列表
        :last_editors: CaiYouBin
        """
        act_id = int(self.get_param("act_id", 0))
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")

        date_list = self.get_date_list(start_date, end_date)

        condition = ""
        params = []

        condition += "act_id=%s"
        params.append(act_id)
        if start_date != "":
            condition += " and %s<=create_date"
            params.append(start_date)
        if end_date != "":
            condition += " and create_date<%s"
            params.append(end_date)

        behavior_orm_model = BehaviorOrmModel(context=self)
        behavior_report_model = BehaviorReportModel(context=self)
        behavior_orm_list = behavior_orm_model.get_list("is_common=1 OR act_id=%s", order_by="id asc", params=act_id, field="key_name,group_name,group_sub_name,key_value,value_type,is_common")

        behavior_report_list = behavior_report_model.get_dict_list(condition, field="key_name,key_value,DATE_FORMAT(create_date,'%%Y-%%m-%%d') AS create_date", params=params)

        #公共映射组（未去重）
        common_groups_1 = [orm.group_name for orm in behavior_orm_list if orm.is_common == 1]
        #公共映射组(去重)
        common_groups = list(set(common_groups_1))
        common_groups.sort(key=common_groups_1.index)

        common_group_data_list = []

        for common_group in common_groups:
            group_data = {}
            group_data["group_name"] = common_group
            data_list = []

            # 无子节点
            orm_list = [orm for orm in behavior_orm_list if orm.group_name == common_group and orm.group_sub_name == '']
            for orm in orm_list:
                data = {}
                data["title"] = orm.key_value
                data["value"] = []
                for date_day in date_list:
                    behavior_date_report = {}
                    for behavior_report in behavior_report_list:
                        if behavior_report["key_name"] == orm.key_name and behavior_report["create_date"] == date_day:
                            if orm.value_type != 2:
                                behavior_report["key_value"] = int(behavior_report["key_value"])
                            behavior_date_report = {"title": orm.key_value, "date": date_day, "value": behavior_report["key_value"]}
                            break
                    if not behavior_date_report:
                        behavior_date_report = {"title": orm.key_value, "date": date_day, "value": 0}
                    data["value"].append(behavior_date_report)
                data_list.append(data)
            if len(data_list) > 0:
                group_data["data_list"] = data_list

            # 有子节点
            orm_list_sub = [orm for orm in behavior_orm_list if orm.group_name == common_group and orm.group_sub_name != '']
            if orm_list_sub:
                groups_sub_name = [orm.group_sub_name for orm in orm_list_sub]
                #公共映射组(去重)
                sub_names = list(set(groups_sub_name))
                sub_names.sort(key=groups_sub_name.index)
                sub_group_data_list = []
                for sub_name in sub_names:
                    sub_group_data = {}
                    sub_group_data["group_name"] = sub_name
                    sub_data_list = []

                    # 无子节点
                    orm_list_1 = [orm for orm in behavior_orm_list if orm.group_sub_name == sub_name]
                    for orm in orm_list_1:
                        data = {}
                        data["title"] = orm.key_value
                        data["value"] = []
                        for date_day in date_list:
                            behavior_date_report = {}
                            for behavior_report in behavior_report_list:
                                if behavior_report["key_name"] == orm.key_name and behavior_report["create_date"] == date_day:
                                    if orm.value_type != 2:
                                        behavior_report["key_value"] = int(behavior_report["key_value"])
                                    behavior_date_report = {"title": orm.key_value, "date": date_day, "value": behavior_report["key_value"]}
                                    break
                            if not behavior_date_report:
                                behavior_date_report = {"title": orm.key_value, "date": date_day, "value": 0}
                            data["value"].append(behavior_date_report)
                        sub_data_list.append(data)
                    sub_group_data["data_list"] = sub_data_list
                    sub_group_data_list.append(sub_group_data)
                group_data["sub_data_list"] = sub_group_data_list

            common_group_data_list.append(group_data)

        return self.reponse_json_success(common_group_data_list)


class ReportInfoHandler(SevenBaseHandler):
    """
    :description: 报表信息2.0版本
    """
    @filter_check_params("act_id")
    def get_async(self):
        """
        :description: 报表信息
        :param act_id：活动id
        :param start_date：开始时间
        :param end_date：结束时间
        :return: 列表
        :last_editors: CaiYouBin
        """
        act_id = int(self.get_param("act_id", 0))
        start_date = self.get_param("start_date")
        end_date = self.get_param("end_date")

        condition = ""
        params = []

        condition += "act_id=%s"
        params.append(act_id)
        if start_date != "":
            condition += " and %s<=create_date"
            params.append(start_date)
        if end_date != "":
            condition += " and create_date<%s"
            params.append(end_date)

        behavior_orm_model = BehaviorOrmModel(context=self)
        behavior_report_model = BehaviorReportModel(context=self)
        behavior_orm_list = behavior_orm_model.get_list("is_common=1 OR act_id=%s", order_by="id asc", params=act_id, field="key_name,group_name,group_sub_name,key_value,value_type,is_common")

        behavior_report_list = behavior_report_model.get_dict_list(condition, group_by="key_name", field="key_name,SUM(key_value) AS key_value", params=params)

        #公共映射组（未去重）
        common_groups_1 = [orm.group_name for orm in behavior_orm_list if orm.is_common == 1]
        #公共映射组(去重)
        common_groups = list(set(common_groups_1))
        common_groups.sort(key=common_groups_1.index)

        big_group_list = []
        big_group1 = {}
        big_group1["group_name"] = "全部开盒"
        big_group1["group_data_list"] = []
        for common_group in common_groups:
            group_data = {}
            group_data["group_name"] = common_group
            data_list = []

            # 无子节点
            orm_list = [orm for orm in behavior_orm_list if orm.group_name == common_group and orm.group_sub_name == '']
            for orm in orm_list:
                data = {}
                data["title"] = orm.key_value
                data["value"] = 0
                for behavior_report in behavior_report_list:
                    if behavior_report["key_name"] == orm.key_name:
                        if orm.value_type == 2:
                            data["value"] = behavior_report["key_value"]
                        else:
                            data["value"] = int(behavior_report["key_value"])
                data_list.append(data)
            if len(data_list) > 0:
                group_data["data_list"] = data_list

            # 有子节点
            orm_list_sub = [orm for orm in behavior_orm_list if orm.group_name == common_group and orm.group_sub_name != '']
            if orm_list_sub:
                groups_sub_name = [orm.group_sub_name for orm in orm_list_sub]
                #公共映射组(去重)
                sub_names = list(set(groups_sub_name))
                sub_names.sort(key=groups_sub_name.index)
                sub_group_data_list = []
                for sub_name in sub_names:
                    sub_group_data = {}
                    sub_group_data["group_name"] = sub_name
                    sub_data_list = []

                    # 无子节点
                    orm_list_1 = [orm for orm in behavior_orm_list if orm.group_sub_name == sub_name]
                    for orm in orm_list_1:
                        data = {}
                        data["title"] = orm.key_value
                        data["value"] = 0
                        for behavior_report in behavior_report_list:
                            if behavior_report["key_name"] == orm.key_name:
                                if orm.value_type == 2:
                                    data["value"] = behavior_report["key_value"]
                                else:
                                    data["value"] = int(behavior_report["key_value"])
                        sub_data_list.append(data)
                    sub_group_data["data_list"] = sub_data_list
                    sub_group_data_list.append(sub_group_data)
                group_data["sub_data_list"] = sub_group_data_list
            big_group1["group_data_list"].append(group_data)
        big_group_list.append(big_group1)

        machine_info_model = MachineInfoModel(context=self)
        machine_info_list = machine_info_model.get_list("act_id=%s AND is_release=1", params=act_id)

        for machine_info in machine_info_list:
            group_data = {}
            group_data["group_name"] = machine_info.machine_name
            group_data["group_data_list"] = deepcopy(big_group1["group_data_list"])
            data_list = []
            for behavior_orm in behavior_orm_list:
                if behavior_orm.key_name == "openCount_" + str(machine_info.id) or behavior_orm.key_name == "openUserCount_" + str(machine_info.id):
                    data = {}
                    if "openCount_" in behavior_orm.key_name:
                        data["title"] = deepcopy("开盒次数")
                    if "openUserCount_" in behavior_orm.key_name:
                        data["title"] = deepcopy("开盒人数")

                    data["value"] = 0
                    for behavior_report in behavior_report_list:
                        if behavior_report["key_name"] == behavior_orm.key_name:
                            if behavior_orm.value_type == 2:
                                data["value"] = behavior_report["key_value"]
                            else:
                                data["value"] = int(behavior_report["key_value"])
                    data_list.append(data)

            group_data["group_data_list"][2]["data_list"] = data_list
            big_group_list.append(group_data)

        return self.reponse_json_success(big_group_list)