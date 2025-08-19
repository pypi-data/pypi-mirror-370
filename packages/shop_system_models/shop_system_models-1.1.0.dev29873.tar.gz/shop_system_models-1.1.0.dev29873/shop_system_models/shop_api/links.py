from typing import Optional, Dict, Any
from pydantic import Field, HttpUrl
from fastapi import HTTPException
from pydantic import BaseModel, field_validator



from shop_system_models.shop_api import MetaBaseModel


class ServiceLink(MetaBaseModel):
    """Model representing a link to another service."""
    service_name: str
    url: HttpUrl
    resource_id: str
    link_metadata: Optional[Dict[str, Any]] = Field(default_factory=lambda: {})


class ServiceLinkResponse(MetaBaseModel):
    """Response model for service link operations."""
    link_id: str
    service_name: str
    resource_id: str
    success: bool = True
    error: Optional[str] = None


class LinkBlocksModel(BaseModel):
    contacts: str | None = "https://teletype.in/@tg-shops/09hOkoJjizN"  # Teletype link
    info: str | None = "https://teletype.in/@tg-shops/2vZa_0ykcCF"  # Teletype link

    @field_validator("contacts", "info", mode="before")
    def link_validation(cls, value):
        if value and (not value.startswith("http://") and not value.startswith("https://")):
            raise HTTPException(status_code=400, detail=f'Invalid link: "{value}"')
        return value
