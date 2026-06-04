import sys
import tomllib
import os
import struct

# Flag Byte:
# SampleRate 0-3 - The sample rate of the audio track. 0 = 44.1khz, 1 = 48, 2 = 22.05, 3 = 11.025, 4 = 32, 5 = 36, 6 = 8, 7 = 96

# Static variables...
HEADER = 0x4D534600
SAMPLE_RATES = {
    0: 44100,
    1: 48000,
    2: 22050,
    3: 11025,
    4: 32000,
    5: 36000,
    6: 8000,
    7: 96000
}

# Strip funcs for each type of file
def StripWav(path):
    with open(path, "rb") as f:
        f.read(12)  # Skip RIFF header
        while True:
            chunk_id = f.read(4)
            chunk_size = struct.unpack("<I", f.read(4))[0]
            if chunk_id == b"data":
                return f.read(chunk_size)
            f.seek(chunk_size, 1)  # Skip chunk
            
# WAV recreation
def WriteWavFromRaw(path, data, sample_rate, bit_depth, stereo):
    Channels = 2 if stereo else 1
    ByteRate = sample_rate * Channels * bit_depth
    BlockAlign = Channels * bit_depth
    DataSize = len(data)
    
    with open(path, "wb") as f:
        # RIFF header
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + DataSize))  # File size - 8
        f.write(b"WAVE")
        
        # fmt chunk
        f.write(b"fmt ")
        f.write(struct.pack("<I", 16))          # Chunk size
        f.write(struct.pack("<H", 1))           # PCM format
        f.write(struct.pack("<H", Channels))
        f.write(struct.pack("<I", sample_rate))
        f.write(struct.pack("<I", ByteRate))
        f.write(struct.pack("<H", BlockAlign))
        f.write(struct.pack("<H", bit_depth * 8))
        
        # data chunk
        f.write(b"data")
        f.write(struct.pack("<I", DataSize))
        f.write(data)

def WriteRaw(path, data):
    with open(path, "wb") as f:
        f.write(data)

# MSF Reader
def GetTracksFromMSF(path):
    if not os.path.isfile(path):
        print(f"{path} is not a valid path...")
        sys.exit(1)

    with open(path, "rb") as f:
        # Verify magic word + version
        Header = struct.unpack(">I", f.read(4))[0]
        if Header != HEADER:
            print("Not a valid MSF file!")
            sys.exit(1)

        Tracks = []
        AudioStart = None

        while True:
            if AudioStart is not None and f.tell() >= AudioStart:
                break

            Length = struct.unpack("B", f.read(1))[0]
            Name = f.read(Length).decode("utf-8")
            Flags = struct.unpack("B", f.read(1))[0]
            BitDepth = struct.unpack("B", f.read(1))[0]
            Offset = struct.unpack(">I", f.read(4))[0]
            Size  = struct.unpack(">I", f.read(4))[0]

            if AudioStart == None:
                AudioStart = Offset
            
            Tracks.append({
                "Name": Name,
                "Flags": Flags,
                "BitDepth": BitDepth,
                "Offset": Offset,
                "Size": Size
            })

        return Tracks
    
# Get Raw Data
def GetRawData(path, offset=0, size=None):
    if not os.path.isfile(path):
        print(f"{path} is not a valid path...")
        sys.exit(1)
    
    with open(path, "rb") as f:
        f.seek(offset)
        if size == None:
            data = f.read()
        else:
            data = f.read(size)
        return data


            
if len(sys.argv) < 2:
    print("Use 'create' to create a new .msf, and 'unpack' to get all of the files from a .msf!")
    sys.exit(1)

