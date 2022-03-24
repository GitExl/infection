import hashlib
import struct
from pathlib import Path
from typing import List, Tuple, Dict

import PIL.Image


Post = Tuple[int, bytearray]

S_HEADER = struct.Struct('<HHhh')


class Column:

    def __init__(self):
        self.posts: List[Post] = []

    def get_data(self) -> bytearray:
        data = bytearray()

        for post_offset, post_data in self.posts:
            post_first_pixel = post_data[0] if len(post_data) > 0 else 0
            post_last_pixel = post_data[-1] if len(post_data) > 0 else 0
            post_data = struct.pack('<BBB', post_offset, len(post_data), post_first_pixel) + post_data + bytes([post_last_pixel])

            data.extend(post_data)

        data.append(0xFF)

        return data


class DoomImageResource:

    def __init__(self, width: int, height: int, pixels: bytes, left: int = 0, top: int = 0):
        self.width: int = width
        self.height: int = height
        self.pixels: bytes = pixels

        self.left: int = left
        self.top: int = top

    @staticmethod
    def from_data(data: bytes, name: str, transparent_index=247):
        width, height, left, top = S_HEADER.unpack_from(data)

        # Attempt to detect invalid data.
        if width > 2048 or height > 2048 or top > 2048 or left > 2048:
            raise Exception('Doom image file {} has invalid dimensions or offsets.'.format(name))

        image_data = bytearray([transparent_index] * width * height)

        # Read column offsets.
        offset_struct = struct.Struct('<' + ('I' * width))
        offsets = offset_struct.unpack_from(data[8:8 + (width * 4)])

        # Read columns.
        column_index = 0
        while column_index < width:
            offset = offsets[column_index]

            # Attempt to detect invalid data.
            if offset < 0 or offset > len(data):
                raise Exception('Doom image file {} has invalid column offsets.'.format(name))

            prev_delta = 0
            while True:
                column_top = data[offset]

                # Column end.
                if column_top == 255:
                    break

                # Tall columns are extended.
                if column_top <= prev_delta:
                    column_top += prev_delta
                prev_delta = column_top

                pixel_count = data[offset + 1]
                offset += 3

                for pixel_index in range(0, pixel_count):
                    pixel = data[offset + pixel_index]
                    dest = (pixel_index + column_top) * width + column_index
                    image_data[dest] = pixel

                offset += pixel_count + 1

            column_index += 1

        return DoomImageResource(width, height, image_data, left, top)

    @staticmethod
    def from_file(file_path: Path, transparent_index=247):
        data = file_path.read_bytes()
        return DoomImageResource.from_data(data, str(file_path), transparent_index)

    def generate_data(self, mask=True, transparent_index=247) -> bytes:
        columns: List[Column] = []

        # Go through columns.
        for c in range(0, self.width):
            column: Column = Column()

            post_offset = 0
            post_data = bytearray()

            is_post = False

            # First 254 pixels should use absolute offsets.
            is_first_254 = True

            offset = c
            row_offset = 0

            for r in range(0, self.height):

                # For vanilla-compatible dimensions, use a split at 128 to prevent tiling.
                if self.height < 256:
                    if row_offset == 128:

                        # Finish current post if any.
                        if is_post:
                            column.posts.append((post_offset, post_data))
                            post_data = bytearray()
                            is_post = False

                # Taller images cannot be expressed without tall patch support.
                # If we're at offset 254, create a dummy post for tall doom gfx support.
                elif row_offset == 254:

                    # Finish current post if any.
                    if is_post:
                        column.posts.append((post_offset, post_data))
                        post_data = bytearray()

                    # Begin relative offsets.
                    is_first_254 = False

                    # Create dummy post.
                    post_offset = 254
                    column.posts.append((post_offset, post_data))
                    post_data = bytearray()

                    # Clear post.
                    row_offset = 0
                    is_post = False

                # If the current pixel is not transparent, add it to the current post.
                if not mask or self.pixels[offset] != transparent_index:

                    # If we're not currently building a post, begin one and set its offset.
                    if not is_post:

                        # Set offset.
                        post_offset = row_offset

                        # Reset offset if we're in relative offset mode.
                        if not is_first_254:
                            row_offset = 0

                        # Start post.
                        is_post = True

                    # Add the pixel to the post.
                    post_data.append(self.pixels[offset])

                elif is_post:

                    # If the current pixel is transparent, and we are currently building
                    # a post, add the current post to the list and clear it.
                    column.posts.append((post_offset, post_data))
                    post_data = bytearray()
                    is_post = False

                # Go to next row.
                offset += self.width
                row_offset += 1

            # If the column ended with a post, add it.
            if is_post:
                column.posts.append((post_offset, post_data))

            # Add the column data.
            columns.append(column)

            # Go to next column.
            offset += 1

        column_offset_by_hash: Dict[str, int] = {}
        column_offsets: List[int] = []
        data = bytearray()
        offset = 8 + len(columns) * 4

        for column in columns:
            column_data = column.get_data()
            column_hash = hashlib.sha256(column_data).hexdigest()

            # Reuse data from existing column or write new column data.
            if column_hash in column_offset_by_hash:
                column_offset = column_offset_by_hash[column_hash]
            else:
                column_offset = offset
                column_offset_by_hash[column_hash] = offset
                data.extend(column_data)
                offset += len(column_data)

            column_offsets.append(column_offset)

        header = struct.pack('<HHhh', self.width, self.height, self.left, self.top)
        column_offset_data = struct.pack('<' + ('I' * len(column_offsets)), *column_offsets)

        return header + column_offset_data + data

    @staticmethod
    def from_image(image: PIL.Image.Image):
        return DoomImageResource(image.width, image.height, bytes(image.getdata()))
