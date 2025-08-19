from fastapi import APIRouter
from svc_order_zxw.config import DYNAMIC_CONFIG
from app_tools_zxw.Funcs.fastapi_logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/apple_pay", tags=["苹果内购"])


@router.get("/config/enable_ios_iap", summary="获取是否开启苹果内购")
async def get_IAP_config():
    """直接从缓存读取配置，无IO操作"""
    logger.info(f"{DYNAMIC_CONFIG=}")
    return DYNAMIC_CONFIG.get("enable_iOS_IAP", True)
