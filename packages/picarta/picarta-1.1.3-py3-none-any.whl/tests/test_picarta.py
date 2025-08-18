import unittest
from picarta import Picarta


class TestPicarta(unittest.TestCase):
    def setUp(self):
        self.api_token = "YOUR API TOKEN"
        self.localizer = Picarta(self.api_token)

    def test_is_valid_url(self):
        self.assertTrue(self.localizer.is_valid_url("https://upload.wikimedia.org/wikipedia/commons/8/83/San_Gimignano_03.jpg"))
        self.assertFalse(self.localizer.is_valid_url("not_a_url"))

    def test_localize_image_url(self):
        result = self.localizer.localize(
            "https://upload.wikimedia.org/wikipedia/commons/8/83/San_Gimignano_03.jpg"
        )
        self.assertIsNotNone(result)

    def test_localize_image_local(self):
        result = self.localizer.localize("tests/images/roma.jpg")
        self.assertIsNotNone(result)

    def test_localize_image_local(self):
        result = self.localizer.localize(
            aerial_image=True,
            img_path="tests/images/43.470191_11.728145.jpg",
            country_code='IT',
            center_latitude=43.470191, 
            center_longitude=11.721814,
            radius=1,
            camera_altitude=300
        )

        self.assertIsNotNone(result)

        # Ensure result is a tuple
        assert isinstance(result, tuple), f"Expected tuple, got {type(result)}"

        # Unpack the tuple
        json_response, kml_file = result  

        # Check if 'bbox' exists in json_response
        assert 'bbox' in json_response, "Key 'bbox' not found in response"


if __name__ == "__main__":
    unittest.main()
