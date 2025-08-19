"""
Abstract base class for defining ML Models.

DO NOT CHANGE THIS CODE DURING IMPLEMENTATION.
"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from abc import ABC, abstractmethod


class BaseAdapter(ABC):
	"""
	Abstract class to be implemented.
	"""

	@abstractmethod
	def send_request(self):
		"""
		Used by the client(s) to send images to the server.

		args:
			datetime: Used as an ID of the request. Should be datetime in utc format. e.g. datetime.datetime.now(timezone.utc)
			image_bytes_list: list of images in bytes.
			tool_name: name of the ML service.
			params: a dictionary of parameters as needed by the service.
		"""

		raise NotImplementedError



	@abstractmethod
	def send_response(self):
		"""
		Sends back the response from the server. Normally, the response will be converted to a native Python data type.
		"""
		
		raise NotImplementedError


