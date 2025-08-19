# -*- coding: utf-8 -*-
"""
:Author: HuangJingCan
:Date: 2020-04-16 14:38:22
@LastEditTime: 2022-07-25 14:39:33
@LastEditors: HuangJianYi
:Description: 潮玩盲盒基础路由
"""
# 框架引用
from seven_framework.web_tornado.monitor import MonitorHandler
from seven_cloudapp.handlers.core import *
from seven_cloudapp.handlers.server import *
from seven_cloudapp.handlers.client import *

from seven_cloudapp_ppmt.handlers.server import *
from seven_cloudapp_ppmt.handlers.client import *


def seven_cloudapp_ppmt_route():
    return [
        (r"/monitor", MonitorHandler),
        (r"/", IndexHandler),
        # 千牛端接口
        (r"/server/saas_custom", base_s.SaasCustomHandler),
        (r"/server/left_ad_list", app_s.LeftAdListHandler),  #左侧广告
        (r"/server/login", user_s.LoginHandler),
        (r"/server/gear_log", user_s.GearLogHandler),
        (r"/server/user_list", user_s.UserListHandler),
        (r"/server/gear_value", user_s.GearValueHandler),
        (r"/server/user_status", user_s.UserStatusHandler),
        (r"/server/user_machine_list", user_s.UserMachineListHandler),
        (r"/server/pay_order_list", order_s.PayOrderListHandler),
        (r"/server/prize_order_list", order_s.PrizeOrderListHandler),
        (r"/server/prize_roster_list", order_s.PrizeRosterListHandler),
        (r"/server/prize_order_status", order_s.PrizeOrderStatusHandler),
        (r"/server/prize_order_remarks", order_s.PrizeOrderRemarksHandler),
        (r"/server/app_info", app_s.AppInfoHandler),
        (r"/server/base_info", app_s.BaseInfoHandler),
        (r"/server/telephone", app_s.TelephoneHandler),
        (r"/server/app_update", app_s.AppUpdateHandler),
        (r"/server/act", act_s.ActHandler),
        (r"/server/act_del", act_s.ActDelHandler),
        (r"/server/act_info", act_s.ActInfoHandler),
        (r"/server/act_save", act_s.ActSaveHandler),
        (r"/server/act_list", act_s.ActListHandler),
        (r"/server/act_create", act_s.ActCreateHandler),
        (r"/server/act_type", act_s.ActTypeListHandler),
        (r"/server/act_qrcode", act_s.ActQrCodeHandler),
        (r"/server/act_review", act_s.ActReviewHandler),
        (r"/server/next_progress", act_s.NextProgressHandler),
        (r"/server/theme_update", theme_s.ThemeUpdate),
        (r"/server/skin_list", theme_s.SkinListHandler),
        (r"/server/theme_list", theme_s.ThemeListHandler),
        (r"/server/machine", machine_s.MachineHandler),
        (r"/server/machine_del", machine_s.MachineDelHandler),
        (r"/server/machine_list", machine_s.MachineListHandler),
        (r"/server/machine_release", machine_s.MachineReleaseHandler),
        (r"/server/update_machineprice_by_gearid", machine_s.UpdateMachinePriceByGearIdHandler),
        (r"/server/goods_list", goods_s.GoodsListHandler),
        (r"/server/goods_info", goods_s.GoodsInfoHandler),
        (r"/server/goods_check", goods_s.GoodsCheckHandler),
        (r"/server/get_goods_list", goods_s.GoodsListByGoodsIDHandler),
        (r"/server/prize", prize_s.PrizeHandler),
        (r"/server/prize_del", prize_s.PrizeDelHandler),
        (r"/server/prize_list", prize_s.PrizeListHandler),
        (r"/server/prize_release", prize_s.PrizeReleaseHandler),
        (r"/server/prize_order_import", order_s.PrizeOrderImportHandler),
        (r"/server/prize_order_export", order_s.PrizeOrderExportHandler),
        (r"/server/prize_roster_export", order_s.PrizeRosterListExportHandler),
        (r"/server/report_info", report_s.ReportInfoHandler),
        (r"/server/report_list2", report_s.ReportInfoListHandler),
        (r"/server/send_sms", app_s.SendSmsHandler),
        (r"/server/series", series_s.SeriesHandler),
        (r"/server/series_del", series_s.SeriesDelHandler),
        (r"/server/series_list", series_s.SeriesListHandler),
        (r"/server/series_release", series_s.SeriesReleaseHandler),
        (r"/server/price", price_s.PriceHandler),
        (r"/server/price_list", price_s.PriceListHandler),
        (r"/server/price_status", price_s.PriceStatusHandler),
        (r"/server/price_list_recover", price_s.PriceListRecoverHandler),
        (r"/server/throw_goods_list", throw_s.ThrowGoodsListHandler),
        (r"/server/async_throw_goods", throw_s.AsyncThrowGoodsHandler),
        (r"/server/init_throw_goods_list", throw_s.InitThrowGoodsListHandler),
        (r"/server/save_throw_goods_status", throw_s.SaveThrowGoodsStatusHandler),
        (r"/server/init_throw_goods_callback", throw_s.InitThrowGoodsCallBackHandler),
        (r"/server/get_launch_plan_status", launch_s.GetLaunchPlanStatusHandler),  #获取投放计划状态
        (r"/server/reset_launch_goods", launch_s.ResetLaunchGoodsHandler),  #重置商品投放 删除已投放的记录并将活动投放状态改为未投放
        (r"/server/add_launch_goods_list", launch_s.AddLaunchGoodsListHandler),  #添加投放商品
        (r"/server/can_launch_goods_list", launch_s.CanLaunchGoodsListHandler),  #获取可投放商品列表（获取当前会话用户出售中的商品列表）
        (r"/server/get_launch_progress", launch_s.GetLaunchProgressHandler),  #获取投放进度
        (r"/server/init_launch_goods_list", launch_s.InitLaunchGoodsHandler),  #初始化活动投放
        (r"/server/init_launch_goods_callback", launch_s.InitLaunchGoodsCallBackHandler),  #初始化投放商品回调接口
        (r"/server/save_launch_goods_status", launch_s.UpdateLaunchGoodsStatusHandler),  #保存更改投放商品的状态
        (r"/server/launch_goods_list", launch_s.LaunchGoodsListHandler),  #投放商品列表
        (r"/server/async_launch_goods", launch_s.AsyncLaunchGoodsStatusHandler),  #同步投放商品列表

        # 2.0
        (r"/server/get_power_menu", power_s.GetPowerMenuHandler),
        (r"/server/task", task_s.TaskSaveHandler),
        (r"/server/task_list", task_s.TaskListHandler),
        (r"/server/exchange", exchange_s.ExchangeSaveHandler),
        (r"/server/exchange_list", exchange_s.ExchangeListHandler),
        (r"/server/check_buy_endbox", machine_s.CheckBuyEndboxHandler),
        (r"/server/endbox_order_list", order_s.EndBoxOrderListHandler),
        (r"/server/prop", user_s.PropHandler),
        (r"/server/prop_log_list", user_s.PropLogHandler),
        (r"/server/user_detail", user_s.UserDetailHandler),
        (r"/server/integral", user_s.SurplusIntegralHandler),
        (r"/server/lottery_value_log_list", user_s.LotteryValueLogHandler),
        # 2.1优化
        (r"/server/checking_price_gear", machine_s.CheckingPriceGearHandler),  #验证价格档位
        # 2.2
        (r"/server/give_prop_list", user_s.PropGiveListHandler),
        (r"/server/get_high_power_list", power_s.GetHighPowerListHandler),
        #2.4
        (r"/server/check_gm_power", app_s.CheckGmPowerHandler),  #获取是否有GM工具权限 用于GM工具
        (r"/server/get_appid_by_gm", app_s.GetAppidByGmHandler),  #根据店铺名称返回应用标识 用于GM工具

        # 客户端接口
        (r"/client/login", user.LoginHandler),
        (r"/client/user", user.UserHandler),
        (r"/client/sync_pay_order", user.SyncPayOrderHandler),
        (r"/client/getunpacknum", user.GetUnpackNumHandler),
        (r"/client/user_prize_order", user.PrizeOrderHandler),
        (r"/client/user_prize_order_series", user.PrizeOrderBySeriesHandler),
        (r"/client/gear_list_num", user.GetNumByPriceGearsListHandler),
        (r"/client/get_horseracelamp_List", user.GetHorseRaceLampListHandler),
        (r"/client/act_info", act.ActInfoHandler),
        (r"/client/machine_list", act.MachineListHandler),
        (r"/client/prize_list", act.PrizeListHandler),
        (r"/client/minbox_list", act.MinboxListHandler),
        (r"/client/theme_info", theme.ThemeInfoHandler),
        (r"/client/theme", theme.ThemeSaveHandler),
        (r"/client/skin", theme.SkinSaveHandler),
        (r"/client/lottery", lottery.LotteryHandler),
        (r"/client/new_lottery", lottery.NewLotteryHandler),
        (r"/client/shakeit", lottery.ShakeItHandler),
        (r"/client/new_shakeit", lottery.NewShakeItHandler),
        (r"/client/recover", lottery.RecoverHandler),
        (r"/client/shakeit_prize_list", lottery.ShakeItPrizeListHandler),
        (r"/client/new_shakeit_prize_list", lottery.NewShakeItPrizeListHandler),
        (r"/client/all_prize_list", prize.AllPrizeListHandler),
        (r"/client/user_prize_list", prize.UserPrizeListHandler),
        (r"/client/address", address.GetAddressInfoHandler),
        (r"/client/get_app_expire", app.GetAppExpireHandler),
        (r"/client/series_list", series.SeriesListHandler),
        (r"/client/match_taobao_order", user.MatchTaobaoOrderHandler),  # 匹配单笔淘宝订单获取次数
        # 2.0
        (r"/client/get_power_menu", power.GetPowerMenuHandler),
        (r"/client/task_share", task.ShareHandler),
        (r"/client/task_follow", task.FollowHandler),
        (r"/client/task_list", task.TaskListHandler),
        (r"/client/task_inivite", task.InviteHandler),
        (r"/client/task_collect", task.CollectGoodsHandler),
        (r"/client/task_weekly_sign", task.WeeklySignHandler),
        (r"/client/task_inivite_reward", task.InviteRewardHandler),
        (r"/client/exchange", exchange.ExchangeHandler),
        (r"/client/exchange_list", exchange.ExchangeListHandler),
        (r"/client/user_detail", user.GetUserDetailHandler),
        (r"/client/integral_list", user.GetIntegralListHandler),
        (r"/client/lottery_all", lottery.LotteryAllHandler),
        (r"/client/use_reset_card", lottery.UseResetCardHandler),
        (r"/client/use_perspective_card", lottery.UsePerspectiveCardHandler),
        (r"/client/new_use_perspective_card", lottery.NewUsePerspectiveCardHandler),
        (r"/client/active_new_user", task.ActiveNewUserHandler),
        #2.2
        (r"/client/give_prop", user.GivePropHandler),
        (r"/client/get_prop_give", user.GetPropGiveHandler),
        (r"/client/give_prop_list", user.PropGiveListHandler),
        (r"/client/prop_log_list", user.PropLogListHandler),

        #2.4
        (r"/client/get_crm_integral", user.GetCrmIntegralHandler),
        (r"/client/get_is_member", user.GetIsMemberHandler),
        (r"/client/crm_integral_gear_list", act.CrmIntegralGearlListHandler),
        (r"/client/get_high_power_list", power.GetHighPowerListHandler)
    ]