if sys.argv[1] == "create":
    if len(sys.argv) < 4:
        print("Usage: msf-handler.py create <file name> <toml definitions>")
        sys.exit(1)

    FileName = sys.argv[2]
    AudioDefines = sys.argv[3]

    if not FileName.endswith(".msf"):
        FileName += ".msf"

    # Track List Opening
    with open(AudioDefines, "rb") as f:
        Config = tomllib.load(f)

    Metadata = []
    Files = []
    TrackBlockLen = 4

    # Creating Track List
    for id, track in Config["track"].items():
        TrackName = track["Name"]
        NameLength = len(TrackName)
        Path = track["File"]

        if NameLength > 255:
            print(f"Track '{id}': name exceeds byte limit (255)...")
            sys.exit(1)

        TrackBlockLen += (NameLength + 11)

        Files.append(Path)

        IsFLAC = 0

        if Path.lower().endswith(".flac"):
            IsFLAC = 1

        Metadata.append({
            "NameLength": NameLength, # Length in Bytes
            "Name": TrackName, # Name
            "SampleRate": track["SampleRate"], # Flags byte, 4 bits
            "Stereo": track["Stereo"], # Flags byte 1 bit
            "Loop": track["Loop"], # Flags byte 1 bit
            "Encoded": IsFLAC, # Flags byte 1 bit
            "BitDepth": track["BitDepth"], # BitDepth (8*BitDepth)
            "Offset": 0x00, # Dummy value, fill in later when all audio files have been put into one data block
            "Size": 0x00 # Dummy value, ^^^^^^^^^^^^
        })

    AudioBlock = bytearray()

    # Stripping all of the headers... fun...
    for i, file in enumerate(Files):
        data = None

        # Error Handling
        if not file.lower().endswith((".flac", ".wav")):
            print(f"Track '{file}': Is not a valid file type...")
            sys.exit(1)

        if not os.path.isfile(file):
            print(f"Track '{file}': Does not exist...")
            sys.exit(1)

        # Get stripped data
        if file.lower().endswith(".wav"):
            data = StripWav(file)
        else:
            data = GetRawData(file)

        # Update Header info
        Metadata[i]["Size"] = len(data)
        Metadata[i]["Offset"] = (len(AudioBlock) + TrackBlockLen)

        # Update Audio Block
        AudioBlock.extend(bytearray(data))

        if len(AudioBlock) > (4294967296 - TrackBlockLen):
            print(f"Data exceeds ~4GB max...")
            sys.exit(1)

    # Write to file
    with open(FileName, "wb") as f:
        # Magic word + version
        f.write(struct.pack(">I", HEADER))

        # Format header
        for track in Metadata:
            f.write(struct.pack("B", track["NameLength"]))
            f.write(track["Name"].encode("utf-8"))
            flags = (track["Stereo"] << 7) | (track["Loop"] << 6) | (track["Encoded"] << 5) | (track["SampleRate"] & 0x0F)
            f.write(struct.pack("B", flags))
            f.write(struct.pack("B", track["BitDepth"]))
            f.write(struct.pack(">I", track["Offset"]))
            f.write(struct.pack(">I", track["Size"]))

        # Audio block
        f.write(AudioBlock)

    print(f"{FileName} was written!")
elif sys.argv[1] == "unpack":
    if len(sys.argv) < 3:
        print("Usage: msf-handler.py unpack <msf file>")
        sys.exit(1)

    Tracks = GetTracksFromMSF(sys.argv[2])
    TFlags = []

    # Get the Metadata
    for i, track in enumerate(Tracks):
        SRIndex = Tracks[i]["Flags"] & 0x0F
        TFlags.append({
            "Stereo": (Tracks[i]["Flags"] >> 7) & 1,
            "Loop": (Tracks[i]["Flags"] >> 6) & 1,
            "Encoded": (Tracks[i]["Flags"] >> 5) & 1,
            "SampleRate": SAMPLE_RATES.get(SRIndex)
        })

    # Output files
    for i, track in enumerate(Tracks):
        Path = None
        AudioData = None
        BitDepth = Tracks[i]["BitDepth"] * 8
        
        if TFlags[i]["Encoded"] == 0:
            Path = Tracks[i]["Name"] + ".wav"
            AudioData = GetRawData(sys.argv[2], Tracks[i]["Offset"], Tracks[i]["Size"])
            WriteWavFromRaw(Path, AudioData, TFlags[i]["SampleRate"], BitDepth, TFlags[i]["Stereo"])
        else:
            Path = Tracks[i]["Name"] + ".flac"
            AudioData = GetRawData(sys.argv[2], Tracks[i]["Offset"], Tracks[i]["Size"])
            WriteRaw(Path, AudioData)

        print(f"{Path} outputted!")

else:
    print("Use 'create' to create a new .msf, and 'unpack' to get all of the files from a .msf!")
    sys.exit(1)
