# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-08-31 11:47:42
@LastEditTime: 2021-08-31 15:34:31
@LastEditors: HuangJianYi
@Description: 
"""

#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class PropGiveModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(PropGiveModel, self).__init__(PropGive, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类


class PropGive:

    def __init__(self):
        super(PropGive, self).__init__()
        self.id = 0  # id
        self.guid = ""  # guid
        self.app_id = ""  # app_id
        self.act_id = 0  # act_id
        self.open_id = ""  # open_id
        self.user_nick = ""  # 用户昵称
        self.draw_open_id = ""  # 领取人
        self.draw_user_nick = ""  # 领取人用户昵称
        self.prop_type = 0  #道具类型(2透视卡3提示卡4重抽卡)
        self.give_num = 0  # 赠送数量
        self.give_status = 0  # 赠送状态(0未领取1已领取2已失效)
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.create_date_int = 0  # 创建天
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'guid', 'app_id', 'act_id', 'open_id', 'user_nick', 'draw_open_id', 'draw_user_nick', 'prop_type', 'give_num', 'give_status', 'create_date', 'create_date_int', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "prop_give_tb"
