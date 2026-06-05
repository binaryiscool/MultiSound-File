import sys
import os
import struct

# V1 of the MSF format.
# Current file spec over view:
# MSF + Version number - same as before. The version number will "overflow" into the next byte if the one before it is equal to 255.
# BNK - BNK marker
# Bank name - always 3 bytes long. Name of the bank
# Track definition - 4 bytes long. Unique string of 4 characters defining how it should be read.
# Bank size - 4 bytes long. Defines the bank length in bytes
# TRK - TRK header. Used to denote a new track. Anything can be inside of a track.
# DAT - Used to denote the data block.
# This will repeat until the end of the file

HEADER = 0x4D5346
VERSION = 0x0001

Ask = None

if len(sys.argv) > 1:
    print("No arguments are needed...")
    sys.exit(1)

def CreateMSF():
    print("To create an MSF file, you must create banks, which contain both individual tracks, along with data.\nSelect one of the options below by inputting its number:")
    UserInput = input("Select an option: ")

print("Welcome to the MSF Handler CLI! With this tool (and some navigation), you'll be able to create, view, and unpack .msf!\nSelect one of the options below by inputting its number: \n [0] Create a new MSF \n [1] View an existing MSF \n [2] Extract an existing MSF \n [3] Exit program")

while True:
    UserInput = input("Select an option: ")
    if UserInput.isdigit() and int(UserInput) <= 3 and int(UserInput) >= 0:
        UserInt = int(UserInput)
        match UserInt:
            case 0:
                CreateMSF()

            case 1:
                print("Preview an existing MSF? uhhhhhh, no.")

            case 2:
                print("Extract an existing MSF? uhhhhhh, no.")
            
            case 3:
                print("bye bye!")
                sys.exit(0)
    else:
        print("Not an option.")
