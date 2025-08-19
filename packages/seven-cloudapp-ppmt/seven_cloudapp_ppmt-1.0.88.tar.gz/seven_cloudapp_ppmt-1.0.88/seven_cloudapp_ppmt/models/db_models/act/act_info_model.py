#此文件由rigger自动生成
from seven_framework.mysql import MySQLHelper
from seven_framework.base_model import *


class ActInfoModel(BaseModel):
    def __init__(self, db_connect_key='db_cloudapp', sub_table=None, db_transaction=None, context=None):
        super(ActInfoModel, self).__init__(ActInfo, sub_table)
        self.db = MySQLHelper(config.get_value(db_connect_key))
        self.db_connect_key = db_connect_key
        self.db_transaction = db_transaction
        self.db.context = context

    #方法扩展请继承此类

class ActInfo:

    def __init__(self):
        super(ActInfo, self).__init__()
        self.id = 0  # id
        self.app_id = ""  # app_id
        self.owner_open_id = ""  # 商家OpenID
        self.act_name = ""  # 活动名称
        self.act_type = 0  # 活动类型
        self.theme_id = 0  # 主题ID
        self.store_url = ""  # 店铺地址
        self.close_word = ""  # 关闭小程序文案
        self.share_desc = ""  # 分享内容
        self.rule_desc = ""  # 规则内容
        self.integral_rule = ""  # 积分规则
        self.start_date = "1900-01-01 00:00:00"  # 开始时间
        self.end_date = "1900-01-01 00:00:00"  # 结束时间
        self.refund_count = 0  # 退款次数
        self.is_black = 0  # 是否开启黑名单
        self.sort_index = 0  # 排序号
        self.menu_configed = ""  # 已配置的菜单
        self.finish_progress = 0  # 完成进度
        self.is_release = 0  # 是否发布（1是0否）
        self.is_task = 0  # 是否开启任务(1是0否)
        self.is_throw = 0  # 是否开启投放（1是0否）
        self.is_del = 0  # 是否删除（1是0否）
        self.join_ways = 0  # 活动参与条件（0所有1关注店铺2加入会员）
        self.is_fictitious = 0  # 是否开启虚拟中奖（1是0否）
        self.currency_type = 0  # 抽奖货币类型（0无1次数2积分3价格档位）
        self.task_currency_type = ""  # 任务货币类型（字典数组）
        self.lottery_value = 0  # 单次抽奖消耗次数（积分）
        self.release_date = "1900-01-01 00:00:00"  # 发布时间
        self.create_date = "1900-01-01 00:00:00"  # 创建时间
        self.modify_date = "1900-01-01 00:00:00"  # 更新时间
        self.index_desc = ""  # 首页内容
        self.shakebox_tips = ""  # 摇盒提示
        self.exceed_tips = ""  # 超出次数提示
        self.shakebox_tips_num = 0  # 摇盒提示次数
        self.is_open_match_taobao_order = 0  # 是否开启淘宝订单匹配

    @classmethod
    def get_field_list(self):
        return [
            'id', 'app_id', 'owner_open_id', 'act_name', 'act_type', 'theme_id', 'store_url', 'close_word', 'share_desc', 'rule_desc', 'integral_rule', 'start_date', 'end_date', 'refund_count', 'is_black', 'sort_index', 'menu_configed', 'finish_progress', 'is_release', 'is_task',
            'is_throw', 'is_del', 'join_ways', 'is_fictitious', 'currency_type', 'task_currency_type', 'lottery_value', 'release_date', 'create_date', 'modify_date', 'index_desc', 'shakebox_tips', 'exceed_tips', 'shakebox_tips_num', 'is_open_match_taobao_order'
        ]

    @classmethod
    def get_primary_key(self):
        return "id"

    def __str__(self):
        return "act_info_tb"
