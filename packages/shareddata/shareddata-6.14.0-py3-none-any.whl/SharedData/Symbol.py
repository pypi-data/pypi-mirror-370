from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any

class ContractType(Enum):
    STOCK = 'STOCK'
    FUT = 'FUT'
    FOP = 'FOP'
    OPT = 'OPT'
    SWAP = 'SWAP'
    FX = 'FX'
    ETF = 'ETF'

MANDATORY_FIELDS = {
    ContractType.STOCK:     ['symbol', 'exchange', 'currency'],
    ContractType.FUT:       ['symbol', 'exchange', 'expiry', 'currency', 'contract_size'],
    ContractType.FOP:       ['symbol', 'exchange', 'expiry', 'currency', 'contract_size', 'option_type', 'strike'],
    ContractType.OPT:       ['symbol', 'exchange', 'expiry', 'currency', 'option_type', 'strike'],
    ContractType.SWAP:      ['symbol', 'exchange', 'currency', 'underlying'],
    ContractType.FX:        ['symbol', 'base_currency', 'quote_currency'],
    ContractType.ETF:       ['symbol', 'exchange', 'currency', 'underlying'],
}

@dataclass
class Symbol:
    contract_type: ContractType
    fields: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        required = MANDATORY_FIELDS[self.contract_type]
        missing = [f for f in required if f not in self.fields or self.fields[f] is None]
        if missing:
            raise ValueError(f"Missing mandatory fields for {self.contract_type.value}: {missing}")

    def __getitem__(self, item):
        return self.fields[item]

    def __setitem__(self, key, value):
        self.fields[key] = value
