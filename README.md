***NOT FINISHED***

A "MultiSound File" (MSF) is a binary file which contains multiple "banks" of data. Each bank is split into a track list and a data block.

# msf-handler.py use
Just type `python msf-handler.py` inside of a command line, and the CLI should walk you through everything!

# Format Specifications
*As with all formats, expect this to change! Not by much though...*
## File Signature
Every .MSF starts with the 3 letters "MSF" (0x4D5346), along with 2 bytes after to designate the version of the MSF file.

## Bank Header
Following the file signature is the bank header. Every bank is designated by the `BNK` marker, and can contain, at most, **4.29GB**. Following the `BNK` marker, each bank is defined as:
Bank Name - 3 bytes long. Uses ASCII characters.
Track Definition - 4 bytes long. Defines how each track should be interpreted. Definitions can either be a string, or a number, depending on use case.
Bank length - 4 bytes long. Defines how long the bank is in bytes.

## Track Header
After the bank header is the track header. Each track is designated by the `TRK` marker. Anything data can be defined in the track, so long as it follows what the definition expects.

## Data Block
After the last track in the track header is the data block. The data block is designated with the `DAT` marker. The data block contains all of the data for the bank.

## Defualt Track Definitions
As stated before, track definitions define how the interpreter should read the track header. Although anyone, with enough competence, can make their own track definition, every interpreter must come with and support the following two track definitions:
- MultiSound File Audio (MSFA)
- CD Digital Audio (CDDA)
- MultiSound File Binary (MSFB)

### MultiSound File Audio
Designated by the MSFA track definition, this can be treated as an improved MSF v0 definition. The following table designates how each track should be interpreted:

| Value Name | Length | Description |
| --- | --- | --- |
| Name Length | 1 Byte | Defines how long the name should be in bytes. |
| Name | N Bytes | Defines the name for the track. |
| Flags | 1 Byte | Bit 7 defines if the track is stereo, bit 6 defines if the track is looped, bits 5-4 are reserved, and bits 3-0 define how the data is encoded via a look up table. |
| Samplerate | 3 Bytes | Defines the samplerate of the track in hz. |
| ByteDepth | 1 Byte | Defines the byte depth of the track. Essentially the bit depth, but divided by 8. |
| Offset | 4 Bytes | Offset into the data block in bytes. |
| Size | 4 Bytes | Size of the track in bytes. |
| Loop Start | 4 Bytes | Only exists if the track is looped. Defines when the start of the is loop in samples. |
| Loop End | 4 Bytes | Only exists if the track is looped. Defines when the end of the is loop in samples. |

Encoding look up table:
| Value | Encoding Method |
| --- | --- |
| 0 | Raw PCM. |
| 1 | FLaC encoded. |
| 2 | MP3 encoded. |
| 3 | Vorbis encoded. |
| 4 | AAC encoded. |
| 5-15 | Reserved. |

All audio files will have their header stripped, and therefore, the headers must be reconstructed when extracting files from a MSFA bank.

### CD Digital Audio
TBD

### MultiSound File Binary
TBD
