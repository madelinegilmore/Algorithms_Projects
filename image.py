class Pixel:
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    def get_r(self):
        return self.r

    def get_g(self):
        return self.g

    def get_b(self):
        return self.b

# Generated in part by genAI
class Image:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pixels = [[Pixel(0, 0, 0) for _ in range(width)] for _ in range(height)]

    def set_pixel(self, r, c, pixel):
        if 0 <= c < self.width and 0 <= r < self.height:
            self.pixels[r][c] = pixel

    def get_pixel(self, r, c):
        if 0 <= c < self.width and 0 <= r < self.height:
            return self.pixels[r][c]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def save_bmp(self, filename):
        with open(filename, 'wb') as f:
            # BMP header
            f.write(b'BM')  # Signature
            file_size = 54 + self.width * self.height * 3
            f.write(file_size.to_bytes(4, 'little'))  # File size
            f.write(b'\x00\x00')  # Reserved
            f.write(b'\x00\x00')  # Reserved
            f.write((54).to_bytes(4, 'little'))  # Offset to pixel data
            
            # DIB header
            f.write((40).to_bytes(4, 'little'))  # DIB header size
            f.write(self.width.to_bytes(4, 'little'))  # Width
            f.write(self.height.to_bytes(4, 'little'))  # Height
            f.write(b'\x01\x00')  # Color planes
            f.write(b'\x18\x00')  # Bits per pixel
            f.write(b'\x00\x00\x00\x00')  # Compression
            f.write((self.width * self.height * 3).to_bytes(4, 'little'))  # Image size
            f.write(b'\x13\x0B\x00\x00')  # X pixels per meter
            f.write(b'\x13\x0B\x00\x00')  # Y pixels per meter
            f.write(b'\x00\x00\x00\x00')  # Total colors
            f.write(b'\x00\x00\x00\x00')  # Important colors
            
            # Pixel data (bottom-up)
            for r in range(self.height - 1, -1, -1):  # BMP format is bottom-up
                for c in range(self.width):
                    pixel = self.get_pixel(r, c)
                    f.write(bytes([pixel.b, pixel.g, pixel.r]))  # Write in BGR format

    def read_bmp(filename):
        with open(filename, 'rb') as f:
            # Read BMP header (54 bytes)
            f.read(18)  # Skip the first 18 bytes to get to width and height
            width = int.from_bytes(f.read(4), 'little')
            height = int.from_bytes(f.read(4), 'little')
            
            # Skip to pixel array (offset is usually at 54 bytes)
            f.read(28)  # Skip more header info

            image = Image(width, height)

            # Read pixel data
            for row in range(height):
                for col in range(width):
                    # BMP stores pixels in BGR format, each pixel is 3 bytes
                    b = ord(f.read(1))
                    g = ord(f.read(1))
                    r = ord(f.read(1))
                    pixel = Pixel(r, g, b)
                    image.set_pixel(height - 1 - row, col, pixel)  # Flip y-axis

            return image