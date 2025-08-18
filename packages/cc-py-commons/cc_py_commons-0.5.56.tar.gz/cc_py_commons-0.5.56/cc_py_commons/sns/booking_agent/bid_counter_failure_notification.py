from cc_py_commons.sns.sns_service import SnsService
from cc_py_commons.utils.logger_v2 import logger


class BidCounterFailureNotification:

    def __init__(self, app_config):
        self._app_config = app_config

    def send(self, bid_id, reason):
        subject = 'bid-counter-failure'
        message = '{' + f'"bidId" : "{bid_id}", ' \
                        f'"failureReason" : "{reason}", ' \
                        f'"subject" : "{subject}", ' \
                        f'"className":  "{self._app_config.BID_COUNTER_FAILURE_SNS_CLASS_NAME}"' + '}'
        logger.debug(f"sending BidCounterFailureNotification {message} to {self._app_config.BOOKING_AGENT_SNS_ARN}")

        try:
            sns_service = SnsService()
            sns_service.send(self._app_config.BOOKING_AGENT_SNS_ARN, subject, message)
        except Exception as e:
            logger.exception(f"failed to send message to {self._app_config.BOOKING_AGENT_SNS_ARN}: {message} - {e}", e)
