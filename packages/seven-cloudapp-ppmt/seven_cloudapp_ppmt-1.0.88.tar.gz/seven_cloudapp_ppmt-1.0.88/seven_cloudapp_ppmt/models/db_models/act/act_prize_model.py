
#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ActPrizeModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActPrizeModel, self).__init__(ActPrize, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类
    
class ActPrize:

    def __init__(self):
        super(ActPrize, self).__init__()
        self.id = 0  # 标识
        self.act_id = 0  # 活动标识
        self.award_id = ""  # 奖项标识
        self.app_id = ""  # 应用唯一标识
        self.owner_open_id = ""  # 商家OpenID
        self.machine_id = 0  # 机台ID
        self.ascription_type = 0  # 奖品归属（0-活动奖品1-任务奖品）
        self.prize_name = ""  # 奖品名称
        self.prize_title = ""  # 奖品子标题
        self.prize_pic = ""  # 奖品图
        self.prize_detail = ""  # 奖品详情图（json）
        self.unpack_pic = ""  # 拆盒图
        self.toys_pic = ""  # 玩具柜图
        self.goods_id = 0  # 商品id
        self.goods_code = ""  # 商品编码
        self.goods_code_list = ""  # 多个sku商品编码
        self.prize_type = 0  # 奖品类型（1实物2虚拟物品）
        self.prize_price = 0  # 奖品价格
        self.probability = 0  # 奖品权重
        self.chance = 0  # 概率
        self.surplus = 0  # 奖品库存
        self.is_surplus = 0  # 是否显示奖品库存（1显示0-不显示）
        self.is_prize_notice = 0  # 是否显示中奖跑马灯
        self.prize_limit = 0  # 中奖限制
        self.prize_total = 0  # 奖品总数
        self.tag_id = 0  # 标签ID
        self.hand_out = 0  # 已发出数量
        self.is_sku = 0  # 是否有SKU
        self.sort_index = 0  # 排序号
        self.is_release = 0  # 是否发布（1是0否）
        self.sku_detail = ""  # sku详情
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间

    @classmethod
    def get_field_list(self):
        return ['id', 'act_id', 'award_id', 'app_id', 'owner_open_id', 'machine_id', 'ascription_type', 'prize_name', 'prize_title', 'prize_pic', 'prize_detail', 'unpack_pic', 'toys_pic', 'goods_id', 'goods_code', 'goods_code_list', 'prize_type', 'prize_price', 'probability', 'chance', 'surplus', 'is_surplus', 'is_prize_notice', 'prize_limit', 'prize_total', 'tag_id', 'hand_out', 'is_sku', 'sort_index', 'is_release', 'sku_detail', 'create_date', 'modify_date']
        
    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_prize_tb"
    