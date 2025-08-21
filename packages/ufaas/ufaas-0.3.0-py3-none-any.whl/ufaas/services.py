import os
from datetime import datetime

import httpx
from usso.utils import agent

from .hold import HoldStatus, WalletHoldCreateSchema, WalletHoldSchema
from .proposal import Participant, ProposalCreateSchema, ProposalSchema
from .wallet import WalletDetailSchema


class AccountingClient(httpx.AsyncClient):
    def __init__(self, tenant_id: str) -> None:
        accounting_service_url = os.getenv(
            "ACCOUNTING_SERVICE_URL", "https://wallets.uln.me"
        )
        super().__init__(
            base_url=f"{accounting_service_url}/api/accounting/v1"
        )
        self.tenant_id = tenant_id

    async def get_token(self, scopes: str | list[str]) -> str:
        if isinstance(scopes, str):
            scopes = [scopes]

        jwt = agent.generate_agent_jwt(
            scopes=scopes,
            aud="accounting",
            tenant_id=self.tenant_id,
        )
        token = await agent.get_agent_token_async(jwt)
        self.headers["Authorization"] = f"Bearer {token}"
        return token

    async def get_wallet(self, wallet_id: str) -> WalletDetailSchema:
        await self.get_token("read:finance/accounting/wallet")
        response = await self.get(f"/wallets/{wallet_id}")
        response.raise_for_status()
        return WalletDetailSchema.model_validate(response.json())

    async def get_holds(self, wallet_id: str) -> list[WalletHoldSchema]:
        await self.get_token("read:finance/accounting/hold")
        response = await self.get(f"/wallets/{wallet_id}/holds")
        response.raise_for_status()
        return [
            WalletHoldSchema.model_validate(item)
            for item in response.json().get("items", [])
        ]

    async def total_held_amount(
        self,
        wallet_id: str,
        currency: str,
        status: HoldStatus = HoldStatus.ACTIVE,
    ) -> float:
        holds = await self.get_holds(wallet_id)
        return sum(
            hold.amount
            for hold in holds
            if hold.currency == currency and hold.status == status
        )

    async def create_hold(
        self,
        wallet_id: str,
        currency: str,
        amount: float,
        expires_at: datetime,
    ) -> WalletHoldSchema:
        await self.get_token("create:finance/accounting/hold")
        response = await self.post(
            f"/wallets/{wallet_id}/holds",
            json=WalletHoldCreateSchema(
                currency=currency,
                amount=amount,
                expires_at=expires_at,
                status=HoldStatus.ACTIVE,
            ).model_dump(mode="json"),
        )
        response.raise_for_status()
        return WalletHoldSchema.model_validate(response.json())

    async def create_proposal(
        self,
        *,
        from_wallet_id: str,
        to_wallet_id: str,
        currency: str,
        amount: float,
        description: str | None = None,
        note: str | None = None,
        hold_id: str | None = None,
    ) -> ProposalSchema:
        await self.get_token("create:finance/accounting/proposal")
        response = await self.post(
            "/proposals",
            json=ProposalCreateSchema(
                participants=[
                    Participant(
                        wallet_id=from_wallet_id,
                        amount=-amount,
                        hold_id=hold_id,
                    ),
                    Participant(wallet_id=to_wallet_id, amount=amount),
                ],
                amount=amount,
                currency=currency,
                description=description,
                note=note,
            ).model_dump(mode="json"),
        )
        response.raise_for_status()
        return ProposalSchema.model_validate(response.json())
