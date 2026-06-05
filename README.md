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
