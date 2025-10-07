import os
import numpy as np
from PIL import Image
class Service:
    def __init__(self, upload_folder, repo):
        self.upload_folder = upload_folder
        self.repo = repo
        os.makedirs(self.upload_folder, exist_ok=True)
class MessageManager(Service):
    def delete_message(self, message):
        if message.photo and os.path.exists(message.photo):
            try:
                os.remove(message.photo)
            except Exception as e:
                raise e
        self.repo.delete(message)

class SteganographyManager(Service):
    def generate_filename(self, photo_file):
        ext = os.path.splitext(photo_file.filename)[1]
        count = len(os.listdir(self.upload_folder)) + 1
        return f"photo{count}{ext}"
    def find_path(self, photo_file):
        filename = self.generate_filename(photo_file)
        path = os.path.join(self.upload_folder, filename)
        photo_file.save(path)

        return path
    def encrypt_message(self, photo, message):
        path = self.find_path(photo)
        self.repo.save(text=message, photo_path=path)
        image = Image.open(path).convert('RGB')
        arr = np.array(image)
        h, w = arr.shape[:2]
        print (f"h: {h}, w: {w}")
        bits_arr = np.unpackbits(arr, axis=2)
        print (f"unpacking bits: {bits_arr.shape}")
        print(f"First 3 channels  [0,0]:{arr[0, 0]}")
        print(f"Bits of this channels: {bits_arr[0, 0]}")

