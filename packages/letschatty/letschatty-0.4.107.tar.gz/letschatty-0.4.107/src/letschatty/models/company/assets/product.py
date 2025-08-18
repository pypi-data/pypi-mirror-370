from ...base_models.chatty_asset_model import CompanyAssetModel, ChattyAssetPreview
from typing import Dict, Any, Optional, ClassVar
from pydantic import Field, field_validator
import pycountry

class ProductPreview(ChattyAssetPreview):
    color: str = Field(default="#000000")
    price: Optional[Dict[str, float]] = Field(default=None)

    @classmethod
    def get_projection(cls) -> dict[str, Any]:
        return super().get_projection() | {"color": 1, "description": 1, "price": 1}

    @classmethod
    def from_asset(cls, asset: 'Product') -> 'ProductPreview':
        return cls(
            _id=asset.id,
            name=asset.name,
            company_id=asset.company_id,
            created_at=asset.created_at,
            color=asset.color,
            updated_at=asset.updated_at
        )

class Product(CompanyAssetModel):
    name: str
    price: Optional[Dict[str, float]] = Field(default=None)
    information: Optional[str] = Field(default=None)
    parameters: Optional[Dict[str, Any]] = Field(default=None)
    external_id: Optional[str] = Field(default=None)
    preview_class: ClassVar[type[ProductPreview]] = ProductPreview
    color: str = Field(default="#000000")

    @field_validator('price', mode='before')
    def validate_price(cls, v: Dict[str, float]):
        if v is None:
            return v
        for currency, amount in v.items():
            try:
                pycountry.currencies.get(alpha_3=currency)
            except KeyError:
                raise ValueError(f"Invalid currency code: {currency}. Must be a valid ISO 4217 currency code.")
            if amount < 0:
                raise ValueError(f"Price amount must be non-negative for currency {currency}")

        return v

