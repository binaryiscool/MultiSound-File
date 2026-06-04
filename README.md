A "MultiSound File" (MSF) is a binary file which contains multiple audio tracks inside of it, either raw or encoded via flac.

# TOML Specifications
To generate a .msf file with the python file included, you must provide a .toml file, so that the program can assign the right meta . Each track must be defined as:
<br>\[tracks.TRACKNAME]\
File = "PATH-TO-FILE"
<br>Name = "TRACK NAME"
<br>SampleRate = 0 # See [here](#data) for the look up table used to determine the samplerate
<br>Stereo = 1 # 1 = Stereo, 0 = Mono
<br>Loop = 0 # 0 = No looping, 1 = looped
<br>BitDepth = 2 # How many bytes each sample should take up

replace each parameter for the correct value for each track, and you should be able to generate your .MSF file! Remember you can have multiple tracks per file.

# Format Specifications
*As with all formats, expect this to change! Not by much though...*
## File Signature
Every .MSF starts with the 3 letters "MSF" (0x4D5346), along with a byte after to designate the version of the MSF file.

## Track Header
Following the file signature is the track header. Each track is defined as:
Name Length - Always takes up 1 byte, defines the length of the name in bytes.
Name - Of arbitrary length. Due to the fact Name Length is always 1 byte long.
Flags & Samplerate - 1 Byte long. Bit 7 defines if the track is stereophonic or not, bit 6 defines if the track is looped, bit 5 defines if the audio is encoded (always encoded with FLaC), bit 4 is reserved, and bits 3-0 define the samplerate (from a look up table).
Bit Depth - 1 Byte long. Defines the bit depth as how many bytes each sample should take up.
Offset - 4 Bytes long. Defines the byte offset into the file.
Size - 4 Bytes long, defines the size (in bytes) of the track.

### Notes
* Since "Name Length" is always a byte long, "Name" has a maximum length of 255.
* Since "Offset" and "Size" are 4 bytes long, the maximum size any .msf file can be is ~4.29GB.

Look up table used for the Samplerate:

| Value | Samplerate (hz) |
| --- | --- |
| 0 | 44.1khz |
| 1 | 48khz |
| 2 | 22.05khz |
| 3 | 11.025khz |
| 4 | 32khz |
| 5 | 36khz |
| 6 | 8khz |
| 7 | 96khz |
| 8-15 | Reserved |

## Data
After the track header comes the data of all of the tracks. All audio data comes after the track header ends. Each track is placed in sequential order (although they do not have to be) in relation to the track header. While WAV files have their header stripped, FLaCs do not.
