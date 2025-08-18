import datetime
import uuid
from dataclasses import dataclass, field

@dataclass
class AccountCarrierMap:
  account_id: int
  carrier_id: uuid.UUID
  status: str
  customer_code: str = field(default=None)
  warmup_email_sent_at: datetime.date = field(default=None)
  no_dispatch: bool = field(default=False)