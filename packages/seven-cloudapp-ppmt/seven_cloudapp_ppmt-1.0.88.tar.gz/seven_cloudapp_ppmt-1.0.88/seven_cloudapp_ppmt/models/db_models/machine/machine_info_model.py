# -*- coding: utf-8 -*-
"""
@Author: HuangJianYi
@Date: 2021-04-19 15:11:42
@LastEditTime: 2021-09-30 16:20:46
@LastEditors: HuangJianYi
@Description: 
"""
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class MachineInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(MachineInfoModel, self).__init__(MachineInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class MachineInfo:

    def __init__(self):
        super(MachineInfo, self).__init__()
        self.id = 0  #
        self.act_id = 0  # act_id
        self.app_id = ""  # app_id
        self.machine_name = ""  # 机台名称
        self.machine_type = 0  # 机台类型：1消耗积分2消耗次数
        self.goods_id = ""  # 商品id
        self.goods_modify_date = "1900-01-01 00:00:00"  # 最后修改商品id时间
        self.sku_id = ""  # sku_id
        self.skin_id = 0  # 主题皮肤id
        self.sort_index = 0  # 排序
        self.is_release = 0  # 是否发布：1发布0-未发布
        self.is_false_prize = 0  # 是否开启虚假中奖
        self.is_buy_endbox = 0  # 是否开启端盒购买
        self.single_lottery_price = 0  # 单抽价格
        self.many_lottery_price = 0  # 连抽价格
        self.many_lottery_num = 0  # 连抽次数
        self.machine_price = 0  # 机台价格
        self.is_repeat_prize = 0  # 是否奖品不重复：0-不重复1-重复
        self.price_gears_id = 0  # 拆盒价格id
        self.series_id = 0  # IP系列id
        self.specs_type = 0  # 中盒规格(6,12)
        self.index_pic = ""  # 首页主图
        self.machine_bg_pic = ""  # 中盒背景图
        self.goods_detail = ""  # 商品详情(json)
        self.box_style_type = 0  # 盲盒样式(1使用模板 2自定义)
        self.box_style_detail = ""  # 盲盒样式详情(json)
        self.sale_type = 0  # 开售方式(1立即开售2定时开售)
        self.sale_date = "1900-01-01 00:00:00"  # 定时开售时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 修改时间

    @classmethod
    def get_field_list(self):
        return ['id', 'act_id', 'app_id', 'machine_name', 'machine_type', 'goods_id', 'goods_modify_date', 'sku_id', 'skin_id', 'sort_index', 'is_release', 'is_false_prize', 'is_buy_endbox', 'single_lottery_price', 'many_lottery_price', 'many_lottery_num', 'machine_price', 'is_repeat_prize', 'price_gears_id', 'series_id', 'specs_type', 'index_pic', 'machine_bg_pic', 'goods_detail', 'box_style_type', 'box_style_detail', 'sale_type', 'sale_date', 'create_date', 'modify_date']

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "machine_info_tb"
