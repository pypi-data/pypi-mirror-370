import os
import time
import json
import logging

logger = logging.getLogger(__name__)

class ImageUploader:
    def __init__(self, image_client, device_id, image_dir="images"):
        """
        Initialize the ImageUploader.

        Args:
            image_client: The ImageUploadClient instance.
            device_id (str): The unique device ID.
            image_dir (str): Directory containing images to upload.
        """
        self.image_client = image_client
        self.device_id = device_id
        self.image_dir = image_dir

    def check_and_upload_images(self):
        """
        Check the last uploaded image date and upload new images.
        """
        try:
            response = self.image_client.get_last_uploaded_date(device_id=self.device_id)

            # Ensure response is a dictionary
            if not response or not isinstance(response, dict):
                logger.error("🚨 [APP] Invalid response from server.")
                return {"success": False, "message": "Invalid response from server."}

            if not response.get("success"):
                error_message = response.get("message", "Unknown error")
                logger.error(f"⚠️ [APP] Failed to get last uploaded image date: {error_message}")
                return {"success": False, "message": error_message}

            last_uploaded_date = response.get("last_uploaded_date", "1970-01-01T00:00:00")
            # logger.info(f"📸 [APP] Last uploaded date: {last_uploaded_date}")

            self._upload_new_images(last_uploaded_date)
            return response

        except Exception as e:
            logger.error("🚨 [APP] Unexpected error while checking/uploading images.", exc_info=True)
            return {"success": False, "message": str(e)}

    def _upload_new_images(self, last_uploaded_date):
        """
        Upload images newer than the last uploaded date and delete them after successful upload.

        Args:
            last_uploaded_date (str): The last uploaded image date.
        """
        try:
            images_uploaded = 0
            for root, _, files in os.walk(self.image_dir):
                for file in sorted(files):
                    file_path = os.path.join(root, file)
                    file_mod_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(os.path.getmtime(file_path)))

                    if file_mod_time > last_uploaded_date:
                        metadata = json.dumps({"file_name": file})
                        response = self.image_client.upload_image(self.device_id, metadata, file_path)

                        if response and response.get("success"):
                            logger.info(f"✅ [APP] Image '{file}' uploaded successfully: {response.get('message')}")
                            self._delete_file(file_path)
                            images_uploaded += 1
                        else:
                            error_message = response.get("message", "Unknown error")
                            logger.error(f"❌ [APP] Failed to upload image '{file}': {error_message}")
            
            if images_uploaded > 0:
                logger.info(f"📊 [APP] Total images uploaded: {images_uploaded}")

        except Exception as e:
            logger.error("🚨 [APP] Unexpected error during image upload process.", exc_info=True)

    def _delete_file(self, file_path):
        """
        Delete the specified file.

        Args:
            file_path (str): Path to the file to delete.
        """
        try:
            os.remove(file_path)
            logger.info(f"🗑️ [APP] File deleted: {file_path}")
        except Exception as e:
            logger.error(f"⚠️ [APP] Failed to delete file '{file_path}': {e}")
