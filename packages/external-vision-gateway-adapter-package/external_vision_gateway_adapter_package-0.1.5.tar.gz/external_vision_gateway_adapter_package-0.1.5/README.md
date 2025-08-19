# external-vision-gateway-adapter

### Introduction
Adapter code to communicate to the external vision gateway system.

The code is meant to be used by Evlos systems that wish to communicate with an external vision gateway service. 

 First, install the latest adapter package via pip. You can find more information [here](https://pypi.org/project/external-vision-gateway-adapter-package/#description).
```
pip install external-vision-gateway-adapter-package
```

The package can then be imported via
```
from external_vision_gateway_adapter.server_client_adapter import ServerClientAdapter
```

### Details
As for the **ServerClientAdapter** class, there are 3 parameters it accepts during initialization.

- **ip**: _string_ - IP address of the gateway service's host. **"0.0.0.0"** by default.
- **port**: _int_ - Port number of the gateway service's host. **5051** y default
- **timeout**: _int_ - The request timeout value in seconds. **2** by default.

The only method that is used by the clients is **send_request** method which expects 3 different parameters when invoked.

- **datetime**: DateTime - Current python's UTC datetime that can be retrieved with datetime.now(timezone=utc).
- **image_bytes_list**: List - The list should contain image bytes. Images are expected to be in RGB.
- **tool_name**: String - The name of the tool/service that you wish to receive response from.

### Example Code

The .py version of this code below can be found in the tests folder.


```
from external_vision_gateway_adapter.server_client_adapter import ServerClientAdapter
from datetime import datetime, timezone

class TestAdapter:

	def __init__(self, ip="0.0.0.0", port=50051, timeout=2):

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
	image_path = ["test.bmp", "test2.bmp"]  # Replace with your image file path
	response = adapter_instance.send_image(image_path, 'ingrind')

	print(response)
```
