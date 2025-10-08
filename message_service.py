import os
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

    def text_fits(self, message, image):
        image_size = self.get_pixel_count(image)
        if len(message) * 3 > image_size:
            return False
        return True

    def get_pixel_count(self, image):
        width, height = image.size
        return width * height

    def get_binary_string(self, msg):
        bytes_msg = msg.encode('utf-8')
        bin_list = [bin(b)[2:].zfill(8) for b in bytes_msg]
        binary_msg = ''.join(bin_list)
        return binary_msg

    def get_pixels(self, pixel_count, image):
        pixels = list(image.getdata())[0:pixel_count]
        return pixels

    def get_bitmaps(self, pixels):
        start = 0
        end = 3
        ascii_len = int(len(pixels) / 3)

        for x in range(0, ascii_len):
            bitmap = pixels[start:end]
            yield list(bitmap[0])
            yield list(bitmap[1])
            yield list(bitmap[2])
            start += 3
            end += 3

    def is_even(self, num):
        return num % 2 == 0

    def mod_bitmap(self, bitmap, bstring):
        bitmap = [list(p) for p in bitmap]
        bstring_start = 0
        bstring_end = 8
        substring_start = 0
        substring_end = 3
        end_pixel_list = 0

        for x in range(len(bitmap)):
            p = 0
            if x % 3 == 0:
                substring = bstring[bstring_start:bstring_end]
                bstring_start += 8
                bstring_end += 8
                substring_start = 0
                substring_end = 3 if x < len(bitmap) - 3 else 2

            for y in substring[substring_start:substring_end]:
                if y == "0":
                    if self.is_even(bitmap[x][p]):
                        pass
                    else:
                        bitmap[x][p] = 1 if bitmap[x][p] == 0 else bitmap[x][p] - 1
                else:
                    if not self.is_even(bitmap[x][p]):
                        pass
                    else:
                        bitmap[x][p] = 1 if bitmap[x][p] == 0 else bitmap[x][p] - 1
                p += 1

            if end_pixel_list == 2:
                if x == len(bitmap) - 1:
                    if self.is_even(bitmap[x][2]):
                        bitmap[x][2] = 1 if bitmap[x][2] == 0 else bitmap[x][2] - 1
                else:
                    if not self.is_even(bitmap[x][2]):
                        bitmap[x][2] = 1 if bitmap[x][2] == 0 else bitmap[x][2] - 1
                end_pixel_list = 0
            else:
                end_pixel_list += 1

            substring_end += 3
            substring_start += 3

        return bitmap

    def inject_bitmap(self, bitmap, img):
        width = img.size[0]
        x, y = 0, 0
        for pixel in bitmap:
            img.putpixel((x, y), tuple(pixel))
            if x == width - 1:
                x = 0
                y += 1
            else:
                x += 1
        return img

    def encrypt_message(self, photo, message):
        path = self.find_path(photo)
        image = Image.open(path).convert('RGB')
        if not self.text_fits(message, image):
            if os.path.exists(path):
                os.remove(path)
            raise ValueError("Message is too big for the image.")
        bstring = self.get_binary_string(message)
        pixel_count = len(message) * 3
        pixels = self.get_pixels(pixel_count, image)
        bitmaps = list(self.get_bitmaps(pixels))
        if len(bstring) > len(bitmaps) * 8:
            if os.path.exists(path):
                os.remove(path)
            raise ValueError("Binary string too long for bitmap.")
        new_bitmap = self.mod_bitmap(bitmaps, bstring)
        new_img = self.inject_bitmap(new_bitmap, image)
        base, _ = os.path.splitext(path)
        modified_path = f"{base}_stego.png"
        new_img.save(modified_path, format='PNG')
        encrypted_message = "#############"
        self.repo.save(text=encrypted_message, photo_path=modified_path)
        if os.path.exists(path):
            os.remove(path)

    def decode(self, img):
        pixels = self.get_pixels(self.get_pixel_count(img), img)
        i = 2
        try:
            while i < len(pixels) and self.is_even(pixels[i][2]):
                i += 3
            if i >= len(pixels):
                raise ValueError("No valid termination flag found.")
        except IndexError:
            raise ValueError("Invalid image or corrupted data.")
        bstring = self.translate_pixels(pixels[0:i + 1])
        string = self.translate_from_binary(bstring)
        return string

    def translate_pixels(self, pixels):
        bstring = ""
        for byte in pixels:
            for b in byte:
                bstring += "0" if self.is_even(b) else "1"
        return bstring

    def translate_from_binary(self, bstring):
        string = ""
        for b in range(0, len(bstring) - 8, 9):
            try:
                char_bits = bstring[b:b + 8]
                if len(char_bits) == 8:
                    char = chr(int(char_bits, 2))
                    string += char
            except ValueError:
                break
        return string

    def decrypt_message(self, photo_path):
        try:
            image = Image.open(photo_path).convert('RGB')
            return self.decode(image)
        except Exception as e:
            raise ValueError(f"Failed to decrypt image: {str(e)}")