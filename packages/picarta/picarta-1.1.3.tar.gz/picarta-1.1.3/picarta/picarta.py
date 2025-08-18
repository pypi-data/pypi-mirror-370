import json
import simplekml
import requests
import base64

from PIL import Image
import io

from urllib.parse import urlparse


class Picarta:
    def __init__(self, api_token, url="https://picarta.ai/classify", top_k=10):
        self.api_token = api_token
        self.url = url
        self.top_k = top_k
        self.headers = {"Content-Type": "application/json"}

    def is_valid_url(self, input_str):
        try:
            result = urlparse(input_str)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def read_image(self, image_path, max_size=(1024, 1024)):

        with Image.open(image_path) as img:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            buffer = io.BytesIO()
            img.save(buffer, format="JPEG")  
            buffer.seek(0)

            return base64.b64encode(buffer.read()).decode("utf-8")
        
    def _create_kml(self, gps_bbox):
        """Generate a KML file from the bounding box coordinates."""
        if not gps_bbox or "bbox" not in gps_bbox:
            raise ValueError("Invalid bbox format in the response.")

        bbox = gps_bbox["bbox"]
        coordinates = [
            (bbox["top_left"]["lon"], bbox["top_left"]["lat"]),
            (bbox["top_right"]["lon"], bbox["top_right"]["lat"]),
            (bbox["bottom_right"]["lon"], bbox["bottom_right"]["lat"]),
            (bbox["bottom_left"]["lon"], bbox["bottom_left"]["lat"]),
            (bbox["top_left"]["lon"], bbox["top_left"]["lat"]),  # Closing the loop
        ]

        # Create KML file
        kml = simplekml.Kml()

        polygon = kml.newpolygon(name="Bounding Box", outerboundaryis=coordinates)
        polygon.style.polystyle.color = "40FFFFFF"  # 25% opacity, white
        polygon.style.polystyle.fill = True
        polygon.style.linestyle.color = "FFFFFFFF"  # White outline
        polygon.style.linestyle.width = 2

        # Add center point
        center = gps_bbox.get("center", {})
        if center:
            kml.newpoint(name="Center", coords=[(center["lon"], center["lat"])])

        # Add markers at the corners
        corner_names = ["Top Left", "Top Right", "Bottom Right", "Bottom Left"]
        for name, coord in zip(
            corner_names, coordinates[:-1]
        ):  # Exclude last duplicate point
            kml.newpoint(name=name, coords=[coord])

        return kml

    def localize(
        self,
        img_path,
        top_k=None,
        country_code=None,
        center_latitude=None,
        center_longitude=None,
        radius=None,
        aerial_image=False,
        camera_altitude=None,
    ):
        if self.is_valid_url(img_path):
            image_data = img_path
        else:
            image_data = self.read_image(img_path)

        payload = {
            "TOKEN": self.api_token,
            "AERIAL_IMAGE": aerial_image,
            "IMAGE": image_data,
            "COUNTRY_CODE": country_code,
            "Center_LATITUDE": center_latitude,
            "Center_LONGITUDE": center_longitude,
            "RADIUS": radius,
        }

        if aerial_image:
            payload["CAMERA_ALTITUDE"] = camera_altitude
        else:
            payload["TOP_K"] = top_k if top_k is not None else self.top_k

        response = requests.post(self.url, headers=self.headers, json=payload, timeout=300)


        if response.status_code == 200:
            json_response = response.json()

            if not aerial_image:
                return json.dumps(json_response, indent=2)
            else:
                if 'bbox' in json_response:
                    kml_file = self._create_kml(json_response)
                else:
                    kml_file = None
                return json.dumps(json_response, indent=2), kml_file
        else:
            try:
                error_message = response.json()  # Try to parse the error message
            except ValueError:
                error_message = response.text  # Fallback to raw text if JSON parsing fails

            print(f"API Error {response.status_code}: {error_message}")  # Print error details
            response.raise_for_status()  # Raise an exception to propagate the error