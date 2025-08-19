from fastapi import APIRouter
from svc_order_zxw.定时任务.task2_定时获取动态配置 import DYNAMIC_CONFIG


router = APIRouter(prefix="/apple_pay", tags=["苹果内购"])


@router.get("/config/enable_ios_iap", summary="获取是否开启苹果内购")
async def get_IAP_config():
    """直接从缓存读取配置，无IO操作"""
    return DYNAMIC_CONFIG.get("enable_iOS_IAP", True)
