from marshmallow import fields, EXCLUDE, post_load
from cc_py_commons.schemas.camel_case_schema import CamelCaseSchema
from cc_py_commons.bids.bid import Bid
from cc_py_commons.bids.bid_history_schema import BidHistorySchema

class BidSchema(CamelCaseSchema):
  class Meta:
    unknown = EXCLUDE

  id = fields.UUID()
  quote_id = fields.UUID()
  carrier_id = fields.UUID()
  receipt_id = fields.String(allow_none=True, missing=None)
  amount = fields.Integer()
  estimated_days = fields.Integer(allow_none=True, missing=None)
  notes = fields.String(allow_none=True, missing=None)
  match_score = fields.Float(allow_none=True)
  status_id = fields.UUID()
  pickup_date = fields.Date()
  delivery_date = fields.Date()
  decline_reason = fields.String(allow_none=True, missing=None)
  bid_histories = fields.List(fields.Nested(BidHistorySchema), allow_none=True)
  origin_deadhead = fields.Float(allow_none=True)
  porus_truck_id = fields.UUID(allow_none=True, missing=None)
  truck_lane_id = fields.UUID(allow_none=True, missing=None)
  distance = fields.Float(allow_none=True, missing=None)
  origin_city = fields.String(missing=None)
  origin_state = fields.String(missing=None)
  origin_zip = fields.String(allow_none=True, missing=None)
  dest_city = fields.String(missing=None)
  dest_state = fields.String(missing=None)
  dest_zip = fields.String(allow_none=True, missing=None)
  invite_emailed_at = fields.DateTime(allow_none=True)
  
  @post_load
  def make_bid(self, data, **kwargs):
      return Bid(**data)
   