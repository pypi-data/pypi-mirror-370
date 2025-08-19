"""
Adapter for client-server(gateway) communication.
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grpc
from google.protobuf.timestamp_pb2 import Timestamp
import resources.grpc.server_proto.external_tool_service_pb2 as external_tool_service_pb2
import resources.grpc.server_proto.external_tool_service_pb2_grpc as external_tool_service_pb2_grpc
from external_vision_gateway_adapter.base_adapter import BaseAdapter


class ServerClientAdapter(BaseAdapter):

	def __init__(self, ip="0.0.0.0", port=50051, timeout=2):

		self.ip = ip
		self.port = port
		self.timeout = timeout
		self.max_message_length = 50 * 1024 * 1024  #50MB max

	
	def send_request(self, datetime, 
					image_bytes_list, tool_name,
					params=None):
		"""
		Used by the client(s) to send images to the server.

		args:
			image_bytes: list of images in bytes. Images are expected to be in RGB format.
			tool_name: name of the ML service.
			params: additional parameters for the ML service in dict format.
		"""

		assert len(image_bytes_list) > 0, "There must be at least 1 element in the image_bytes_list"

		channel = grpc.insecure_channel(

			f"{self.ip}:{self.port}",
			options=[
		        ('grpc.max_send_message_length', self.max_message_length),
		        ('grpc.max_receive_message_length', self.max_message_length),
		    ]
		)
		


		stub = external_tool_service_pb2_grpc.ExternalToolServiceStub(channel)

		timestamp = Timestamp()
		timestamp.FromDatetime(datetime)

		request = external_tool_service_pb2.ExternalToolRequest(req_datetime=timestamp, tool_name=tool_name, payload=image_bytes_list, params=params)

		try:

			response = self.send_response(stub, request, self.timeout)
			return response

		except grpc.RpcError as e:
			print(f"gRPC Error: {e.code()} - {e.details()}")
			return e


	def send_response(self, stub, request, timeout):
		"""
		Used to convert the response from the gateway into a native python format.
		"""

		gateway_response = stub.HandleExternalToolRequest(request, timeout=timeout)

		#convert the gateway response into a python's native Dictionary type.
		result_json = {}

		for k, v in gateway_response.results.fields.items():

			result_json[k] = []

			for item in v.list_value:
				result_json[k].append(item)
		

		return result_json


		

	