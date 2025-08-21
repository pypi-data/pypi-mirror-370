from typing import Literal

from pydantic import BaseModel, Field


class ProtocolSchema(BaseModel):
    protocol: Literal["H2", "VVS"] = Field(
        description="The DeFi protocol name. Options: H2, VVS"
    )


class ProtocolSymbolSchema(ProtocolSchema):
    symbol: str = Field(
        description="The farm symbol (e.g., 'zkCRO-AMPLY', 'zkCRO-MOON', 'zkCRO-CRO', 'CRO-CAW')"
    )
