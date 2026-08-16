from unittest.mock import Mock, patch
import requests

fake_response = Mock()
fake_response.status_code = 200
fake_response.json.return_value = {
    "message":"这是假的响应"
}

with patch("requests.post") as fake_post:
    fake_post.return_value = fake_response

    response=requests.post("https://example.com")
    print(response.status_code)
    print(response.json())