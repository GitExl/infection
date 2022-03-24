import hashlib
import struct


# WAD header struct
# ID            4       ASCII "IWAD" or "PWAD"
# Lump count    int     Number of lump entries
# Size          int     Offset of lump directory
WAD_HEADER = struct.Struct('4sII')

# WAD lump struct
# Offset    int Lump offset in file
# Size      int Lump size
# Name      8   Name of lump in ASCII
WAD_LUMP = struct.Struct('II8s')

# Translation table for lump names.
# Lump names containing [, ] and \ can appear, but cannot be saved to disk
# because their filename would be illegal. These characters are mapped to legal ones internally.
LUMP_MAP_WAD = '[\\]'
LUMP_MAP_INT = '$@#'
LUMP_TRANS_TO_WAD = str.maketrans(LUMP_MAP_INT, LUMP_MAP_WAD)
LUMP_TRANS_TO_INT = str.maketrans(LUMP_MAP_WAD, LUMP_MAP_INT)


class WADLump:
    """
    WAD lump (directory entry)

    A file inside a WAD file.
    """

    def __init__(self, name, size, offset, file_obj, wad):
        self.name = name
        self.size = size
        self.offset = offset

        self.file_obj = file_obj
        self.data = None
        self.wad = wad
        self.has = None

        self.index = -1

        self.resource = None

    def __str__(self):
        return '{:8}  size = {:9}  offset = {:9}'.format(self.name, self.size, self.offset)


class WADBase:
    """
    WAD file base

    Contains a list of lumps (files).
    Note that lump names are not required to be unique, so no dictionary is used.

    sid indicates the type of WAD file. IWAD for Internal WAD files (doom/doom2/heretic/etc.wad), PWAD for Patch WAD
    files (addons). list_offset points to the offset inside the WAD file of the lump list, which is placed after the
    header and all lump data.
    """

    def __init__(self):
        self.sid = ''
        self.path = ''

        self.list_offset = 0
        self.lumps = None

        self.file_obj = None

        self.opened = False

    def __str__(self):
        return '{:4}  lump count = {:5}  {}'.format(self.sid, len(self.lumps), self.__class__)


class WADWriter(WADBase):
    """WAD file reader."""

    def __enter__(self):
        self.file_obj = open(self.path, 'wb')
        self.opened = True

        self.list_offset = WAD_HEADER.size
        self.lumps = []
        self.lumps_by_hash = {}

        return self

    def __init__(self, filename, sid):
        super().__init__()

        if not (sid == 'PWAD' or sid == 'IWAD'):
            raise Exception('{} is not a valid WAD id.'.format(sid))

        self.path = filename
        self.sid = sid

        self.__enter__()

    def __exit__(self, *args):
        self.close()

    def add_lump(self, name, data):
        """Add a new lump to the list."""

        if len(name) > 8:
            raise Exception('Lump name is too long.')

        lump = WADLump(name.upper(), len(data), -1, self.file_obj, self)
        lump.data = data
        lump.hash = hashlib.sha256(data).hexdigest()
        lump.index = len(self.lumps)

        self.lumps_by_hash[lump.hash] = lump
        self.lumps.append(lump)

    def write(self):

        # Write temporary header.
        self.file_obj.seek(0)
        self.file_obj.write(WAD_HEADER.pack(bytearray(self.sid, 'ascii'), len(self.lumps), self.list_offset))

        # Write lump data.
        for lump in self.lumps:
            dup_lump = self.lumps_by_hash.get(lump.hash)
            if dup_lump is None:
                raise Exception('Lump hash not found for "{}".'.format(lump.name))

            # Use existing lump data if it is identical.
            if dup_lump.offset == -1:
                dup_lump.offset = self.file_obj.tell()
                lump.offset = self.file_obj.tell()
                self.file_obj.write(lump.data)
            else:
                lump.offset = dup_lump.offset

        # Write lump index list.
        self.list_offset = self.file_obj.tell()
        for lump in self.lumps:
            lump_name = lump.name.translate(LUMP_TRANS_TO_WAD)
            self.file_obj.write(WAD_LUMP.pack(lump.offset, lump.size, bytearray(lump_name, 'ASCII')))

        # Rewrite header with correct list offset.
        self.file_obj.seek(0)
        self.file_obj.write(WAD_HEADER.pack(bytearray(self.sid, 'ascii'), len(self.lumps), self.list_offset))

    def close(self):
        """Close the WAD file."""

        self.file_obj.close()
        self.opened = False


class WADReader(WADBase):
    """WAD file reader."""

    def __enter__(self):
        self.file_obj = open(self.path, 'rb')
        self.opened = True

        # Read header
        self.sid, lump_count, self.list_offset = WAD_HEADER.unpack(self.file_obj.read(WAD_HEADER.size))

        # Check if this is really a WAD file
        if not self.sid == b'IWAD' and not self.sid == b'PWAD':
            raise Exception('Not a valid WAD file.')

        # Read lumps
        self.file_obj.seek(self.list_offset)
        self.lumps = []

        for idx in range(lump_count):
            offset, size, name = WAD_LUMP.unpack(self.file_obj.read(WAD_LUMP.size))

            # End at NULL char and translate to valid filename
            name = name.decode('ascii').rstrip('\x00')
            name = name.translate(LUMP_TRANS_TO_INT)

            lump = WADLump(name, size, offset, self.file_obj, self)
            lump.index = idx

            self.lumps.append(lump)
            self.lump_indices[name] = idx

        # Read lump data
        for lump in self.lumps:
            self.file_obj.seek(lump.offset)
            lump.data = self.file_obj.read(lump.size)

        return self

    def __init__(self, filename):
        super().__init__()

        self.path = filename
        self.lump_indices = {}
        self.iter_index = 0
        self.__enter__()

    def __exit__(self, *args):
        self.close()

    def __next__(self):
        self.iter_index += 1

        if self.iter_index > len(self.lumps):
            raise StopIteration

        return self.lumps[self.iter_index - 1]

    def __iter__(self):
        self.iter_index = 0
        return self

    def lump_index(self, name):
        """Return a lump's index from a lump name."""

        if name in self.lump_indices:
            return self.lump_indices[name]

        return -1

    def close(self):
        """Close the WAD file."""

        self.file_obj.close()
        self.opened = False

        self.sid = ''
        self.path = ''
        self.list_offset = 0
        self.lumps = None
        self.file_obj = None
        self.iter_index = 0
        self.lump_indices = None
