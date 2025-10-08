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
        bin_list = [bin(ord(x))[2:].zfill(8) for x in msg]
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
        if num % 2 == 0:
            return True
        else:
            return False

    def mod_bitmap(self, bitmap, bstring):
        bitmap = [list(p) for p in bitmap]

        bstring_start = 0
        bstring_end = 8
        substring_start = 0
        substring_end = 3
        end_pixel_list = 0

        for x in range(0, len(bitmap)):
            p = 0

            if x % 3 == 0:
                substring = bstring[bstring_start:bstring_end]
                bstring_start += 8
                bstring_end += 8
                substring_start = 0
                substring_end = 3

            for y in substring[substring_start:substring_end]:
                if y == "0":
                    if self.is_even(bitmap[x][p]):
                        pass
                    else:
                        if bitmap[x][p] == 0:
                            bitmap[x][p] += 1
                        else:
                            bitmap[x][p] -= 1
                else:
                    if self.is_even(bitmap[x][p]):
                        if bitmap[x][p] == 0:
                            bitmap[x][p] += 1
                        else:
                            bitmap[x][p] -= 1
                    else:
                        pass
                p += 1

            if end_pixel_list == 2:
                if x == len(bitmap) - 1:
                    if self.is_even(bitmap[x][2]):
                        if bitmap[x][2] == 0:
                            bitmap[x][2] += 1
                        else:
                            bitmap[x][2] -= 1
                else:
                    if not self.is_even(bitmap[x][2]):
                        if bitmap[x][2] == 0:
                            bitmap[x][2] += 1
                        else:
                            bitmap[x][2] -= 1
                end_pixel_list = 0
            else:
                end_pixel_list += 1

            substring_end += 3
            substring_start += 3

        return bitmap

    def inject_bitmap(self, bitmap, img):
        width = img.size[0]
        (x, y) = (0, 0)
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
            raise ValueError("Message is too big.")
        bstring = self.get_binary_string(message)
        pixel_count = len(message) * 3
        pixels = self.get_pixels(pixel_count, image)
        bitmaps = list(self.get_bitmaps(pixels))
        new_bitmap = self.mod_bitmap(bitmaps, bstring)
        new_img = self.inject_bitmap(new_bitmap, image)
        base, _ = os.path.splitext(path)
        modified_path = f"{base}_stego.png"
        new_img.save(modified_path)
        encrypted_message = "#############"
        self.repo.save(text=encrypted_message, photo_path=modified_path)
        if os.path.exists(path):
            os.remove(path)

    def decode(self, img):
        pixels = self.get_pixels(self.get_pixel_count(img), img)
        if self.is_even(pixels[2][2]):
            i = 2
            while self.is_even(pixels[i][2]):
                i += 3
        else:
            i = 2
        bstring = self.translate_pixels(pixels[0:i + 1])
        string = self.translate_from_binary(bstring)
        return string

    def translate_pixels(self, pixels):
        bstring = ""
        for byte in pixels:
            for b in byte:
                if int(b) % 2 == 0:
                    bstring += "0"
                else:
                    bstring += "1"
        return bstring

    def translate_from_binary(self, bstring):
        string = ""
        for b in range(0, len(bstring), 9):
            st = chr(int(bstring[b:b + 8], 2))
            string += st
        return string

    def decrypt_message(self, photo_path):
        image = Image.open(photo_path).convert('RGB')
        return self.decode(image)