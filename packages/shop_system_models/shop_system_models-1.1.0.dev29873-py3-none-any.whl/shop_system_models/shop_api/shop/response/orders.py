from typing import List, Optional
from pydantic import Field
from pydantic import BaseModel

from shop_system_models.shop_api import MetaBaseModel
from shop_system_models.shop_api.shop.request.orders import OrderModel, DeliveryTypeModel
from shop_system_models.shop_api.shop.response.products import PaginationResponseModel


class OrderResponseModel(OrderModel):
    """Response model for a single order."""
    id: str


class OrderListResponseModel(BaseModel):
    """Response model for a list of orders."""
    orders: List[OrderResponseModel]
    page_info: PaginationResponseModel


class DeliveryTypeResponseModel(DeliveryTypeModel):
    """Response model for a delivery type."""
    id: str 