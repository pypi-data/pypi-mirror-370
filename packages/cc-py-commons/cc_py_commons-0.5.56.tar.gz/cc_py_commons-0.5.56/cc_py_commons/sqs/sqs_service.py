import json
from uuid import uuid4
import boto3

class SqsService:
	def send(self, queue_url, message, delaySeconds=0, messageGroupId=None):
		'''
		Sends a message to the specified queue and returns the messageId. 
		The messageId can be used to lookup and delete the message in the queue.
		'''
		sqs = boto3.client('sqs')
		if messageGroupId:
			response = sqs.send_message(
				QueueUrl=queue_url,
				MessageBody=message,
				DelaySeconds=delaySeconds,
				MessageAttributes={},
				MessageGroupId=messageGroupId
			)
		else:
			response = sqs.send_message(
				QueueUrl=queue_url,
				MessageBody=message,
				DelaySeconds=delaySeconds,
				MessageAttributes={}
			)
		return response.get('MessageId')

	def send_batches(self, queue_url, messages):
		'''
		Sends all messages to the specified queue in groups of 10 (the limit of send_batch)
		The messageId can be used to lookup and delete the message in the queue.
		Args:
			queue_url (str): The URL of the Amazon SQS queue
			messages (list): List of messages to be sent

		Returns:
			dict: Results containing 'successful' and 'failed' message lists
		'''
		results = {
			'successful': [],
			'failed': []
		}

		if not messages:
			return results

		sqs = boto3.client('sqs')
		entries = [
			{
				# each message must have a unique id
				'Id': str(uuid4()),
				'MessageBody': json.dumps(message),
			}
			for message in messages
		]

		# SQS can only process 10 messages per batch
		batch_size = 10

		# Split messages into batches of 10
		for i in range(0, len(entries), batch_size):
			batch = entries[i:i + batch_size]

			try:
				response = sqs.send_message_batch(
					QueueUrl=queue_url,
					Entries=batch
				)

				# Track successful and failed messages
				if 'Successful' in response:
					results['successful'].extend(response['Successful'])
				if 'Failed' in response:
					results['failed'].extend(response['Failed'])

			except Exception as e:
				# Mark all messages in failed batch
				failed_batch = [{
					'Id': entry['Id'],
					'Error': str(e),
					'Message': entry['MessageBody']
				} for entry in batch]
				results['failed'].extend(failed_batch)

		return results
