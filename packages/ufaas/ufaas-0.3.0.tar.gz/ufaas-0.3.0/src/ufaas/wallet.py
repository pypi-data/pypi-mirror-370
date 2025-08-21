from decimal import Decimal
from enum import StrEnum

from fastapi_mongo_base.schemas import TenantUserEntitySchema
from pydantic import BaseModel, Field, model_validator

from .enums import Currency


class WalletOwnerType(StrEnum):
    user = "user"
    tenant = "tenant"
    app = "app"
    system = "system"


class WalletPurpose(StrEnum):
    regular = "regular"
    treasury = "treasury"
    test = "test"

    # settlement = "settlement"
    # fee_collector = "fee_collector"
    # income_wallet = "income_wallet"
    # bonus_wallet = "bonus_wallet"
    # reserve = "reserve"


class WalletBalanceType(StrEnum):
    positive = "positive"
    negative = "negative"


class WalletStatus(StrEnum):
    active = "active"
    inactive = "inactive"
    pending = "pending"
    blocked = "blocked"
    deleted = "deleted"


class WalletSchema(TenantUserEntitySchema):
    wallet_purpose: WalletPurpose = WalletPurpose.regular
    owner_type: WalletOwnerType = WalletOwnerType.user
    balance_type: WalletBalanceType = WalletBalanceType.positive
    status: WalletStatus = WalletStatus.active

    main_currency: Currency = Currency.main_currency()
    is_default: bool = True


class BalanceSchema(BaseModel):
    currency: Currency
    total: Decimal = Field(ge=0)
    held: Decimal = Field(ge=0)
    available: Decimal = Field(ge=0)

    @model_validator(mode="before")
    def validate_balance(cls, values: dict[str, object]) -> dict[str, object]:  # noqa: N805
        total = Decimal(values.get("total"))
        held = Decimal(values.get("held"))
        available = Decimal(values.get("available"))
        set_fields = [x is not None for x in (total, held, available)]
        num_set = sum(set_fields)

        if num_set < 2:
            raise ValueError(
                "At least two of 'total', 'held', and 'available' must be set."
            )

        if num_set == 2:
            if total is None:
                values["total"] = held + available
            elif held is None:
                values["held"] = total - available
            elif available is None:
                values["available"] = total - held
        elif num_set == 3 and (total != held + available):
            raise ValueError(
                f"'total' ({total}) must equal "
                f"'held' ({held}) + 'available' ({available})"
            )
        return values


class WalletDetailSchema(WalletSchema):
    balance: dict[str, BalanceSchema] = Field(default_factory=dict)


class WalletCreateSchema(BaseModel):
    user_id: str | None = None
    meta_data: dict | None = None

    wallet_purpose: WalletPurpose = WalletPurpose.regular
    owner_type: WalletOwnerType = WalletOwnerType.user
    balance_type: WalletBalanceType = WalletBalanceType.positive
    status: WalletStatus = WalletStatus.active

    main_currency: Currency = Currency.main_currency()
    is_default: bool = False


class WalletUpdateSchema(BaseModel):
    meta_data: dict | None = None
    is_default: bool | None = None
