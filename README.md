# Steganography Web Application

This project is a Flask-based web application that implements steganography, a technique for hiding text messages within images using the Least Significant Bit (LSB) method. The application allows users to upload an image and a text message, encode the message into the image, and later decode the hidden message from the encoded image. The encoded images are saved in PNG format to ensure lossless storage, and a repository is used to manage message metadata.

The core functionality is provided by the SteganographyManager class, which handles encoding and decoding, and the MessageManager class, which manages file and database operations. The application is designed to be simple, secure, and user-friendly, with a focus on minimal visual changes to the image during encoding.




## Installation

1. Clone the repository:

```bash
    git clone https://github.com/namur1408/Steganography-Web-Application.git
    cd Steganography-Web-Application
```
2. Install dependencies:
```bash
  pip install -r requirements.txt
``` 
3. Set Up the Upload Folder:
Create a directory named static/photo in the project root to store uploaded and encoded images.

4. Open your browser and go to the link that was given to you
## How it works
Steganography is a way to hide secret information inside normal-looking files usually pictures. The main idea is that you can slightly change the pixels of an image in a way that the human eye can’t notice, but a computer can still read those small changes and recover the hidden message.

Every image is made of pixels, and each pixel has three color values: red (R), green (G), and blue (B).

For example, a few pixels from an image might look like this:
```css
[(120, 64, 200), (121, 63, 199), (122, 65, 201)]
```
Now, let’s say we want to hide the word “Hi” inside the image.
First, every letter is turned into binary — a code made of 1s and 0s.

The word “Hi” in binary looks like this:
```css
H → 01001000
i → 01101001
```
Each bit (0 or 1) will change one of the color values in the pixels.
The rule is simple:

If the bit is 0, make the color value even.

If the bit is 1, make the color value odd.

For example, if one pixel looks like this:
```css
(120, 64, 200)
```
and the next three bits we want to hide are 0, 1, 0,
we would make it look like this:
```css
(120, 65, 200)
```
After repeating this process for all the bits, the image now secretly contains the binary code for “Hi”.
To anyone looking at it, it’s the same image but a program that knows the rules can extract the message.

Decoding
To read the hidden text, we go backward:

- Even numbers mean 0

- Odd numbers mean 1

By collecting these bits in groups of 8, we can rebuild the binary data and translate it back into text.
When a special marker is found (for example, a certain pixel value), it means the message has ended.



## Features

- Encode Messages: Hide a text message in an image by modifying the LSBs of pixel RGB values

- Decode Messages: Extract hidden messages from encoded images

- File Management: Upload images to a designated folder and delete them when no longer needed

- Database Integration: Store metadata (e.g., image paths) using a repository

- Error Handling: Validate image size, message length, and file format to prevent errors

- UTF-8 Support: Handle non-ASCII characters in messages using UTF-8 encoding


##  Project Structure
```text
steganography-web-app/
├── static/
│   └── photo/           
├── templates/
│   ├── index.html       # Main page for uploading image and message
│   ├── decrypted.html   # Page to display decoded message
│   ├── encrypted.html   # Page to display encoding result
│   └── view.html
├── db_config.py 
├── forms.py
├── message_repository.py
├── message_service.py   # Core steganography and message management logic
├── app.py                
├── models.py 
├── routes.py           
└── README.md            
```

## Technologies Used

- Python 3.13

- Flask

- SQLAlchemy

- Jinja2

- pillow


## Notes

- This is an educational project do not try to hide here something important, the LSB method is simple and not highly secure; it can be detected with steganalysis tools.

- Message Size: The message must fit within the image (3 pixels per character). Large messages require larger images.
