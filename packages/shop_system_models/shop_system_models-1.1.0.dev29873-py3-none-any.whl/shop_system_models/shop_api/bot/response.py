from shop_system_models.shop_api.bot.request import OrderStatusModel
from pydantic import BaseModel


class OrderStatusResponseModel(OrderStatusModel):
    id: str


class OrderStatusResponseModelWithShopName(BaseModel):
    shop_name: str
    order_statuses: list[OrderStatusResponseModel]
