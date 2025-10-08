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
        photo_path = getattr(message, "photo", None)
        try:
            if os.path.exists(photo_path):
                os.remove(photo_path)
        except Exception as e:
            raise e
        finally:
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

    def message_into_bits(self, message):
        bytes_message = message.encode('utf-8')
        message_len = len(bytes_message)
        header = message_len.to_bytes(4, byteorder='little')
        payload = header + bytes_message
        bits = []
        for b in payload:
            for i in range(7, -1, -1):
                bits.append((b >> 1) & 1)
        return bits

    def recreate_photo (self, bits, path):
        base, _ = os.path.splitext(path)
        arr_modified = np.packbits(bits, axis=2)
        image_modified = Image.fromarray(arr_modified, mode='RGB')
        modified_path = f"{base}_stego.png"
        image_modified.save(modified_path)
        return modified_path

    def encrypt_message(self, photo, message):
        path = self.find_path(photo)
        image = Image.open(path).convert('RGB')
        arr = np.array(image)
        bits = self.message_into_bits(message)
        bits_arr = np.unpackbits(arr, axis=2)
        flat_bits = bits_arr.flatten()
        if len(bits) > flat_bits.size:
            if os.path.exists(path):
                os.remove(path)
            raise ValueError("Message is too big.")
        for i, bit in enumerate(bits):
            flat_bits[i] = (flat_bits[i] & 0xFE) | bit
        bits_arr_modified = flat_bits.reshape(bits_arr.shape)
        modified_path = self.recreate_photo(bits_arr_modified, path)
        encrypted_message = "#############"
        self.repo.save(text=encrypted_message, photo_path=modified_path)
        if os.path.exists(path):
            os.remove(path)



