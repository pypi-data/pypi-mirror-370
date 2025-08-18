import unittest

from cc_py_commons.utils.lambda_utils import is_event_from_lambda_warmer


class TestLambdaUtils(unittest.TestCase):

	def test_event_from_lambda_warmer(self):
		event = {
			'version': '0',
			'id': 'f70d7afc-e2c0-cb53-10e7-43bcafc4c8fb',
			'detail-type': 'Scheduled Event',
			'source': 'aws.events',
			'account': '791608169866',
			'time': '2023-03-14T10:36:03Z',
			'region': 'us-west-1',
			'resources': ['arn:aws:events:us-west-1:791608169866:rule/BULK_LANE_PRICING_LAMBDA_WARMER_DEV'],
			'detail': {}
		}
		result = is_event_from_lambda_warmer(event)

		self.assertTrue(result)

	def test_event_not_from_lambda_warmer(self):
		event = {
			'Records': [],
		}
		result = is_event_from_lambda_warmer(event)

		self.assertFalse(result)
