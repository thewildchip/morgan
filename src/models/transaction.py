from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, getcontext
from datetime import datetime
from uuid import uuid4
from typing import Optional, Literal, Dict, Any
from zoneinfo import ZoneInfo   # for timezone handling if needed

# plus: import your utils for money/time conversion (we'll reference them)
from src.utils.money import to_decimal
from src.utils.time import parse_iso_to_utc, ISO_UTC, to_local_display

INCOME = "income"
EXPENSE = "expense"

@dataclass
class Transaction:
    id: str = field(default_factory=lambda: str(uuid4()))
    ts: datetime  # internal: timezone-aware UTC datetime
    amount: Decimal  # signed: positive = income, negative = expense
    type: Literal["income", "expense"]
    category: str
    note: Optional[str] = None

    def __post_init__(self):
        
        if isinstance(self.ts, str):
            self.ts = parse_iso_to_utc(self.ts)

        self.amount = to_decimal(self.amount)
        
        if self.type == INCOME and self.amount < 0:
            self.amount = abs(self.amount)
        
        elif self.type == EXPENSE and self.amount > 0:
            self.amount = -abs(self.amount)

        self.category = self.category.strip()
        if not self.category:
            raise ValueError()
        
        if not (len(self.category) <= 50 and len(self.note) <= 500):
            raise ValueError()
        
        if not self.id:
            self.id = str(uuid4())

        if self.type not in (INCOME, EXPENSE):
            raise ValueError()
        
    def to_dict(self):

        return {
            "id": self.id,
            "ts": ISO_UTC(self.ts),
            "amount": str(self.amount),
            "type": self.type,
            "category": self.category,
            "note": "" if not self.note else self.note
        }

    def from_dict(cls, d: dict) -> "Transaction":
        ts = parse_iso_to_utc(d["ts"])
        amount = to_decimal(d[amount])

        note = None if not d["note"] else d["note"]

        transaction = Transaction(ts, 
                                  amount, 
                                  d["type"],
                                  d["category"],
                                  note)
        return transaction
    

    def is_expense(self) -> bool:
        return self.amount < Decimal("0")

    def is_income(self) -> bool:
        return self.amount > Decimal("0")
    
    def abs_amount(self) -> Decimal:
        return abs(self.amount)