from external_vision_gateway_adapter.server_client_adapter import ServerClientAdapter
from datetime import datetime, timezone

class TestAdapter:

	def __init__(self, ip="192.168.0.81", port=50051, timeout=5):

		self.server = ServerClientAdapter(ip=ip, port=port, timeout=timeout)

	@staticmethod
	def load_image(image_path):
		"""Read an image file as binary data."""
		with open(image_path, "rb") as f:
			return f.read()


	def send_image(self, image_path, tool_name):
		# Load image data
		image_data = [self.load_image(img_path) for img_path in image_path]

		datetime_now = datetime.now(timezone.utc)

		response = self.server.send_request(datetime=datetime_now, image_bytes_list=image_data, tool_name=tool_name)
		
		return response


if __name__ == '__main__':

	adapter_instance = TestAdapter()
	image_path = ["test.bmp"]  # Replace with your image file path
	response = adapter_instance.send_image(image_path, 'discoloration')

	print(response)