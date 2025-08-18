from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.carriers.account_carrier_map import AccountCarrierMap
class AccountCarrierMapSchema(CamelCaseSchema):
  class Meta:
    unknown = EXCLUDE

  account_id = fields.Integer()
  carrier_id = fields.UUID()
  status = fields.String()
  customer_code = fields.String(allow_none=True, missing=None)
  no_dispatch = fields.Boolean(allow_none=True, missing=None)
  
  @post_load
  def make_account_carrier_map(self, data, **kwargs):
      return AccountCarrierMap(**data)  