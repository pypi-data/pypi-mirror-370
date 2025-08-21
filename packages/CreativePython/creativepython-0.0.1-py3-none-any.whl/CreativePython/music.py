#######################################################################################
# music.py       Version 1.0     03-Apr-2025
# Trevor Ritchie, Taj Ballinger, Drew Smuniewski, and Bill Manaris
#
#######################################################################################
#
# This file is part of CreativePython.
#
# [LICENSING GOES HERE]
#
#######################################################################################
#
# REVISIONS:
#
#
# TODO:
#  -
#
#######################################################################################

############### IMPORTS ###############################################################
# C++ documentation: https://github.com/schellingb/TinySoundFont
# Python bindings: https://pypi.org/project/tinysoundfont/
import tinysoundfont  # C++ library for MIDI synthesis

from timer import Timer     # scheduling audio events and playback timing
import atexit               # registering cleanup functions to run on program exit
import math                 # mathematical operations like frequency calculations
import os                   # file path and system operations
import random               # generating random numbers and musical elements
from AudioSample import *   # audio sample playback and manipulation
import mido                 # midi operations for Read and Write classes

#######################################################################################
# Constants
#######################################################################################

# define scales as lists of pitch offsets (from the root)
AEOLIAN_SCALE        = [0, 2, 3, 5, 7, 8, 10]
BLUES_SCALE          = [0, 2, 3, 4, 5, 7, 9, 10, 11]
CHROMATIC_SCALE      = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
DIATONIC_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
DORIAN_SCALE         = [0, 2, 3, 5, 7, 9, 10]
HARMONIC_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 11]
LYDIAN_SCALE         = [0, 2, 4, 6, 7, 9, 11]
MAJOR_SCALE          = [0, 2, 4, 5, 7, 9, 11]
MELODIC_MINOR_SCALE  = [0, 2, 3, 5, 7, 8, 9, 10, 11]
MINOR_SCALE          = [0, 2, 3, 5, 7, 8, 10]
MIXOLYDIAN_SCALE     = [0, 2, 4, 5, 7, 9, 10]
NATURAL_MINOR_SCALE  = [0, 2, 3, 5, 7, 8, 10]
PENTATONIC_SCALE     = [0, 2, 4, 7, 9]

######################################################################################
# define text labels for MIDI instruments (index in list is same as MIDI instrument number)
MIDI_INSTRUMENTS = [ # Piano Family
                    "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano",
                    "Honky-tonk Piano", "Electric Piano 1 (Rhodes)", "Electric Piano 2 (DX)",
                    "Harpsichord", "Clavinet",

                    # Chromatic Percussion Family
                    "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba",
                    "Xylophone", "Tubular Bells", "Dulcimer",

                    # Organ Family
                    "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ",
                    "Reed Organ", "Accordion", "Harmonica", "Tango Accordion",

                    # Guitar Family
                    "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)",
                    "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar",
                    "Distortion Guitar", "Guitar harmonics",

                    # Bass Family
                    "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass",
                    "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",

                    # Strings and Timpani Family
                    "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings",
                    "Orchestral Harp", "Timpani",

                    # Ensemble Family
                    "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2",
                    "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",

                    # Brass Family
                    "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn",
                    "Brass Section", "SynthBrass 1", "SynthBrass 2",

                    # Reed Family
                    "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn",
                    "Bassoon", "Clarinet",

                    # Pipe Family
                    "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi",
                    "Whistle", "Ocarina",

                    # Synth Lead Family
                    "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)",  "Lead 4 (chiff)",
                    "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)",

                    # Synth Pad Family
                    "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)",
                    "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)",

                    # Synth Effects Family
                    "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)",
                    "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",

                    # Ethnic Family
                    "Sitar",  "Banjo", "Shamisen", "Koto", "Kalimba", "Bag pipe", "Fiddle", "Shanai",

                    # Percussive Family
                    "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom",
                    "Synth Drum", "Reverse Cymbal",

                    # Sound Effects Family
                    "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring",
                    "Helicopter", "Applause", "Gunshot" ]

# define text labels for inverse-lookup of MIDI pitches (index in list is same as MIDI pitch number)
# (for enharmonic notes, e.g., FS4 and GF4, uses the sharp version, e.g. FS4)
MIDI_PITCHES = ["C_1", "CS_1", "D_1", "DS_1", "E_1", "F_1", "FS_1", "G_1", "GS_1", "A_1", "AS_1", "B_1",
                "C0", "CS0", "D0", "DS0", "E0", "F0", "FS0", "G0", "GS0", "A0", "AS0", "B0",
                "C1", "CS1", "D1", "DS1", "E1", "F1", "FS1", "G1", "GS1", "A1", "AS1", "B1",
                "C2", "CS2", "D2", "DS2", "E2", "F2", "FS2", "G2", "GS2", "A2", "AS2", "B2",
                "C3", "CS3", "D3", "DS3", "E3", "F3", "FS3", "G3", "GS3", "A3", "AS3", "B3",
                "C4", "CS4", "D4", "DS4", "E4", "F4", "FS4", "G4", "GS4", "A4", "AS4", "B4",
                "C5", "CS5", "D5", "DS5", "E5", "F5", "FS5", "G5", "GS5", "A5", "AS5", "B5",
                "C6", "CS6", "D6", "DS6", "E6", "F6", "FS6", "G6", "GS6", "A6", "AS6", "B6",
                "C7", "CS7", "D7", "DS7", "E7", "F7", "FS7", "G7", "GS7", "A7", "AS7", "B7",
                "C8", "CS8", "D8", "DS8", "E8", "F8", "FS8", "G8", "GS8", "A8", "AS8", "B8",
                "C9", "CS9", "D9", "DS9", "E9", "F9", "FS9", "G9"]

#######################################################################################
# MIDI rhythm/duration constants

DWN  = DOTTED_WHOLE_NOTE          = 4.5
WN   = WHOLE_NOTE                 = 4.0
DHN  = DOTTED_HALF_NOTE           = 3.0
DDHN = DOUBLE_DOTTED_HALF_NOTE    = 3.5
HN   = HALF_NOTE                  = 2.0
HNT  = HALF_NOTE_TRIPLET          = 4.0/3.0
QN   = QUARTER_NOTE               = 1.0
QNT  = QUARTER_NOTE_TRIPLET       = 2.0/3.0
DQN  = DOTTED_QUARTER_NOTE        = 1.5
DDQN = DOUBLE_DOTTED_QUARTER_NOTE = 1.75
EN   = EIGHTH_NOTE                = 0.5
DEN  = DOTTED_EIGHTH_NOTE         = 0.75
ENT  = EIGHTH_NOTE_TRIPLET        = 1.0/3.0
DDEN = DOUBLE_DOTTED_EIGHTH_NOTE  = 0.875
SN   = SIXTEENTH_NOTE             = 0.25
DSN  = DOTTED_SIXTEENTH_NOTE      = 0.375
SNT  = SIXTEENTH_NOTE_TRIPLET     = 1.0/6.0
TN   = THIRTYSECOND_NOTE          = 0.125
TNT  = THIRTYSECOND_NOTE_TRIPLET  = 1.0/12.0

######################################################################################
# MIDI pitch constants (for first octave, i.e., minus 1 octave)
C_1  = c_1                = 0
CS_1 = cs_1 = DF_1 = df_1 = 1
D_1  = d_1                = 2
EF_1 = ef_1 = DS_1 = ds_1 = 3
E_1  = e_1  = FF_1 = ff_1 = 4
F_1  = f_1  = ES_1 = es_1 = 5
FS_1 = fs_1 = GF_1 = gf_1 = 6
G_1  = g_1                = 7
AF_1 = af_1 = GS_1 = gs_1 = 8
A_1  = a_1                = 9
BF_1 = bf_1 = AS_1 = as_1 = 10
B_1  = b_1  = CF0  = cf0  = 11
C0   = c0   = BS_1 = bs_1 = 12
CS0  = cs0  = DF0  = df0  = 13
D0   = d0                 = 14
EF0  = ef0  = DS0  = ds0  = 15
E0   = e0   = FF0  = ff0  = 16
F0   = f0   = ES0  = es0  = 17
FS0  = fs0  = GF0  = gf0  = 18
G0   = g0                 = 19
AF0  = af0  = GS0  = gs0  = 20
A0   = a0                 = 21
BF0  = bf0  = AS0  = as0  = 22
B0   = b0   = CF1  = cf1  = 23
C1   = c1   = BS0  = bs0  = 24
CS1  = cs1  = DF1  = df1  = 25
D1   = d1                 = 26
EF1  = ef1  = DS1  = ds1  = 27
E1   = e1   = FF1  = ff1  = 28
F1   = f1   = ES1  = es1  = 29
FS1  = fs1  = GF1  = gf1  = 30
G1   = g1                 = 31
AF1  = af1  = GS1  = gs1  = 32
A1   = a1                 = 33
BF1  = bf1  = AS1  = as1  = 34
B1   = b1   = CF2  = cf2  = 35
C2   = c2   = BS1  = bs1  = 36
CS2  = cs2  = DF2  = df2  = 37
D2   = d2                 = 38
EF2  = ef2  = DS2  = ds2  = 39
E2   = e2   = FF2  = ff2  = 40
F2   = f2   = ES2  = es2  = 41
FS2  = fs2  = GF2  = gf2  = 42
G2   = g2                 = 43
AF2  = af2  = GS2  = gs2  = 44
A2   = a2                 = 45
BF2  = bf2  = AS2  = as2  = 46
B2   = b2   = CF3  = cf3  = 47
C3   = c3   = BS2  = bs2  = 48
CS3  = cs3  = DF3  = df3  = 49
D3   = d3                 = 50
EF3  = ef3  = DS3  = ds3  = 51
E3   = e3   = FF3  = ff3  = 52
F3   = f3   = ES3  = es3  = 53
FS3  = fs3  = GF3  = gf3  = 54
G3   = g3                 = 55
AF3  = af3  = GS3  = gs3  = 56
A3   = a3                 = 57
BF3  = bf3  = AS3  = as3  = 58
B3   = b3   = CF4  = cf4  = 59
C4   = c4   = BS3  = bs3  = 60
CS4  = cs4  = DF4  = df4  = 61
D4   = d4                 = 62
EF4  = ef4  = DS4  = ds4  = 63
E4   = e4   = FF4  = ff4  = 64
F4   = f4   = ES4  = es4  = 65
FS4  = fs4  = GF4  = gf4  = 66
G4   = g4                 = 67
AF4  = af4  = GS4  = gs4  = 68
A4   = a4                 = 69
BF4  = bf4  = AS4  = as4  = 70
B4   = b4   = CF5  = cf5  = 71
C5   = c5   = BS4  = bs4  = 72
CS5  = cs5  = DF5  = df5  = 73
D5   = d5                 = 74
EF5  = ef5  = DS5  = ds5  = 75
E5   = e5   = FF5  = ff5  = 76
F5   = f5   = ES5  = es5  = 77
FS5  = fs5  = GF5  = gf5  = 78
G5   = g5                 = 79
AF5  = af5  = GS5  = gs5  = 80
A5   = a5                 = 81
BF5  = bf5  = AS5  = as5  = 82
B5   = b5   = CF6  = cf6  = 83
C6   = c6   = BS5  = bs5  = 84
CS6  = cs6  = DF6  = df6  = 85
D6   = d6                 = 86
EF6  = ef6  = DS6  = ds6  = 87
E6   = e6   = FF6  = ff6  = 88
F6   = f6   = ES6  = es6  = 89
FS6  = fs6  = GF6  = gf6  = 90
G6   = g6                 = 91
AF6  = af6  = GS6  = gs6  = 92
A6   = a6                 = 93
BF6  = bf6  = AS6  = as6  = 94
B6   = b6   = CF7  = cf7  = 95
C7   = c7   = BS6  = bs6  = 96
CS7  = cs7  = DF7  = df7  = 97
D7   = d7                 = 98
EF7  = ef7  = DS7  = ds7  = 99
E7   = e7   = FF7  = ff7  = 100
F7   = f7   = ES7  = es7  = 101
FS7  = fs7  = GF7  = gf7  = 102
G7   = g7                 = 103
AF7  = af7  = GS7  = gs7  = 104
A7   = a7                 = 105
BF7  = bf7  = AS7  = as7  = 106
B7   = b7   = CF8  = cf8  = 107
C8   = c8   = BS7  = bs7  = 108
CS8  = cs8  = DF8  = df8  = 109
D8   = d8                 = 110
EF8  = ef8  = DS8  = ds8  = 111
E8   = e8   = FF8  = ff8  = 112
F8   = f8   = ES8  = es8  = 113
FS8  = fs8  = GF8  = gf8  = 114
G8   = g8                 = 115
AF8  = af8  = GS8  = gs8  = 116
A8   = a8                 = 117
BF8  = bf8  = AS8  = as8  = 118
B8   = b8   = CF9  = cf9  = 119
C9   = c9   = BS8  = bs8  = 120
CS9  = cs9  = DF9  = df9  = 121
D9   = d9                 = 122
EF9  = ef9  = DS9  = ds9  = 123
E9   = e9   = FF9  = ff9  = 124
F9   = f9   = ES9  = es9  = 125
FS9  = fs9  = GF9  = gf9  = 126
G9   = g9                 = 127

######################################################################################
# MIDI instrument constants

ACOUSTIC_GRAND = PIANO = 0
BRIGHT_ACOUSTIC = 1
ELECTRIC_GRAND = 2
HONKYTONK_PIANO = HONKYTONK = 3
EPIANO1 = RHODES_PIANO = RHODES = 4
EPIANO2 = DX_PIANO = DX = 5
HARPSICHORD = 6
CLAVINET = 7
CELESTA = 8
GLOCKENSPIEL = 9
MUSIC_BOX = 10
VIBRAPHONE = VIBES = 11
MARIMBA = 12
XYLOPHONE = 13
TUBULAR_BELLS = 14
DULCIMER = 15
DRAWBAR_ORGAN = ORGAN = 16
PERCUSSIVE_ORGAN = JAZZ_ORGAN = 17
ROCK_ORGAN = 18
CHURCH_ORGAN = 19
REED_ORGAN = 20
ACCORDION = 21
HARMONICA = 22
TANGO_ACCORDION = BANDONEON = 23
NYLON_GUITAR = GUITAR = 24
STEEL_GUITAR = 25
JAZZ_GUITAR = 26
CLEAN_GUITAR = ELECTRIC_GUITAR = 27
MUTED_GUITAR = 28
OVERDRIVE_GUITAR = OVERDRIVEN_GUITAR = 29
DISTORTION_GUITAR = 30
GUITAR_HARMONICS = 31
ACOUSTIC_BASS = 32
BASS = ELECTRIC_BASS = FINGERED_BASS = 33
PICKED_BASS = 34
FRETLESS_BASS = 35
SLAP_BASS1 = 36
SLAP_BASS2 = 37
SYNTH_BASS1 = 38
SYNTH_BASS2 = 39
VIOLIN = 40
VIOLA = 41
CELLO = 42
CONTRABASS = 43
TREMOLO_STRINGS = 44
PIZZICATO_STRINGS = 45
ORCHESTRAL_HARP = HARP = 46
TIMPANI = 47
STRING_ENSEMBLE1 = STRINGS = 48
STRING_ENSEMBLE2 = 49
SYNTH_STRINGS1 = SYNTH = 50
SYNTH_STRINGS2 = 51
CHOIR_AHHS = CHOIR = 52
VOICE_OOHS = VOICE = 53
SYNTH_VOICE = VOX = 54
ORCHESTRA_HIT = 55
TRUMPET = 56
TROMBONE = 57
TUBA = 58
MUTED_TRUMPET = 59
FRENCH_HORN = HORN = 60
BRASS_SECTION = BRASS = 61
SYNTH_BRASS1 = 62
SYNTH_BRASS2 = 63
SOPRANO_SAX = SOPRANO_SAXOPHONE = 64
ALTO_SAX = ALTO_SAXOPHONE = 65
TENOR_SAX = TENOR_SAXOPHONE = SAX = SAXOPHONE = 66
BARITONE_SAX = BARITONE_SAXOPHONE = 67
OBOE = 68
ENGLISH_HORN = 69
BASSOON = 70
CLARINET = 71
PICCOLO = 72
FLUTE = 73
RECORDER = 74
PAN_FLUTE = 75
BLOWN_BOTTLE = BOTTLE = 76
SHAKUHACHI = 77
WHISTLE = 78
OCARINA = 79
LEAD_1_SQUARE = SQUARE = 80
LEAD_2_SAWTOOTH = SAWTOOTH = 81
LEAD_3_CALLIOPE = CALLIOPE = 82
LEAD_4_CHIFF = CHIFF = 83
LEAD_5_CHARANG = CHARANG = 84
LEAD_6_VOICE = SOLO_VOX = 85
LEAD_7_FIFTHS = FIFTHS = 86
LEAD_8_BASS_LEAD = BASS_LEAD = 87
PAD_1_NEW_AGE = NEW_AGE = 88
PAD_2_WARM = WARM_PAD = 89
PAD_3_POLYSYNTH = POLYSYNTH = 90
PAD_4_CHOIR = SPACE_VOICE = 91
PAD_5_GLASS = BOWED_GLASS = 92
PAD_6_METTALIC = METALLIC = 93
PAD_7_HALO = 94
PAD_8_SWEEP = 95
FX_1_RAIN = ICE_RAIN = 96
FX_2_SOUNDTRACK = 97
FX_3_CRYSTAL = 98
FX_4_ATMOSPHERE = 99
FX_5_BRIGHTNESS = BRIGHTNESS = 100
FX_6_GOBLINS = GOBLINS = 101
FX_7_ECHOES = ECHO_DROPS = 102
FX_8_SCI_FI = SCI_FI = 103
SITAR = 104
BANJO = 105
SHAMISEN = 106
KOTO = 107
KALIMBA = 108
BAGPIPE = 109
FIDDLE = 110
SHANNAI = 111
TINKLE_BELL = BELL = 112
AGOGO = 113
STEEL_DRUMS = 114
WOODBLOCK = 115
TAIKO_DRUM = TAIKO = 116
MELODIC_TOM = TOM_TOM = 117
SYNTH_DRUM = 118
REVERSE_CYMBAL = 119
GUITAR_FRET_NOISE = FRET_NOISE = 120
BREATH_NOISE = BREATH = 121
SEASHORE = SEA = 122
BIRD_TWEET = BIRD = 123
TELEPHONE_RING = TELEPHONE = 124
HELICOPTER = 125
APPLAUSE = 126
GUNSHOT = 127

# and MIDI drum and percussion abbreviations
ABD = 35
BASS_DRUM = 36
BDR = 36
STK = 37
SNARE = 38
SNR = 38
CLP = 39
ESN = 40
LFT = 41
CHH = 42
HFT = 43
PHH = 44
LTM = 45
OHH = 46
LMT = 47
HMT = 48
CC1 = 49
HGT = 50
RC1 = 51
CCM = 52
RBL = 53
TMB = 54
SCM = 55
CBL = 56
CC2 = 57
VSP = 58
RC2 = 59
HBG = 60
LBG = 61
MHC = 62
OHC = 63
LCG = 64
HTI = 65
LTI = 66
HAG = 67
LAG = 68
CBS = 69
MRC = 70
SWH = 71
LWH = 72
SGU = 73
LGU = 74
CLA = 75
HWB = 76
LWB = 77
MCU = 78
OCU = 79
MTR = 80
OTR = 81

# The MIDI specification stipulates that pitch bend be a 14-bit value, where zero is
# maximum downward bend, 16383 is maximum upward bend, and 8192 is the center (no pitch bend).
PITCHBEND_MIN = 0
PITCHBEND_MAX = 16383
PITCHBEND_NORMAL = 8192

# calculate constants from the way we handle pitch bend
OUR_PITCHBEND_MAX    = PITCHBEND_MAX - PITCHBEND_NORMAL
OUR_PITCHBEND_MIN    = -PITCHBEND_NORMAL
OUR_PITCHBEND_NORMAL = 0

# initialize pitchbend across channels to 0
_currentPitchbend = {}    # holds pitchbend to be used when playing a note / frequency (see below)
for i in range(16):
   _currentPitchbend[i] = 0   # set this channel's pitchbend to zero

# constants that came from jMusic
REST = -2147483648
DEFAULT_LENGTH_MULTIPLIER = 0.9


#######################################################################################
# MIDI Synthesizer and Soundfont Setup
#######################################################################################
_MIDI_SYNTH = tinysoundfont.Synth()   # prepare synthesizer
_SOUNDFONT = None                     # initialize soundfont to none to be explicit

try:
   # load soundfont with slightly reduced decibels for some headroom
   _SOUNDFONT = _MIDI_SYNTH.sfload("default.SF2", -0.3)

except Exception as e:
   # error, so warn the user
   print(f'music.py: Error setting up MIDI synthesizer (after soundfont load attempt): {e}')

if _SOUNDFONT is not None:   # soundfont loaded succesfully

   # so, set the soundfont for all 16 channels of the midi synth
   try:
      for i in range(16):   # set soundfont for all 16 channels

         if i == 9:   # reserve channel 9 for percussion
            _MIDI_SYNTH.program_select(i, _SOUNDFONT, 0, 0, is_drums=True)

         else:   # non-percussion channel
            _MIDI_SYNTH.program_select(i, _SOUNDFONT, 0, 0, is_drums=False)
      # now, all 16 channels are set

      # so, we can start the synthesizer
      _MIDI_SYNTH.start()

   except Exception as e:
      # error, so warn the user
      print(f'music.py: Error setting soundfont for MIDI synthesizer channels: {e}')

else:   # soundfont did not load correctly
   # so, warn the user
   print("music.py: Skipping synth program setup and start because soundfont did not load correctly.")

# register MIDI synthesizer cleanup function with atexit
# to ensure the synth stops when the program exits
atexit.register(_MIDI_SYNTH.stop)


######################################################################################
#### Free music library functions ####################################################
#######################################################################################

def mapValue(value, minValue, maxValue, minResultValue, maxResultValue):
   """
   Maps value from a given source range, i.e., (minValue, maxValue),
   to a new destination range, i.e., (minResultValue, maxResultValue).
   The result will be converted to the result data type (int, or float).
   """
   # check if value is within the specified range
   if value < minValue or value > maxValue:
      raise ValueError("value, " + str(value) + ", is outside the specified range, " \
                                 + str(minValue) + " to " + str(maxValue) + ".")

   # we are OK, so let's map
   value = float(value)  # ensure we are using float (for accuracy)
   normal = (value - minValue) / (maxValue - minValue)   # normalize source value

   # map to destination range
   result = normal * (maxResultValue - minResultValue) + minResultValue

   destinationType = type(minResultValue)  # find expected result data type
   result = destinationType(result)        # and apply it

   return result

def mapScale(value, minValue, maxValue, minResultValue, maxResultValue, scale=CHROMATIC_SCALE, key=None):
   """
   Maps value from a given source range, i.e., (minValue, maxValue), to a new destination range, i.e.,
   (minResultValue, maxResultValue), using the provided scale (pitch row) and key.  The scale provides
   a sieve (a pattern) to fit the results into.  The key determines how to shift the scale pattern to
   fit a particular key - if key is not provided, we assume it is the same as minResultValue (e.g., C4
   and C5 both refer to the key of C)).

   The result will be within the destination range rounded to closest pitch in the
   provided pitch row.   It always returns an int (since it is intended to be used
   as a pitch value).

   NOTE:  We are working within a 12-step tonal system (MIDI), i.e., octave is 12 steps away,
          so pitchRow must contain offsets (from the root) between 0 and 11.
   """
   # check if value is within the specified range
   if value < minValue or value > maxValue:
      raise ValueError("value, " + str(value) + ", is outside the specified range, " \
                                 + str(minValue) + " to " + str(maxValue) + ".")

   # check pitch row - it should contain offsets only from 0 to 11
   badOffsets = [offset for offset in scale if offset < 0 or offset > 11]
   if badOffsets != []:  # any illegal offsets?
      raise TypeError("scale, " + str(scale) + ", should contain values only from 0 to 11.")

   # figure out key of scale
   if key == None:             # if they didn't specify a key
      key = minResultValue % 12   # assume that minResultValue the root of the scale
   else:                       # otherwise,
      key = key % 12              # ensure it is between 0 and 11 (i.e., C4 and C5 both mean C, or 0).

   # we are OK, so let's map
   value = float(value)  # ensure we are using float (for accuracy)
   normal = (value - minValue) / (maxValue - minValue)   # normalize source value

   # NOTE:  The following calculation has a problem, exhibited below:
   #
   #   >>> x = 0
   #   >>> mapScale(x, 0, 10, 127, 0, MAJOR_SCALE)
   #   127
   #
   #   This is fine.
   #
   #   >>> x = 10
   #   >>> mapScale(x, 0, 10, 127, 0, MAJOR_SCALE)
   #   11
   #
   #   Problem:  This should be 0, not 11 !!

   # map to destination range (i.e., chromatic scale)
   # (subtracting 'key' aligns us with indices in the provided scale - we need to add it back later)
   chromaticStep = normal * (maxResultValue - minResultValue) + minResultValue - key

   # map to provided pitchRow scale
   pitchRowStep = chromaticStep * len(scale) / 12   # note in pitch row
   scaleDegree  = int(pitchRowStep % len(scale))    # find index into pitchRow list
   register     = int(pitchRowStep / len(scale))    # find pitch register (e.g. 4th, 5th, etc.)

   # calculate the octave (register) and add the pitch displacement from the octave.
   result = register * 12 + scale[scaleDegree]

   # adjust for key (scale offset)
   result = result + key

   # now, result has been sieved through the pitchSet (adjusted to fit the pitchSet)

   #result = int(round(result))   # force an int data type
   result = int(result)   # force an int data type

   return result

def frange(start, stop, step):
   """
   A range function for floats, with variable accuracy (controlled by
   number of digits in decimal part of 'step').
   """
   import math

   if step == 0:   # make sure we do not get into an infinite loop
      raise ValueError("frange() step argument must not be zero")

   result = []                         # holds resultant list
   # since Python's represetation of real numbers may not be exactly what we expect,
   # let's round to the number of decimals provided in 'step'
   accuracy = len(str(step-int(step))[1:])-1  # determine number of decimals in 'step'

   # determine which termination condition to use
   if step > 0:
      done = start >= stop
   else:
      done = start <= stop

   # generate sequence
   while not done:
      start = round(start, accuracy)  # use same number of decimals as 'step'
      result.append(start)
      start += step
      # again, determine which termination condition to use
      if step > 0:
         done = start >= stop
      else:
         done = start <= stop

   return result

def xfrange(start, stop, step):
   """
   A generator range function for floats, with variable accuracy (controlled by
   number of digits in decimal part of 'step').
   """
   import math

   if step == 0:   # make sure we do not get into an infinite loop
      raise ValueError("frange() step argument must not be zero")

   # since Python's represetation of real numbers may not be exactly what we expect,
   # let's round to the number of decimals provided in 'step'
   accuracy = len(str(step-int(step))[1:])-1  # determine number of decimals in 'step'

   # determine which termination condition to use
   if step > 0:
      done = start >= stop
   else:
      done = start <= stop

   # generate sequence
   while not done:
      start = round(start, accuracy)  # use same number of decimals as 'step'
      yield start
      start += step
      # again, determine which termination condition to use
      if step > 0:
         done = start >= stop
      else:
         done = start <= stop

def freqToNote(frequency):
   """Converts frequency to the closest MIDI note number with pitch bend value
      for finer control.  A4 corresponds to the note number 69 (concert pitch
      is set to 440Hz by default).  The default pitch bend range is 4 half tones,
      and ranges from -8191 to +8192 (0 means no pitch bend).
   """
   concertPitch = 440.0   # 440Hz
   bendRange = 4          # 4 semitones (2 below, 2 above)

   x = math.log(frequency / concertPitch, 2) * 12 + 69
   pitch = round(x)
   pitchBend = round((x - pitch) * 8192 / bendRange * 2)

   # TODO: I don't know why I needed to add 2 here when using default.SF2
   return int(pitch) + 2, int(pitchBend)

# create alias
frequencyToPitch = freqToNote

def noteToFreq(pitch):
   """Converts a MIDI pitch to the corresponding frequency.  A4 corresponds to the note number 69 (concert pitch
      is set to 440Hz by default).
   """

   concertPitch = 440.0   # 440Hz

   frequency = concertPitch * 2 ** ( (pitch - 69) / 12.0 )

   return frequency

# create alias
pitchToFrequency = noteToFreq


#######################################################################################
#### Transciption Classes #############################################################
#######################################################################################

class Note():

   def __str__(self):
      # notes can be either pitch or frequency based
      if self._type == "Pitch":
         type_str = f"(Pitch = {self._pitch})"
      else:
         type_str = f"(Frequency = {self._frequency})"

      # handle REST case where pitch is large negative number
      if self._pitch == REST:
         type_str = f"(Pitch = {self._pitch})"

      duration = f"(Duration = {self._duration})"
      dynamic  = f"(Dynamic = {self._dynamic})"
      pan      = f"(Pan = {self._pan})"
      length   = f"(Length = {self._length})"

      return f"<NOTE {type_str} {duration} {dynamic} {pan} {length}>\n"

   def __repr__(self):
      return self.__str__()

   def __init__(self, value, duration, dynamic=85, pan=0.5, length=None):

      # establish note properties (for readability)
      self._type      = None      # "Pitch" or "Frequency", describes how pitch was set
      self._pitch     = None      # MIDI pitch (0 to 127) or REST
      self._frequency = None      # frequency (Hz) or REST
      self._pitchBend = None      # pitch bend value (-8191 to +8192)
      self._duration  = float(duration)  # duration (in seconds) - ensure it's a float
      self._dynamic   = dynamic   # dynamic (0 to 127)
      self._pan       = pan       # panning (0.0 to 1.0)

      # NOTE: If value is an int, it signifies a MIDI pitch;
      # otherwise, if it is a float, it signifies a frequency.

      # do some basic error checking
      if type(value) == int and value != REST and (value < 0 or value > 127):
         raise TypeError(f"Note pitch should be an integer between 0 and 127 (it was {value}).")
      elif type(value) == float and not value > 0.0:
         raise TypeError(f"Note frequency should be a float greater than 0.0 (it was {value}).")
      elif (type(value) != int) and (type(value) != float):
         raise TypeError(f"Note first parameter should be a pitch (int) or a frequency (float) - it was {type(value)}.")

      # ensure duration is non-negative (but allow zero for chord notes)
      if self._duration < 0:
         self._duration = 0.1  # Set a small but audible duration as fallback
         print(f"Warning: Note duration must be non-negative. Using {self._duration} as default.")

      # set note length (if needed)
      if length is None:   # not provided?
         # handle the case where duration is zero (likely a chord note)
         if self._duration > 0:
            self._length = self._duration * DEFAULT_LENGTH_MULTIPLIER  # normally, duration * 0.9
         else:
            # for zero-duration notes (chord notes), set a small length
            self._length = 0.05  # Very small but non-zero length
      else:
         # ensure length is a float and non-negative
         self._length = float(length)
         if self._length < 0:
            self._length = self._duration * DEFAULT_LENGTH_MULTIPLIER
            print(f"Warning: Note length must be non-negative. Using calculated length {self._length}.")

      # now, construct the Note with the proper attributes
      if type(value) == int:
         self.setPitch(value)
      elif type(value) == float:
         self.setFrequency(value)

   def getPitch( self ):
      """
      Get the pitch for this note.
      """

      return self._pitch

   def setPitch( self, pitch ):
      """
      Set the pitch and frequency for this note from a MIDI pitch.
      """

      if type(pitch) != int:
         raise TypeError(f"Note pitch should be an integer - (it was a {type(pitch)}).")

      elif not (0 <= pitch <= 127) and pitch != REST:
         raise TypeError(f"Note pitch should be an integer between 0 and 127 - (it was {pitch}).")

      # set pitch
      self._type  = "Pitch"  # remember pitch/frequency was set from a pitch
      self._pitch = pitch

      if pitch == REST:
         # pitch is a rest, so set frequency to rest
         self._frequency = REST
         self._pitchBend = 0

      else:
         # otherwise, set frequency as normal
         self._frequency = noteToFreq(pitch)

   def getFrequency( self ):
      """
      Get the frequency for this note.
      """

      return self._frequency

   def setFrequency( self, frequency ):
      """
      Set the frequency and pitch for this note from a frequency.
      """

      # do some basic error checking
      if type(frequency) != float:
         raise TypeError(f"Note frequency should be a float - (it was {type(frequency)}).")

      elif frequency <= 0.0:
         raise TypeError(f"Note frequency should be a float greater than 0.0 - (it was {frequency}).")

      # set pitch and frequency
      self._type = "Frequency"  # remember pitch/frequency was set from a frequency
      self._frequency = frequency
      self._pitch, self._pitchBend = freqToNote(frequency)

   def getPitchBend( self ):
      """
      Get the pitch bend for this note (for microtonal sounds).
      """

      return self._pitchBend

   def getDuration( self ):
      """
      Get the duration for this note.
      """

      return self._duration

   def setDuration( self, duration ):
      """
      Set the duration for this note.
      When duration changes, length is updated proportionally based on the original ratio.
      """

      # Ensure the input is converted to float
      try:
         duration = float(duration)

         # Allow zero duration specifically for chord notes in jMusic format
         # but prevent negative durations
         if duration < 0:
            print(f"Warning: Note duration must be non-negative (got {duration}). Using 0.1 as fallback.")
            duration = 0.1
      except (ValueError, TypeError):
         print(f"Warning: Invalid duration value. Using 0.1 as fallback.")
         duration = 0.1

      # calculate length factor (ratio of length to duration)
      # this preserves the original articulation style
      lengthFactor = self._length / self._duration if self._duration > 0 else DEFAULT_LENGTH_MULTIPLIER

      # update duration and length
      self._duration = duration

      # only update length if duration is non-zero
      if duration > 0:
         self._length = duration * lengthFactor

   def getLength( self ):
      """
      Get the length for this note.
      """

      return self._length

   def setLength( self, length ):
      """
      Set the length for this note.
      Length determines how long the note actually sounds (versus its notated duration).
      """

      # ensure the input is converted to float
      try:
         length = float(length)
         # allow zero length but prevent negative values
         if length < 0:
            print(f"Warning: Note length must be non-negative (got {length}). Using {self._duration * DEFAULT_LENGTH_MULTIPLIER} as fallback.")
            length = self._duration * DEFAULT_LENGTH_MULTIPLIER
      except (ValueError, TypeError):
         print(f"Warning: Invalid length value. Using {self._duration * DEFAULT_LENGTH_MULTIPLIER} as fallback.")
         length = self._duration * DEFAULT_LENGTH_MULTIPLIER

      self._length = length

   def getDynamic( self ):
      """
      Get the dynamic for this note.
      """

      return self._dynamic

   def setDynamic( self, dynamic ):
      """
      Set the dynamic for this note.
      """

      if type(dynamic) != int:
         raise TypeError(f"Note dynamic should be an integer - (it was {type(dynamic)}).")

      elif not (0 <= dynamic <= 127) and (dynamic != REST):
         raise TypeError(f"Note dynamic should be an integer between 0 and 127 - (it was {dynamic}).")

      self._dynamic = dynamic

   def getPan( self ):
      """
      Get the panning for this note.
      """

      return self._pan

   def setPan( self, pan ):
      """
      Set the panning for this note.
      """

      if not (0.0 <= pan <= 1.0):
         raise TypeError(f"Note panning should be a float between 0.0 and 1.0 - (it was {pan})")

      self._pan = float( pan )

   def isRest( self ):
      """
      Determine whether or not this note is a REST.
      """

      return (self._pitch == REST)

   def copy( self ):
      """
      Create a copy of this note (leaving the original unmodified).
      """

      if self._type == "Pitch":
         value = self._pitch

      elif self._type == "Frequency":
         value = self._frequency

      return Note(
         value,
         self._duration,
         self._dynamic,
         self._pan,
         self._length
      )


class Phrase():

   def __str__( self ):
      # build header string
      phraseString = (
         f'\n<-------- PHRASE \'{self.getTitle()}\' '
         f'contains {self.getSize()} notes.  '
         f'Start time: {self.getStartTime()} -------->\n'
      )

      # add each note in the phrase
      for note in self.getNoteList():
         phraseString += str(note)

      return phraseString

   def __repr__( self ):
      return self.__str__()

   def __init__( self, arg1=None, arg2=None ):

      # initialize default phrase properties
      self._noteList      = []
      self._title         = "Untitled Phrase"
      self._instrument    = -1
      self._tempo         = -1
      self._startTime     = None

      # parse arguments by type - (arg1, arg2)
      # (None, None) is an empty phrase
      # (Note, None) is a phrase with a single note
      # (Note, float) is a phrase with a single note and a start time
      # (float, None) is an empty phrase with a start time

      if type(arg1) is Note:
         self.addNote(arg1)

         if type(arg2) in [float, int]:
            self.setStartTime(arg2)

         elif arg2 is not None:
            raise TypeError( "Phrase(Note, startTime) expected types (Note, float) -" \
                              + f" got (Note, {type(arg2)})." )

      elif type(arg1) in [float, int]:
         self.setStartTime(arg1)

         if arg2 is not None:
            raise TypeError(f"Phrase(startTime) expected type (float) - got (float, {type(arg2)}).")

      elif arg1 is not None:
         raise TypeError(f"Phrase() first argument expected Note or float - got ({type(arg1)}).")

   def addNote( self, note, duration=None ):
      """
      Appends the given note to this phrase, or a new note of given pitch (0-127) and duration (a float) to the phrase.
      """
      if duration is not None:
         # two arguments were given, so create a new note with pitch and duration
         note = Note(note, duration)
         self._noteList.append(note)
      else:
         # one argument given - either a Note object or invalid input
         if isinstance(note, Note):
            self._noteList.append(note)
         else:
            raise TypeError(f"Phrase.addNote() expected a Note or (pitch, duration) - got {type(note)}.")

   def addChord( self, pitchList, duration, dynamic=85, pan=0.5, length=None ):
      """
      Appends a chord containing the specified pitches with the specified
      duration, dynamic, panning.
      Dynamic and panning values are optional.
      """

      # Ensure we have valid input
      if not pitchList:
         raise ValueError("Cannot add an empty chord - pitchList must contain at least one pitch.")

      # Convert duration to float to ensure consistent handling
      duration = float(duration)

      # set chord length (if needed)
      if length is None:   # not provided?
         length = duration * DEFAULT_LENGTH_MULTIPLIER  # normally, duration * 0.9
      else:
         length = float(length)  # ensure it's a float

      # For chord notes, all notes but the last one have zero duration
      # This is how jMusic/MIDI handles chords - only the last note carries the duration

      # add all notes, except last one, with no duration and normal length
      # (exploiting how Play.midi() and Write.midi() work)
      for i in range(len(pitchList) - 1):
         n = Note(pitchList[i], 0, dynamic, pan, length)
         self.addNote(n)

      # now, add last note with proper duration (and length)
      n = Note(pitchList[-1], duration, dynamic, pan, length)
      self.addNote(n)

   def addNoteList(
         self, pitchList, durationList,
         dynamicList=[], panoramicList=[], lengthList=[]
      ):
      """
      Add notes to the phrase using provided lists of pitches, durations, etc.
      """

      # if dynamics was not provided, construct it with max value
      if dynamicList == []:
         dynamicList = [85] * len( pitchList )

      # if panoramics was not provided, construct it at CENTER
      if panoramicList == []:
         panoramicList = [0.5] * len( pitchList )

      # if note lengths was not provided, construct it at 90% of note duration
      if lengthList == []:
         lengthList = [
            duration * DEFAULT_LENGTH_MULTIPLIER for duration in durationList
         ]

      # check if provided lists have equal lengths
      if not ( len(pitchList)    ==
              len(durationList)  ==
              len(dynamicList)   ==
              len(panoramicList) ==
              len(lengthList) ):
         raise ValueError( "addNoteList() The provided lists should have the " \
                          + "same length." )

      # traverse the pitch list and handle each entry appropriately
      for i in range( len(pitchList) ):

         # is it a chord or a note?

         if type(pitchList[i]) == list:
            # chord, so pass its values to addChord()
            self.addChord(
                pitchList[i],
                durationList[i],
                dynamicList[i],
                panoramicList[i],
                lengthList[i]
            )

         else:
            # note, construct a new note and add it
            n = Note(
                pitchList[i],
                durationList[i],
                dynamicList[i],
                panoramicList[i],
                lengthList[i]
            )
            self.addNote(n)

   def getNoteList( self ):
      """
      Get the notes in this phrase.
      """

      return self._noteList

   def getInstrument( self ):
      """
      Get the instrument for this phrase.
      """

      return self._instrument

   def setInstrument( self, instrument ):
      """
      Set the instrument for this phrase.
      """

      if type(instrument) != int:
         raise TypeError(f"Instrument should be an integer - (it was {type(instrument)}).")

      if instrument == -1:
         pass

      elif not (0 <= instrument <= 127):
         raise TypeError(f"Instrument should be an integer between 0 and 127 - (it was {instrument}).")

      self._instrument = instrument

   def getTempo( self ):
      """
      Get the tempo for this phrase.
      """

      return self._tempo

   def setTempo( self, tempo ):
      """
      Set the tempo for this phrase.
      """

      self._tempo = float(tempo)

   def getTitle( self ):
      """
      Get the title for this phrase.
      """

      return self._title

   def setTitle( self, title ):
      """
      Set the title for this phrase.
      """

      if type(title) != str:
         raise TypeError(f"Title should be a string - (it was {type(title)}).")

      self._title = title

   def setDynamic( self, dynamic ):
      """
      Set the dynamic of every note in this phrase.
      """

      for note in self._noteList:
         note.setDynamic( dynamic )

   def setPan( self, pan ):
      """
      Set the panning of every note in this phrase.
      """

      for note in self._noteList:
         note.setPan(pan)

   def getStartTime( self ):
      """
      Get the startTime of this phrase.
      """
      if self._startTime is None:
         self._startTime = 0.0

      return self._startTime

   def setStartTime( self, startTime ):
      """
      Set the startTime of this phrase.
      """
      if startTime is None:
         startTime = 0.0

      self._startTime = float( startTime )

   def getEndTime( self ):
      """
      Get the endTime of this phrase.
      """

      # sum duration of every note in this phrase
      endTime = self.getStartTime()

      for note in self.getNoteList():
         endTime += note.getDuration()

      return endTime

   def getSize( self ):
      """
      Get the number of notes in this phrase.
      """

      return len( self._noteList )

   def getNote( self, index ):
      """
      Gets the note object at 'index'. It does not modify this phrase.
      """

      return self._noteList[index]

   def removeNote( self, index ):
      """
      Removes the note object at 'index'.
      """

      return self._noteList.pop(index)

   def getNoteStartTime( self, index ):
      """
      Calculates the start time, in beats, of the note at the specified index.
      """

      # sum duration of every note up to specified index
      startTime = 0

      for i in range( index ):
         startTime += self._noteList[i].getDuration()

      return startTime

   def getLowestPitch( self ):
      """
      Finds the pitch value of the lowest note in this phrase.
      """

      # check every note in this phrase for the lowest pitch
      lowestPitch = float(math.inf)

      for note in self._noteList:
         if note.getPitch() < lowestPitch:
               lowestPitch = note.getPitch()

      return lowestPitch

   def getHighestPitch( self ):
      """
      Finds the pitch value of the highest note in this phrase.
      """

      # check every note in this phrase for the highest pitch
      highestPitch = float(-math.inf)

      for note in self._noteList:
         if note.getPitch() > highestPitch:
               highestPitch = note.getPitch()

      return highestPitch

   def getShortestDuration( self ):
      """
      Finds the duration value of the shortest note in this phrase.
      """

      # check every note in this phrase for the shortest duration
      shortestDuration = float(math.inf)

      for note in self._noteList:
         if note.getDuration() < shortestDuration:
               shortestDuration = note.getDuration()

      return shortestDuration

   def getLongestDuration( self ):
      """
      Finds the duration value of the shortest note in this phrase.
      """

      # check every note in this phrase for the longest duration
      longestDuration = float(-math.inf)

      for note in self._noteList:
         if note.getDuration() > longestDuration:
               longestDuration = note.getDuration()

      return longestDuration

   def copy( self ):
      """
      Create a copy of this phrase (leaving the original unmodified).
      """

      # create a new phrase
      newPhrase = Phrase()

      # copy this phrase's properties
      newPhrase.setTitle( self.getTitle() )
      newPhrase.setInstrument( self.getInstrument() )
      newPhrase.setTempo( self.getTempo() )
      newPhrase.setStartTime( self.getStartTime() )

      # copy all notes in this phrase
      for note in self.getNoteList():
         newPhrase.addNote( note.copy() )

      return newPhrase

   def empty( self ):
      """
      Remove all notes from this phrase.
      """

      self._noteList = []


class Part():

   def __str__( self ):
      # build header string
      partString = (
         f'\n<----- PART \'{self.getTitle()}\' contains {self.getSize()} phrases.  ----->\n'
         f'Channel = {self.getChannel()}\n'
         f'Instrument = {self.getInstrument()}\n'
      )

      # add each phrase in the part
      displayStartTime = 0.0

      for phrase in self.getPhraseList():
         # create a copy of the phrase with an adjusted start time for display purposes
         tempPhrase = phrase.copy()
         tempPhrase.setStartTime(displayStartTime)
         partString += str(tempPhrase)
         displayStartTime += phrase.getEndTime()

      return partString

   def __repr__(self):
      return self.__str__()

   def __init__( self, arg1=None, arg2=None, arg3=None ):

      # initialize default part properties
      self._phraseList = []
      self._title      = "Untitled Part"
      self._instrument = -1
      self._channel    = 0
      self._tempo      = -1
      self._volume     = -1

      # parse arguments by type - (arg1, arg2, arg3)
      # (None, None, None) is an empty part
      # (int,  None, None) is an empty part with an instrument
      # (int,  int,  None) is an empty part with an instrument and channel
      # (str,  int,  int ) is an empty part a title, instrument, and channel
      # (Phrase, None, None) is a part with a single phrase

      if type(arg1) is int:
         self.setInstrument(arg1)

         if type(arg2) is int:
            self.setChannel(arg2)

         if arg3 is not None:
            raise TypeError( "Error: 3 arguments were given when 2 were expected." )

      elif type(arg1) == str:
         self.setTitle(arg1)

         if type(arg2) is int:
            self.setInstrument(arg2)

         if type(arg3) is int:
            self.setChannel(arg3)

      elif type(arg1) == Phrase:
         self.addPhrase(arg1)

   def addPhrase( self, phrase ):
      """
      Appends the given phrase to this part.
      """

      if type( phrase ) is not Phrase:
         raise TypeError(f"addPhrase(phrase) parameter should be a Phrase - (it was {type(phrase)}).")

      if phrase.getStartTime() is None:
         # first phrase starts at 0.0, subsequent phrases start after previous content
         if not self.getPhraseList():
            phrase.setStartTime(0.0)  # start the first phrase at time 0
         else:
            # subsequent phrases start after previous content
            phrase.setStartTime(self.getEndTime())

      self._phraseList.append( phrase )

   def addPhraseList( self, phraseList ):
      """
      Add list of phrases to this part.
      """

      for phrase in phraseList:
         self.addPhrase(phrase)

   def getPhraseList( self ):
      """
      Get the phrases in this part.
      """

      return self._phraseList

   def getTitle( self ):
      """
      Get the title for this part.
      """

      return self._title

   def setTitle( self, title ):
      """
      Set the title for this part.
      """

      if type( title ) != str:
         raise TypeError(f"Part title should be a string - (it was {type(title)})")

      self._title = title

   def getInstrument( self ):
      """
      Get the instrument for this part.
      """

      return self._instrument

   def setInstrument( self, instrument ):
      """
      Set the instrument for this part.
      """

      if type( instrument ) != int:
         raise TypeError(f"Instrument should be an integer - (it was {type(instrument)})")

      elif instrument == -1:
         # -1 uses the global instrument for this part's channel
         pass

      elif not ( 0 <= instrument <= 127 ):
         # MIDI instruments are between 0 and 127
         raise TypeError(f"Instrument should be an integer between 0 and 127 - (it was {instrument})")

      self._instrument = instrument

   def getChannel( self ):
      """
      Get the channel for this part.
      """

      return self._channel

   def setChannel( self, channel ):
      """
      Set the channel for this part.
      """

      if type(channel) != int:
         raise TypeError(f"Channel should be an integer - (it was {type(channel)})")

      elif not (0 <= channel <= 15):
         raise TypeError(f"Channel should be an integer between 0 and 15 - (it was {channel})")

      self._channel = channel

   def getTempo( self ):
      """
      Get the tempo for this part.
      """

      return self._tempo

   def setTempo( self, tempo ):
      """
      Set the tempo for this part.
      """

      self._tempo = float(tempo)

   def getVolume( self ):
      """
      Get the volume for this part.
      """

      return self._volume

   def setVolume( self, volume ):
      """
      Set the volume for this part.
      """
      if type(volume) != int:
         raise TypeError(f"Volume should be an integer - (it was {type(volume)})")

      elif volume == -1:
         volume = 127

      elif not (0 <= volume <= 127):
         raise TypeError(f"Volume should be an integer between 0 and 127 - (it was {volume})")

      self._volume = volume

   def getStartTime( self ):
      """
      Get the start time for this part.
      """

      startTime = float(math.inf)

      # find the earliest starting time of all phrases in this part
      for phrase in self.getPhraseList():
         startTime = min( startTime, phrase.getStartTime() )

      if startTime is None:
         startTime = 0.0

      return startTime

   def getEndTime( self ):
      """
      Get the end time for this part.
      """

      # check if the part is empty
      if not self.getPhraseList():
         return 0.0  # return 0.0 for an empty part instead of -infinity

      endTime = float(-math.inf)

      # find the latest ending time of all phrases in this part
      for phrase in self.getPhraseList():
         endTime = max( endTime, phrase.getEndTime() )

      return endTime

   def getSize( self ):
      """
      Get the number of phrases in this part.
      """

      return len( self.getPhraseList() )

   def setPan( self, panning ):
      """
      Set the panning of every note in this part.
      """

      for phrase in self.getPhraseList():
         phrase.setPan( panning )

   def setDynamic( self, dynamic ):
      """
      Set the dynamic of every note in this part.
      """

      for phrase in self.getPhraseList():
         phrase.setDynamic( dynamic )

   def copy( self ):
      """
      Create a copy of this part (leaving the original unmodified).
      """

      # create a new part
      newPart = Part()

      # copy this part's properties
      newPart.setTitle( self.getTitle() )
      newPart.setInstrument( self.getInstrument() )
      newPart.setChannel( self.getChannel() )
      newPart.setTempo( self.getTempo() )
      newPart.setVolume( self.getVolume() )

      # copy all phrases in this part
      for phrase in self.getPhraseList():
         newPart.addPhrase( phrase.copy() )

      return newPart

   def empty( self ):
      """
      Remove all phrases from this part.
      """

      self._phraseList = []

class Score():

   def __str__( self ):
      # build header string
      scoreString = (
         f'\n<***** SCORE \'{self.getTitle()}\' '
         f'contains {self.getSize()} parts. ****>\n'
         f'Score Tempo = {self.getTempo()} bpm\n'
      )

      # add each part in the score
      for part in self.getPartList():
         scoreString += str(part) + "\n"

      return scoreString

   def __repr__( self ):
      return self.__str__()

   def __init__( self, arg1=None, arg2=None ):

      # initialize default score properties
      self._partList      = []
      self._title         = "Untitled Score"
      self._tempo         = 60.0
      self._volume        = 85
      self._timeSignature = [4, 4]
      self._keySignature  = 0
      self._keyQuality    = 0

      # parse arguments by type - (arg1, arg2)
      # (None, None) is an empty score
      # (str,  None) is an empty score with a title
      # (str,  int)  is an empty score with a title and tempo
      # (int,  None) is an empty score with a tempo
      # (Part, None) is a score with a single part

      if type(arg1) is str:
         self.setTitle( arg1 )

         if arg2 is not None:
            self.setTempo(arg2)

      elif type(arg1) is Part:
         self.addPart(arg1)

      elif arg1 is not None:
         self.setTempo(arg1)

   def addPart( self, part ):
      """Appends the given part to this score."""
      if type(part) is not Part:
         raise TypeError(f'addPart(part) parameter should be a Part - (it was {type(part)}).')

      self._partList.append(part)

   def addPartList( self, partList ):
      """Add multiple parts (in a list) to this score."""
      for part in partList:
         self.addPart( part )

   def getPartList( self ):
      """Get parts in this score as a list."""
      return self._partList

   def getTitle( self ):
      """Get the title for this score."""
      return self._title

   def setTitle( self, title ):
      """Set the title for this score."""
      if type( title ) != str:
         raise TypeError(f'Score title should be a string - (it was {type(title)}).')

      self._title = title

   def getTempo( self ):
      """Get the tempo for this score."""
      return self._tempo

   def setTempo( self, tempo ):
      """Set the tempo for this score."""
      self._tempo = float(tempo)

   def getVolume(self):
      """Get the volume for this score."""
      return self._volume

   def setVolume(self, volume):
      """Set the volume for this score."""
      if type( volume ) != int:
         raise TypeError(f'Volume should be an integer - (it was {type(volume)}).')

      elif not (0 <= volume <= 127):
         raise TypeError(f'Volume should be an integer between 0 and 127 - (it was {volume}).')

      self._volume = volume

   def getNumerator( self ):
      """Get the time signature numerator for this score."""

      return self._timeSignature[0]

   def getDenominator( self ):
      """Get the time signature denominator for this score."""
      return self._timeSignature[1]

   def setTimeSignature(self, numerator, denominator):
      """Set the time signature for this score."""
      self._timeSignature = [numerator, denominator]

   def getKeyQuality(self):
      """Get the key quality for this score. (0 is major, 1 is minor)"""
      return self._keyQuality

   def setKeyQuality(self, quality):
      """Set the key quality for this score. (0 is major, 1 is minor)"""
      if type( quality ) != int:
         raise TypeError(f'Key quality should be an integer - (it was {type(quality)}).')

      elif not (quality == 0 or quality == 1):
         raise TypeError(f'Key quality should be either 0 or 1 - (it was {quality}).')

      self._keyQuality = quality

   def getKeySignature( self ):
      """Get the key signature for this score."""
      return self._keySignature

   def setKeySignature( self, signature ):
      """Set the key signature for this score."""
      if type( signature ) != int:
         raise TypeError(f'Key signature should be an integer - (it was {type(signature)}).')

      elif not (-8 < signature < 8):
         raise TypeError(f'Key signature should be an integer between -7 and 7 - (it was {signature}).')

      self._keySignature = signature

   def getStartTime( self ):
      """Get the start time for this score."""

      startTime = float(math.inf)

      # find the earliest starting time of all parts in this score
      for part in self.getPartList():
         startTime = min( startTime, part.getStartTime() )

      return startTime


   def getEndTime( self ):
      """Get the ending time for this score."""
      endTime = float(-math.inf)

      # find the latest ending time of all parts in this score
      for part in self.getPartList():
         endTime = max( endTime, part.getEndTime() )

      return endTime

   def getSize( self ):
      """Get the number of parts in this score."""
      return len( self.getPartList() )

   def setPan( self, pan ):
      """Set the panning of every part in this score."""
      for part in self.getPartList():
         part.setPan(pan)

   def copy( self ):
      """Get a copy of this score (leaving the original unmodified)."""
      # create a new score
      newScore = Score()
      # copy this score's properties
      newScore.setTitle( self.getTitle() )
      newScore.setTempo( self.getTempo() )
      newScore.setVolume( self.getVolume() )
      newScore.setTimeSignature( self.getNumerator(), self.getDenominator() )
      newScore.setKeySignature( self.getKeySignature() )
      newScore.setKeyQuality( self.getKeyQuality() )

      # copy all parts in this score
      for part in self.getPartList():
         newScore.addPart( part.copy() )

      return newScore

   def empty(self):
      """Remove all parts from this score."""
      self._partList.clear()


#######################################################################################
#### Play #############################################################################
#######################################################################################

# store Timer objects to prevent garbage collection
_NOTE_TIMERS = []

# track active notes, {(pitch, channel): count}
_activeNotes = {}

# track active audio samples
_activeAudioSamples = []

# track settings on each channel for _MIDI_SYNTH
_currentInstrument = [0] * 16     # default to piano for all 16 channels
_currentVolume = [100] * 16       # default to moderate volume for all channels
_currentPanning = [64] * 16       # default to center for all channels
_currentPitchbend = [0] * 16      # default to no bend for all channels

class Play:
   """Provides functionality for playing music data (notes, phrases, etc.)."""

   @staticmethod
   def midi(material):
      """
      Play transcription material (Score, Part, Phrase, Note)
      using our own Play.note() function.
      """

      # do necessary datatype wrapping (MidiSynth() expects a Score)
      if type(material) == Note:
         material = Phrase(material)
      if type(material) == Phrase:   # no elif - we need to successively wrap from Note to Score
         material = Part(material)
         material.setInstrument(-1)     # indicate no default instrument (needed to access global instrument)
      if type(material) == Part:     # no elif - we need to successively wrap from Note to Score
         material = Score(material)
      if type(material) == Score:
         # we are good - let's play it then!
         score = material   # by now, material is a score, so create an alias (for readability)

         # loop through all parts and phrases to get all notes
         noteList = []               # holds all notes
         tempo = score.getTempo()    # get global tempo (can be overidden by part and phrase tempos)
         for part in score.getPartList():   # traverse all parts
            channel = part.getChannel()        # get part channel
            instrument = Play.getInstrument(channel)  # get global instrument for this channel
            if part.getInstrument() > -1:      # has the part instrument been set?
               instrument = part.getInstrument()  # yes, so it takes precedence
            if part.getTempo() > -1:           # has the part tempo been set?
               tempo = part.getTempo()            # yes, so update tempo
            for phrase in part.getPhraseList():   # traverse all phrases in part
               if phrase.getInstrument() > -1:        # is this phrase's instrument set?
                  instrument = phrase.getInstrument()    # yes, so it takes precedence
               if phrase.getTempo() > -1:          # has the phrase tempo been set?
                  tempo = phrase.getTempo()           # yes, so update tempo

               # time factor to convert time from jMusic Score units to milliseconds
               # (this needs to happen here every time, as we may be using the tempo from score, part, or phrase)
               FACTOR = 1000 * 60.0 / tempo

               # process notes in this phrase
               startTime = phrase.getStartTime() * FACTOR   # in milliseconds
               for note in phrase.getNoteList():
                  frequency = note.getFrequency()
                  panning = note.getPan()
                  panning = mapValue(panning, 0.0, 1.0, 0, 127)    # map from range 0.0..1.0 (Note panning) to range 0..127 (as expected by Java synthesizer)
                  start = int(startTime)                           # remember this note's start time (in milliseconds)

                  # NOTE:  Below we use note length as opposed to duration (getLength() vs. getDuration())
                  # since note length gives us a more natural sounding note (with proper decay), whereas
                  # note duration captures the more formal (printed score) duration (which sounds unnatural).
                  duration = int(note.getLength() * FACTOR)             # get note length (as oppposed to duration!) and convert to milliseconds
                  startTime = startTime + note.getDuration() * FACTOR   # update start time (in milliseconds)
                  velocity = note.getDynamic()

                  # accumulate non-REST notes
                  if (frequency != REST):
                     noteList.append((start, duration, frequency, velocity, channel, instrument, panning))   # put start time first and duration second, so we can sort easily by start time (below),
                     # and so that notes that are members of a chord as denoted by having a duration of 0 come before the note that gives the specified chord duration

         # sort notes by start time
         noteList.sort()

         # schedule playing all notes in noteList
         chordNotes = []      # used to process notes belonging in a chord
         for start, duration, pitch, velocity, channel, instrument, panning in noteList:
            # set appropriate instrument for this channel
            Play.setInstrument(instrument, channel)

            # handle chord (if any)
            # Chords are denoted by a sequence of notes having the same start time and 0 duration (except the last note
            # of the chord).
            if duration == 0:   # does this note belong in a chord?
               chordNotes.append([start, duration, pitch, velocity, channel, panning])  # add it to the list of chord notes

            elif chordNotes == []:   # is this a regular, solo note (not part of a chord)?

               # yes, so schedule it to play via a Play.note event
               Play.note(pitch, start, duration, velocity, channel, panning)
               #print "Play.note(" + str(pitch) + ", " + str(int(start * FACTOR)) + ", " + str(int(duration * FACTOR)) + ", " + str(velocity) + ", " + str(channel) + ")"

            else:   # note has a normal duration and it is part of a chord

               # first, add this note together with this other chord notes
               chordNotes.append([start, duration, pitch, velocity, channel, panning])

               # now, schedule all notes in the chord list using last note's duration
               for start, ignoreThisDuration, pitch, velocity, channel, panning in chordNotes:
                  # schedule this note using chord's duration (provided by the last note in the chord)
                  Play.note(pitch, start, duration, velocity, channel, panning)
                  #print "Chord: Play.note(" + str(pitch) + ", " + str(int(start * FACTOR)) + ", " + str(int(duration * FACTOR)) + ", " + str(velocity) + ", " + str(channel) + ")"
               # now, all chord notes have been scheduled

               # so, clear chord notes to continue handling new notes (if any)
               chordNotes = []

         # now, all notes have been scheduled for future playing - scheduled notes can always be stopped using
         # JEM's stop button - this will stop all running timers (used by Play.note() to schedule playing of notes)
         #print "Play.note(" + str(pitch) + ", " + str(int(start * FACTOR)) + ", " + str(int(duration * FACTOR)) + ", " + str(velocity) + ", " + str(channel) + ")"

      else:   # error check
         print(f'Play.midi(): Unrecognized type {type(material)}, expected Note, Phrase, Part, or Score.')

   @staticmethod
   def noteOn(pitch, velocity=100, channel=0, panning = -1):
      """
      Send a NOTE_ON message for this pitch to the synthesizer object.
      # Default panning of -1 means to use the default (global) panning setting of the
      synthesizer.
      """

      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # convert to frequency, then let frequencyOn handle it
         frequency = noteToFreq(pitch)
         Play.frequencyOn(frequency, velocity, channel, panning)

      elif type(pitch) == float:        # a pitch in Hertz?
         Play.frequencyOn(pitch, velocity, channel, panning)  # start it

      else:
         print(f'Play.noteOn(): Unrecognized pitch {pitch}, expected MIDI pitch from 0 to 127 (int), or frequency in Hz from 8.17 to 12600.0 (float).')

   @staticmethod
   def frequencyOn(frequency, velocity=100, channel=0, panning = -1):
      """
      Send a NOTE_ON message for this frequency (in Hz) to the synthesizer object.
      Default panning of -1 means to use the default (global) panning setting of the
      synthesizer.
      """

      if (type(frequency) == float) and (8.17 <= frequency <= 12600.0): # a pitch in Hertz (within MIDI pitch range 0 to 127)?

         pitch, bend = freqToNote( frequency )  # convert to MIDI note and pitch bend
         Play.noteOnPitchBend(pitch, bend, velocity, channel, panning)  # and start it

      else:

         print(f'Play.frequencyOn(): Invalid frequency {frequency}, expected frequency in Hz from 8.17 to 12600.0 (float).')

   @staticmethod
   def noteOff(value, channel=0):
      """
      Send a NOTE_OFF message for this pitch to the synthesizer object.
      """

      if type(value) == float:
         # this is actually a frequency, so convert it to a pitch first
         value, bend = freqToNote(value)

      if (type(value) == int) and (0 <= value <= 127):
         # this is a pitch, so let's stop it!

         # create noteID for this note
         noteID = (value, channel)
         global _activeNotes
         if noteID in _activeNotes:
            _activeNotes[noteID] -= 1
            if _activeNotes[noteID] <= 0:
               # turn off note in the synthesizer
               _MIDI_SYNTH.noteoff(channel, value)   # value represents pitch here
               # NOTE: just to be good citizens, also turn pitch bend to normal
               Play.setPitchBend(0, channel)
               del _activeNotes[noteID]
         else:
            # If not tracked, just turn off for safety
            _MIDI_SYNTH.noteoff(channel, value)
            Play.setPitchBend(0, channel)

      else:   # value is not valid
         # so, warn the user
         print(f'Play.noteOff(): Unrecognized pitch {value}, expected MIDI pitch from 0 to 127 (int).')

   @staticmethod
   def frequencyOff(value, channel=0):
      """
      Send a NOTE_OFF message for this frequency (in Hz) to the synthesizer object.
      """

      if (type(value) == float) and (8.17 <= value <= 12600.0):
         # convert to MIDI note and pitch bend
         value, bend = freqToNote(value)

      if type(value) == int:
         # pass pitch to Play.noteOff()
         Play.noteOff(value, channel)

      else:
         print(f'Play.frequencyOff(): Invalid frequency {value}, expected frequency in Hz from 8.17 to 12600.0 (float).')

   @staticmethod
   def note(pitch, start, duration, velocity=100, channel=0, panning = -1):
      """Plays a note with given 'start' time (in milliseconds from now), 'duration' (in milliseconds
         from 'start' time), with given 'velocity' on 'channel'.  Default panning of -1 means to
         use the default (global) panning setting of the Java synthesizer. """

      # check for negative start times and durations
      if start < 0:
         print(f'Play.note(): Start time must be non-negative, got {start}')
         return

      # ensure duration is a positive number
      if duration <= 0:
         print(f'Play.note(): Duration must be positive, got {duration}')
         return

      # store the Timer objects in a list - this prevents them from being garbage collected
      # before they execute
      global _NOTE_TIMERS

      # create a timer for the note-on event
      noteOn = Timer(start, Play.noteOn, [pitch, velocity, channel, panning], False)

      # create a timer for the note-off event
      noteOff = Timer(start+duration, Play.noteOff, [pitch, channel], False)

      # store timers to prevent garbage collection
      _NOTE_TIMERS.append(noteOn)
      _NOTE_TIMERS.append(noteOff)

      # and activate timers (set things in motion)
      noteOn.start()
      noteOff.start()

      # We'll clean up _NOTE_TIMERS periodically to avoid memory leaks
      # Keep only timers that are still running
      _NOTE_TIMERS = [timer for timer in _NOTE_TIMERS if timer.isRunning()]

   @staticmethod
   def frequency(frequency, start, duration, velocity=100, channel=0, panning = -1):
      """Plays a frequency with given 'start' time (in milliseconds from now), 'duration' (in milliseconds
         from 'start' time), with given 'velocity' on 'channel'.  Default panning of -1 means to
         use the default (global) panning setting of the Java synthesizer."""

      # NOTE:  We assume that the end-user will ensure that concurrent microtones end up on
      # different channels.  This is needed since MIDI has only one pitch band per channel,
      # and most microtones require their unique pitch bending.

      # check for negative start times
      if start < 0:
         print(f'Play.frequency(): Start time must be non-negative, got {start}')
         return

      # ensure duration is a positive number
      if duration <= 0:
         print(f'Play.frequency(): Duration must be positive, got {duration}')
         return

      # Store the Timer objects in a list - this prevents them from being garbage collected
      # before they execute
      global _NOTE_TIMERS

      # create a timer for the frequency-on event
      frequencyOn = Timer(start, Play.frequencyOn, [frequency, velocity, channel, panning], False)

      # create a timer for the frequency-off event
      frequencyOff = Timer(start+duration, Play.frequencyOff, [frequency, channel], False)

      # store timers to prevent garbage collection
      _NOTE_TIMERS.append(frequencyOn)
      _NOTE_TIMERS.append(frequencyOff)

      # and activate timers (set things in motion)
      frequencyOn.start()
      frequencyOff.start()

      # We'll clean up _NOTE_TIMERS periodically to avoid memory leaks
      # Keep only timers that are still running
      _NOTE_TIMERS = [timer for timer in _NOTE_TIMERS if timer.isRunning()]

   # No (normal) pitch bend in JythonMusic (as opposed to MIDI) is 0, max downward bend is -8192, and max upward bend is 8191.
   # (Result is undefined if you exceed these values - it may wrap around or it may cap.)
   @staticmethod
   def setPitchBend(bend = 0, channel=0):
      """Set global pitchbend variable to be used when a note / frequency is played."""

      if (bend <= OUR_PITCHBEND_MAX) and (bend >= OUR_PITCHBEND_MIN):   # is pitchbend within appropriate range?
         _currentPitchbend[channel] = bend        # remember the pitch bend (e.g., for Play.noteOn() )

         _MIDI_SYNTH.pitchbend(channel, bend)  # set pitchbend on synthesizer

      else:     # frequency was outside expected range
         print(f'Play.setPitchBend(): Invalid pitchbend {bend}, expected pitchbend in range {OUR_PITCHBEND_MIN} to {OUR_PITCHBEND_MAX}.')

   @staticmethod
   def getPitchBend(channel=0):
      """
      Returns the current pitchbend for this channel.
      """
      return _currentPitchbend[channel]

   @staticmethod
   def noteOnPitchBend(pitch, bend=0, velocity=100, channel=0, panning = -1):
      """
      Send a NOTE_ON message for this pitch to the synthesizer object.
      Default panning of -1 means to use the default (global) panning setting of the
      synthesizer.
      """

      # check if pitch bend is within expected range
      if OUR_PITCHBEND_MIN <= bend <= OUR_PITCHBEND_MAX:

         # we are OK, so set pitchbend on the synthesizer!
         Play.setPitchBend(bend, channel)

         # then, also send message to start the note on this channel
         if panning != -1:                  # if we have a specific panning...
            Play.setPanning(panning, channel)  # set it

         noteID = (pitch, channel)
         # check number of overlapping notes
         global _activeNotes
         _activeNotes[noteID] = _activeNotes.get(noteID, 0) + 1
         _MIDI_SYNTH.noteon(channel, pitch, velocity)   # start the note on synthesizer

      else:     # bend was outside expected range
         error_msg = f'Play.noteOn(): Invalid pitchbend {bend}, expected pitchbend in range {OUR_PITCHBEND_MIN} to {OUR_PITCHBEND_MAX}. Perhaps reset global pitch bend via Play.setPitchBend(0)... ?'
         print(error_msg)

   @staticmethod
   def allNotesOff():
      """Turns off all notes on all channels."""
      global _MIDI_SYNTH

      # use TinySoundFont to directly stop all notes on all channels
      for channel in range(16):  # MIDI has 16 channels
         _MIDI_SYNTH.notes_off(channel)

   @staticmethod
   def allFrequenciesOff():
      """Turns off all notes on all channels."""
      # Since frequencies are also represented as notes in MIDI,
      # we can reuse the allNotesOff implementation.
      Play.allNotesOff()

   @staticmethod
   def stop(): # TODO: is this correct?
      """Stops all Play music from sounding."""
      Play.allNotesOff()

      # also stop all audio samples
      for sample in _activeAudioSamples:
         sample.stop()

   @staticmethod
   def setInstrument(instrument, channel=0):
      """Send a patch change message for this channel to the synthesizer object."""
      _currentInstrument[channel] = instrument     # remember instrument
      if channel == 9:   # special handling for percussion channel
         _MIDI_SYNTH.program_select(channel, _SOUNDFONT, 0, instrument, is_drums=True)
      else:
         _MIDI_SYNTH.program_change(channel, instrument)  # set instrument on synthesizer

   @staticmethod
   def getInstrument(channel=0):
      """Gets the current instrument for this channel of the synthesizer object."""
      return _currentInstrument[channel]

   @staticmethod
   def setVolume(volume, channel=0):
      """Sets the current coarse volume for this channel to the synthesizer object."""
      _currentVolume[channel] = volume     # remember volume
      _MIDI_SYNTH.control_change(channel, 7, volume)  # set volume on synthesizer

   @staticmethod
   def getVolume(channel=0):
      """Gets the current coarse volume for this channel of the synthesizer object."""
      return _currentVolume[channel]

   @staticmethod
   def setPanning(panning, channel=0):
      """Sets the current panning setting for this channel to the synthesizer object."""
      _currentPanning[channel] = panning     # remember panning
      _MIDI_SYNTH.control_change(channel, 10, panning)  # set panning on synthesizer

   @staticmethod
   def getPanning(channel=0):
      """Gets the current panning setting for this channel of the synthesizer object."""
      return _currentPanning[channel]

   # TODO: come back to these audio functions after AudioSample class is implemented
   @staticmethod
   def audio(material, audioSamples, loopFlags, envelopes):
      """Play material using a list of audio samples as voices"""

      # do necessary datatype wrapping (MidiSynth() expects a Score)
      if type(material) == Note:
         material = Phrase(material)
      if type(material) == Phrase:   # no elif - we need to successively wrap from Note to Score
         material = Part(material)
      if type(material) == Part:     # no elif - we need to successively wrap from Note to Score
         material = Score(material)
      if type(material) == Score:

         # we are good - let's play it then!

         score = material   # by now, material is a score, so create an alias (for readability)

         # loop through all parts and phrases to get all notes
         noteList = []               # holds all notes
         tempo = score.getTempo()    # get global tempo (can be overidden by part and phrase tempos)
         for part in score.getPartList():   # traverse all parts
            # NOTE: channel is used as an index for the audio voice
            channel = part.getChannel()        # get part channel
            instrument = part.getInstrument()  # get part instrument
            if part.getTempo() > -1:           # has the part tempo been set?
               tempo = part.getTempo()            # yes, so update tempo
            for phrase in part.getPhraseList():   # traverse all phrases in part
               if phrase.getInstrument() > -1:        # is this phrase's instrument set?
                  instrument = phrase.getInstrument()    # yes, so it takes precedence
               if phrase.getTempo() > -1:          # has the phrase tempo been set?
                  tempo = phrase.getTempo()           # yes, so update tempo

               # time factor to convert time from jMusic Score units to milliseconds
               # (this needs to happen here every time, as we may be using the tempo from score, part, or phrase)
               FACTOR = 1000 * 60.0 / tempo

               for index in range(phrase.getSize()):      # traverse all notes in this phrase
                  note = phrase.getNote(index)              # and extract needed note data
                  frequency = note.getFrequency()
                  panning = note.getPan()
                  panning = mapValue(panning, 0.0, 1.0, 0, 127)    # map from range 0.0..1.0 (Note panning) to range 0..127 (as expected by Java synthesizer)
                  start = int(phrase.getNoteStartTime(index) * FACTOR)  # get time and convert to milliseconds

                  # NOTE:  Below we use note length as opposed to duration (getLength() vs. getDuration())
                  # since note length gives us a more natural sounding note (with proper decay), whereas
                  # note duration captures the more formal (printed score) duration (which sounds unnatural).
                  duration = int(note.getLength() * FACTOR)             # get note length (as oppposed to duration!) and convert to milliseconds
                  velocity = note.getDynamic()

                  # accumulate non-REST notes
                  if (frequency != REST):
                     noteList.append((start, duration, frequency, velocity, channel, instrument, panning))   # put start time first and duration second, so we can sort easily by start time (below),
                     # and so that notes that are members of a chord as denoted by having a duration of 0 come before the note that gives the specified chord duration

         # sort notes by start time
         noteList.sort()

         # Schedule playing all notes in noteList
         chordNotes = []      # used to process notes belonging in a chord
         for start, duration, pitch, velocity, channel, instrument, panning in noteList:
            # *** not needed, since we are using audio to play back music (was: set appropriate instrument for this channel)
            #Play.setInstrument(instrument, channel)

            # handle chord (if any)
            # Chords are denoted by a sequence of notes having the same start time and 0 duration (except the last note
            # of the chord).
            if duration == 0:   # does this note belong in a chord?
               chordNotes.append([start, duration, pitch, velocity, channel, panning])  # add it to the list of chord notes

            elif chordNotes == []:   # is this a regular, solo note (not part of a chord)?

               # TODO: list of envelopes was in JythonMusic, but not even defined there.
               # # yes, so schedule it to play via a Play.audioNote event
               # if listOfEnvelopes:
               #    Play.audioNote(pitch, start, duration, audioSamples[channel], velocity, panning, loopFlags[channel], envelopes[channel])
               Play.audioNote(pitch, start, duration, audioSamples[channel], velocity, panning)
               #***print "Play.note(" + str(pitch) + ", " + str(int(start * FACTOR)) + ", " + str(int(duration * FACTOR)) + ", " + str(velocity) + ", " + str(channel) + ")"

            else:   # note has a normal duration and it is part of a chord

               # first, add this note together with this other chord notes
               chordNotes.append([start, duration, pitch, velocity, channel, panning])

               # now, schedule all notes in the chord list using last note's duration
               for start, ignoreThisDuration, pitch, velocity, channel, panning in chordNotes:
                  # schedule this note using chord's duration (provided by the last note in the chord)
                  # TODO: JythonMusic checked listOfEnvolopes here, but it wasn't even defined?
                  # if listOfEnvelopes:   # have they provided a list of envelopes
                  #    Play.audioNote(pitch, start, duration, audioSamples[channel], velocity, panning, loopFlags[channel], envelopes[channel])
                  # else:
                  Play.audioNote(pitch, start, duration, audioSamples[channel], velocity, panning)

                  #***print "Chord: Play.note(" + str(pitch) + ", " + str(int(start * FACTOR)) + ", " + str(int(duration * FACTOR)) + ", " + str(velocity) + ", " + str(channel) + ")"
               # now, all chord notes have been scheduled

               # so, clear chord notes to continue handling new notes (if any)
               chordNotes = []

         # now, all notes have been scheduled for future playing - scheduled notes can always be stopped using
         # JEM's stop button - this will stop all running timers (used by Play.note() to schedule playing of notes)
         #print "Play.note(" + str(pitch) + ", " + str(int(start * FACTOR)) + ", " + str(int(duration * FACTOR)) + ", " + str(velocity) + ", " + str(channel) + ")"

      else:   # error check
         print(f"Play.audio(): Unrecognized type {type(material)}, expected Note, Phrase, Part, or Score.")

   @staticmethod
   def audioNote(pitch, start, duration, audioSample, velocity = 127, panning = -1, loopAudioSample = False, envelope = None):
      """Play a note using an AudioSample for generating the sound."""

      # *** do more testing here

      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # yes, so convert pitch from MIDI number (int) to Hertz (float)
         pitch = noteToFreq(pitch)

      # create timers for note-on and note-off events
      audioOn  = Timer(start, Play.audioOn, [pitch, audioSample, velocity, panning, loopAudioSample, envelope], False)
      audioOff = Timer(start + duration, Play.audioOff, [pitch, audioSample, envelope], False)

      # everything is ready, so start timers to schedule playing of note
      audioOn.start()
      audioOff.start()

   #def audioOn(pitch, audioSample, velocity = 127, panning = -1, envelope = None, loopAudioSample = False):   #***
   @staticmethod
   def audioOn(pitch, audioSample, velocity = 127, panning = -1, loopAudioSample = False, envelope = None):
      """ Start playing a specific pitch at a given volume using provided audio sample. """

      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # yes, so convert pitch from MIDI number (int) to Hertz (float)
         pitch = noteToFreq(pitch)

      if type(pitch) == float:        # a pitch in Hertz?

         # all good, so play it

         # allocate a AudioSample voice to play this pitch
         voice = audioSample.allocateVoiceForPitch(pitch)

         if voice == None:   # is there an available voice?

            print(f"Play.audioOn(): AudioSample does not have enough free voices to play this pitch, {pitch}.")

         else:   # we have a voice to play this pitch, so do it!!!

            # let's start the sound

            if panning != -1:                              # if we have a specific panning...
               audioSample.setPanning(panning, voice)         # then, use it (otherwise let default / global panning stand
            else:                                          # otherwise...
               audioSample.setPanning( Play.getPanning(), voice )   # use the global / default panning

            audioSample.setFrequency(pitch, voice)         # set the sample to the specified frequency

            if envelope:   # do we have an envelope to apply?

               # schedule volume changes needed to apply this envelope
               envelope.performAttackDelaySustain(audioSample, velocity, voice)

            else:   # no envelope, so...

               # set volume right away, as specified
               audioSample.setVolume(volume = velocity, voice = voice)         # and specified volume

            # ready - let make some sound!!!
            if loopAudioSample:

               audioSample.loop(start=0, size=-1, voice=voice)   # loop it continuously (until the end of the note)

            else:

               audioSample.play(start=0, size=-1, voice=voice)   # play it just once, and stop (even if before the end of the note)

      else:

         print(f"Play.audioNoteOn(): Unrecognized pitch {pitch}, expected MIDI pitch from 0 to 127 (int), or frequency in Hz from 8.17 to 12600.0 (float).")

   @staticmethod
   def audioOff(pitch, audioSample, envelope = None):
      """ Stop playing the specified pitch on the provided audio sample. """

      if (type(pitch) == int) and (0 <= pitch <= 127):   # a MIDI pitch?
         # yes, so convert pitch from MIDI number (int) to Hertz (float)
         pitch = noteToFreq(pitch)

      if type(pitch) == float:        # a pitch in Hertz?

         # all good, so stop it

         voice = audioSample.getVoiceForPitch(pitch)   # find which voice is being used to play this pitch

         if voice != None:   # if a voice was associated with this pitch (as opposed to None) - meaning that this pitch was sounding...

            if envelope:   # if there is an envelope to apply...

               # release sound and stop, as prescribed by this envelope
               envelope.performReleaseAndStop(audioSample, voice)

            else:   # no envelope, so...

               # stop sound right away
               audioSample.stop(voice)

            # now, return the voice back to the pool of free voices (to potentially be used to play other notes)
            audioSample.deallocateVoiceForPitch(pitch)

         #else:
         #
         #  Could output a warning that this pitch is not playing, but let's be silent - better for live coding performances...
         #

      else:
         print(f"Play.audioNoteOff(): Unrecognized pitch {pitch}, expected MIDI pitch from 0 to 127 (int), or frequency in Hz from 8.17 to 12600.0 (float).")

   @staticmethod
   def allAudioNotesOff():
      """Turns off all notes on all audio samples."""

      # stop all notes from all active AudioSamples
      for a in _activeAudioSamples:

         # stop all voices for this AudioSample
         for voice in range(a.maxVoices):
            a.stop(voice)    # no need to check if they are playing - just do it (it's fine)

      # NOTE: One possibility here would be to also handle scheduled notes through Play.audio().  This could be done
      # by creating a list of AudioSamples and Timers created via audioNote() and looping through them to stop them.
      # For now, it makes sense to keep separate Play.audio() activity (which is score based), and Live Coding activity
      # i.e., interactively playing AudioSamples.

   @staticmethod
   def code(material, functions):
      """Use transcription material (Score, Part, Phrase, Note) to trigger execution of arbitrary Python functions.
         Parameter 'functions' is a list of functions (at least one, for channel 0), where index corresponds to channel
         (i.e., channel of note being "played" determines which function to call).
      """

      # do necessary datatype wrapping (MidiSynth() expects a Score)
      if isinstance(material, Note):
         material = Phrase(material)
      if isinstance(material, Phrase):   # no elif - we need to successively wrap from Note to Score
         material = Part(material)
         material.setInstrument(-1)     # indicate no default instrument (needed to access global instrument)
      if isinstance(material, Part):     # no elif - we need to successively wrap from Note to Score
         material = Score(material)
      if isinstance(material, Score):
         # we are good - let's play it then!

         score = material   # by now, material is a score, so create an alias (for readability)

         # loop through all parts and phrases to get all notes
         noteList = []               # holds all notes
         tempo = score.getTempo()    # get global tempo (can be overidden by part and phrase tempos)
         for part in score.getPartArray():   # traverse all parts
            channel = part.getChannel()        # get part channel
            instrument = Play.getInstrument(channel)  # get global instrument for this channel
            if part.getInstrument() > -1:      # has the part instrument been set?
               instrument = part.getInstrument()  # yes, so it takes precedence
            if part.getTempo() > -1:           # has the part tempo been set?
               tempo = part.getTempo()            # yes, so update tempo
            for phrase in part.getPhraseArray():   # traverse all phrases in part
               if phrase.getInstrument() > -1:        # is this phrase's instrument set?
                  instrument = phrase.getInstrument()    # yes, so it takes precedence
               if phrase.getTempo() > -1:          # has the phrase tempo been set?
                  tempo = phrase.getTempo()           # yes, so update tempo

               # time factor to convert time from Score units to milliseconds
               # (this needs to happen here every time, as we may be using the tempo from score, part, or phrase)
               FACTOR = 1000 * 60.0 / tempo

               for index in range(phrase.length()):      # traverse all notes in this phrase
                  note = phrase.getNote(index)              # and extract needed note data
                  frequency = note.getFrequency()
                  panning = note.getPan()
                  panning = mapValue(panning, 0.0, 1.0, 0, 127)    # map from range 0.0..1.0 (Note panning) to range 0..127 (as expected by Java synthesizer)
                  start = int(phrase.getNoteStartTime(index) * FACTOR)  # get time and convert to milliseconds

                  # NOTE:  Below we use note length as opposed to duration (getLength() vs. getDuration())
                  # since note length gives us a more natural sounding note (with proper decay), whereas
                  # note duration captures the more formal (printed score) duration (which sounds unnatural).
                  duration = int(note.getLength() * FACTOR)             # get note length (as oppposed to duration!) and convert to milliseconds
                  velocity = note.getDynamic()

                  # accumulate non-REST notes
                  # if (frequency != REST):
                  #    noteList.append((start, duration, frequency, velocity, channel, instrument, panning))   # put start time first and duration second, so we can sort easily by start time (below),
                     # and so that notes that are members of a chord as denoted by having a duration of 0 come before the note that gives the specified chord duration

                  # since they may want to give special meaning to REST notes, accumulate all notes (including RESTs)
                  # NOTE:  This is different from play.midi() and play.audio()
                  noteList.append((start, duration, frequency, velocity, channel, instrument, panning))   # put start time first and duration second, so we can sort easily by start time (below),

         # sort notes by start time
         noteList.sort()

         # schedule playing all notes in noteList
         chordNotes = []      # used to process notes belonging in a chord
         for start, duration, frequency, velocity, channel, instrument, panning in noteList:
            # set appropriate instrument for this channel
            #Play.setInstrument(instrument, channel)

            # handle chord (if any)
            # Chords are denoted by a sequence of notes having the same start time and 0 duration (except the last note
            # of the chord).
            if duration == 0:   # does this note belong in a chord?
               chordNotes.append([start, duration, frequency, velocity, channel, instrument, panning])  # add it to the list of chord notes

            elif chordNotes == []:   # is this a regular, solo note (not part of a chord)?

               # yes, so schedule to execute the corresponding function for this note

               # extract function associated with this channel
               if len(functions) > channel:   # is there a function associated with this channel?

                  # create timer to call this function
                  function = functions[channel]
                  functionTimer = Timer(start, function, [frequency, start, duration, velocity, channel, instrument, panning], False)
                  functionTimer.start()

               else:   # no, there isn't, so let them know

                  print(f"Play.code(): No function provided for channel {channel}.")

               #print "Play.note(" + str(frequency) + ", " + str(int(start * FACTOR)) + ", " + str(int(duration * FACTOR)) + ", " + str(velocity) + ", " + str(channel) + ")"

            else:   # note has a normal duration and it is part of a chord

               # first, add this note together with this other chord notes
               chordNotes.append([start, duration, frequency, velocity, channel, instrument, panning])

               # now, schedule all notes in the chord list using last note's duration
               for start, ignoreThisDuration, frequency, velocity, channel, instrument, panning in chordNotes:
                  # schedule to execute the corresponding function for this note

                  # extract function associated with this channel
                  if len(functions) > channel:   # is there a function associated with this channel?

                     # create timer to call this function
                     function = functions[channel]
                     functionTimer = Timer(start, function, [frequency, start, duration, velocity, channel, instrument, panning], False)
                     functionTimer.start()

                  else:   # no, there isn't, so let them know
                     print(f"Play.code(): No function provided for channel {channel}.")

               # now, all chord notes have been scheduled

               # so, clear chord notes to continue handling new notes (if any)
               chordNotes = []

         # now, all notes have been scheduled for future playing - scheduled notes can always be stopped using
         # JEM's stop button - this will stop all running timers

      else:   # error check
         print(f"Play.code(): Unrecognized type {type(material)}, expected Note, Phrase, Part, or Score.")

#######################################################################################
#### Mod ##############################################################################
#######################################################################################
class Mod():

   @staticmethod
   def accent(material, meter, accentedBeats={0.0}, accentAmount=20):
      """Accents by accentAmount at the accentedBeats locations."""

      # define helper functions
      def accentPhrase(phrase):
         """Helper function to accent a single phrase."""

         beatCounter = phrase.getStartTime()

         # for every note in phrase...
         for note in phrase.getNoteList():

            # check note against each accented beat
            for beat in accentedBeats:

               # if note occurs on accented beat, increase dynamic level
               if beatCounter % meter == beat:
                  tempDynamic = note.getDynamic() + accentAmount
                  note.setDynamic(tempDynamic)

            # update current beat count
            beatCounter += note.getDuration()

      def accentPart(part):
         """Helper function to accent a single part."""

         for phrase in part.getPhraseList():
            accentPhrase(phrase)

      def accentScore(score):
         """Helper function to accent a single score."""

         for part in score.getPartList():
            accentPart(part)

      # do some basic error checking
      if float(meter) <= 0.0:
         raise TypeError(f"Expected meter greater than 0.0 - (it was {meter}).")

      for accentedBeat in accentedBeats:
         if not 0.0 <= float(accentedBeat) < float(meter):
            raise ValueError(f"Expected accented beat between 0.0 and {meter} - (it was {accentedBeat}).")

      if type(material) is Score:
         accentScore(material)

      elif type(material) is Part:
         accentPart(material)

      elif type(material) is Phrase:
         accentPhrase(material)

      else:
         raise TypeError(f"Unrecognized material type {type(material)} - expected Phrase, Part, or Score.")

   @staticmethod
   def append(material1, material2):
      """Appends material1 to material2."""

      if type(material1) is Note and type(material2) is Note:
         material1.setDuration(material1.getDuration() + material2.getDuration())

      elif type(material1) is Phrase and type(material2) is Phrase:
         for note in material2.getNoteList():
            material1.addNote(note.copy())

      elif type(material1) is Part and type(material2) is Part:
         for phrase in material2.getPhraseList():
            material1.addPhrase(phrase.copy())

      elif type(material1) is Score and type(material2) is Score:
         endTime = material1.getEndTime()

         for part in material2.copy().getPartList():
            for phrase in part.getPhraseList():
               if phrase.getNoteList():
                  phrase.setStartTime(phrase.getStartTime() + endTime)
                  phrase.setInstrument(-1)

            material1.addPart(part)

      else:
         raise TypeError(f"Expected arguments of the same type - (it was {type(material1)} and {type(material2)})")

   @staticmethod
   def bounce(material):
      """Adjusts the pan values of all notes in material to alternate between extreme left and right from note to note."""

      # define helper functions
      def bouncePhrase(phrase):
         """Helper function to bounce a single phrase."""

         newPan = 0.0
         panIncrement = 1.0

         # for every note in phrase...
         for note in phrase.getNoteList():
            note.setPan(newPan)            # set panning
            pan += panIncrement         # increment panning value
            panIncrement *= -1          # alternate panning increment

      def bouncePart(part):
         """Helper function to bounce a single part."""

         for phrase in part.getPhraseList():
            bouncePhrase(phrase)

      def bounceScore(score):
         """Helper function to bounce a single score."""

         for part in score.getPartList():
            bouncePart(part)

      if type(material) is Score:
         bounceScore(material)

      elif type(material) is Part:
         bouncePart(material)

      elif type(material) is Phrase:
         bouncePhrase(material)

      else:
         raise TypeError(f"Unrecognized material type {type(material)} - expected Phrase, Part, or Score.")

   @staticmethod
   def changeLength(phrase, newLength):
      """Alters the phrase so that it's notes are stretched or compressed until the phrase is the length specified."""

      # do some basic error checking
      if float(newLength) <= 0.0:
         raise TypeError(f"Expected newLength greater than 0.0 - (it was {newLength}).")

      if type(phrase) is not Phrase:
         raise TypeError(f"Unrecognized material type {type(phrase)} - expected Phrase.")

      oldLength = phrase.getEndTime() - phrase.getStartTime()
      Mod.elongate(phrase, newLength / oldLength)

   @staticmethod
   def compress(material, ratio):
      """Compresses (or expands) the material."""

      # define helper functions
      def compressPhrase(phrase):
         """Helper function to compress a single phrase."""

         min = float(-math.inf)
         max = float(math.inf)

         for note in phrase.getNoteList():
            min = min(min, note.getDynamic())
            max = max(max, note.getDynamic())

         mean = (min + max) / 2

         for note in phrase.getNoteList():
            newDyn = round(mean + ((note.getDynamic() - mean) * ratio))
            note.setDynamic(newDyn)

      def compressPart(part):
         """Helper function to compress a single part."""

         accum = 0
         counter = 0

         for phrase in part.getPhraseList():
            for note in phrase.getNoteList():
               if note.getPitch != REST:
                  accum += note.getDynamic()
                  counter += 1

         mean = round(accum / counter)

         for phrase in part.getPhraseList():
            for note in phrase.getNoteList():
               newDyn = round(mean + ((note.getDynamic() - mean) * ratio))
               note.setDynamic(newDyn)

      def compressScore(score):
         """Helper function to compress a single score."""

         for part in score.getPartList():
            compressPart(part)

      # do some basic error checking
      if type(material) is Phrase:
         compressPhrase(material)

      elif type(material) is Part:
         compressPart(material)

      if type(material) is Score:
         compressScore(material)

      else:
         raise TypeError(f"Unrecognized material type {type(material)} - expected Phrase, Part, or Score.")

   @staticmethod
   def consolidate(part):
      """Joins all of the phrases within this part into a single phrase"""

      # do some basic error checking
      if type(part) is not Part:
         raise TypeError(f"Unrecognized material type {type(part)} - expected Part.")

      part.__str__()

      prevsst = part.getStartTime()   # previous smallest start time (start of part)
      finished = False                # are we done consolidating?

      newPhrase = Phrase()

      while not finished:
         sst = float(math.inf)    # smallest start time (initialized to big number)
         tempPhrase = None

         # get phrase with earliest start time
         for phrase in part.getPhraseList():
            if phrase.getStartTime() < sst and phrase.getSize() > 0:
               tempPhrase = phrase
               sst = phrase.getStartTime()

         if tempPhrase is None:
            finished = True
            break

         note = tempPhrase.getNote(0)        # get next note from phrase

         if not note.isRest():

            if newPhrase.getSize() == 0:        # if this is the first note
               newPhrase.setStartTime(sst)

            else:                               # if this is not the first note
               newDuration = int(((sst - prevsst) * 100000) + 0.5) / 100000.0          # calculate new duration for previous note
               newPhrase.getNote(newPhrase.getSize() - 1).setDuration(newDuration)     # update previous note's duration

            newPhrase.addNote(note)

         tempPhrase.removeNote(0)    # remove note from phrase

         newStartTime = int(((sst + note.getDuration()) * 100000) + 0.5) / 100000.0      # calculate new start time for phrase
         tempPhrase.setStartTime(newStartTime)                                           # update phrase's start time

         prevsst = sst               # update previou smallest start time

      part.empty()
      part.addPhrase(newPhrase)

   @staticmethod
   def cycle(phrase, numberOfNotes):
      """Repeats the material until it contains the specified number of notes."""

      # do some basic error checking
      if type(phrase) is not Phrase:
         raise TypeError(f"Unrecognized material type {type(phrase)} - expected Phrase.")
      elif type(numberOfNotes) is not int:
         raise TypeError(f"Unexpected times type {type(numberOfNotes)} - expected int.")
      elif numberOfNotes <= phrase.getSize():
         raise ValueError("numberOfNotes should be greater than phrase size.")

      # for each additional note needed...
      for i in range(0, numberOfNotes - phrase.getSize()):

            noteCopy = phrase.getNote(i).copy()     # copy next note in sequence
            phrase.addNote(noteCopy)                # add note to end of phrase

   @staticmethod
   def elongate(material, scaleFactor):
      """
      Elongates the material by scaleFactor.
      material:    Score, Part, Phrase, or Note
      scaleFactor: float > 0.0
      """

      # do some basic error checking
      if not isinstance(material, (Score, Part, Phrase, Note)):
         raise TypeError(f'Mod.elongate(): material must be a Score, Part, Phrase, or Note - (it was {type(material)}).')
      if not isinstance(scaleFactor, (int, float)):
         raise TypeError(f'Mod.elongate(): scaleFactor must be a number - (it was {type(scaleFactor)}).')
      if scaleFactor <= 0.0:
         raise ValueError(f'Mod.elongate(): scaleFactor must be greater than 0.0 - (it was {scaleFactor}).')

      # define helper functions
      def elongateNote(note, scaleFactor):
         note.setDuration(note.getDuration() * scaleFactor)  # elongate note

      def elongatePhrase(phrase, scaleFactor):
         for note in phrase.getNoteList():
            elongateNote(note, scaleFactor)

      def elongatePart(part, scaleFactor):
         for phrase in part.getPhraseList():
            elongatePhrase(phrase, scaleFactor)

      def elongateScore(score, scaleFactor):
         for part in score.getPartList():
            elongatePart(part, scaleFactor)

      # do the work
      if isinstance(material, Score):
         elongateScore(material, scaleFactor)
      elif isinstance(material, Part):
         elongatePart(material, scaleFactor)
      elif isinstance(material, Phrase):
         elongatePhrase(material, scaleFactor)
      elif isinstance(material, Note):
         elongateNote(material, scaleFactor)


   @staticmethod
   def fadeIn(material, fadeLength):
      """Linearly fades in the material (fadeLength is quarter notes)."""

      # define helper functions
      def fadeInPhrase(phrase, startTime=0.0):
         """Helper function to fadeIn a single phrase."""

         durationCounter = startTime                     # track how far into piece we are

         # for each note in phrase
         for note in phrase.getNoteList():
            fadeFactor = durationCounter / fadeLength           # calculate fraction of fading needed

            if fadeFactor >= 1:                                 # check if fade is over
               break

            newDynamic = note.getDynamic() * fadeFactor         # calculate new faded dynamic
            newDynamic = max(1, newDynamic)                     # keep dynamic above 0

            note.setDynamic(int(newDynamic))                    # update note dynamic

            durationCounter += note.getDuration()               # update time tracker

      def fadeInPart(part, startTime=0.0):
         """Helper function to fadeIn a single part."""

         for phrase in part.getPartList():
            fadeInPart(phrase, startTime + phrase.getStartTime())

      def fadeInScore(score):
         """Helper function to fadeIn a score."""

         for part in score.getPartList():
            fadeInPart(part, part.getStartTime())

      # check type of time
      if type(fadeLength) not in [float, int]:
         raise TypeError(f"Unrecognized fadeLength type {type(fadeLength)} - expected int or float.")

      # check type of material and call the appropriate function
      if type(material) == Score:
         fadeInScore(material)

      elif type(material) == Part:
         fadeInPart(material)

      elif type(material) == Phrase:
         fadeInPhrase(material)

      else:   # error check
         raise TypeError(f"Unrecognized material type {type(material)} - expected Phrase, Part, or Score.")

   @staticmethod
   def fadeOut(material, fadeLength):
      """Linearly fades out the material (fadeLength is quarter notes)."""

      # define helper functions
      def fadeOutPhrase(phrase, endTime):
         """Helper function to fadeOut a single phrase."""

         durationCounter = endTime                       # how far from the end are we?

         # for each note in phrase, starting from end
         for note in phrase.getNoteList()[::-1]:
               fadeFactor = durationCounter / fadeLength           # calculate fraction of fading needed

               if fadeFactor >= 1:                                 # check if fade is over
                  break

               newDynamic = note.getDynamic() * fadeFactor         # calculate new faded dynamic
               newDynamic = max(1, newDynamic)                     # keep dynamic above 0

               note.setDynamic(int(newDynamic))                    # update note dynamic

               durationCounter += note.getDuration()               # update time tracker

      def fadeOutPart(part, endTime):
         """Helper function to fadeOut a single part."""

         for phrase in part.getPartList():
            fadeOutPart(phrase, endTime  - phrase.getEndTime())

      def fadeOutScore(score):
         """Helper function to fadeOut a score."""

         for part in score.getPartList():
               fadeOutPart(part, score.getEndTime() - part.getEndTime())

         # check type of time
         if type(fadeLength) not in [float, int]:
            raise TypeError(f"Unrecognized fadeLength type {type(fadeLength)} - expected int or float.")

         # check type of material and call the appropriate function
         if type(material) == Score:
            fadeOutScore(material)

         elif type(material) == Part:
            fadeOutPart(material, 0.0)

         elif type(material) == Phrase:
            fadeOutPhrase(material, 0.0)

         else:   # error check
            raise TypeError(f"Unrecognized material type {type(material)} - expected Phrase, Part, or Score.")

   @staticmethod
   def fillRests(material):
      """Lengthens notes followed by a rest in the phrase by creating one longer note and deleting the rest."""

      # define helper functions
      def fillPhrase(phrase):
         """Helper function to fill rests in a phrase."""

         index = phrase.getSize() - 2
         while index > -1:
            currNote = phrase.getNote(index)
            nextNote = phrase.getNote(index + 1)

            if currNote.getPitch() != REST == nextNote.getPitch():

               newDuration = currNote.getDuration() + nextNote.getDuration()
               currNote.setDuration(newDuration)

               phrase.removeNote(index + 1)

               index -= 1

      def fillPart(part):
         """Helper function to fill rests in a part."""

         for phrase in part.getPhraseList():
               fillPhrase(phrase)

      def fillScore(score):
         """Helper function to fill rests in a score."""

         for part in score.getPartList():
            fillPart(part)

      # check type of material and call the appropriate function
      if type(material) == Score:
         fillScore(material)

      elif type(material) == Part:
         fillPart(material)

      elif type(material) == Phrase:
         fillPhrase(material)

      else:   # error check
         raise TypeError(f"Unrecognized material type {type(material)} - expected Phrase, Part, or Score.")

   @staticmethod
   def invert(phrase, pitchAxis):
      """
      Invert phrase using pitch as the mirror (pivot) axis.
      phrase:    Phrase to invert
      pitchAxis: Pitch axis to pivot around (0-127)
      """

      # do some basic error checking
      if type(pitchAxis) is not int:
         raise TypeError(f"Unrecognized pitchAxis type {type(pitchAxis)} - expected int.")
      if type(phrase) is not Phrase:
         raise TypeError(f"Unrecognized material type {type(phrase)} - expected Phrase.")
      # traverse list of notes, and adjust pitches accordingly
      for note in phrase.getNoteList():

         if not note.isRest():  # modify regular notes only (i.e., do not modify rests)
            invertedPitch = pitchAxis + (pitchAxis - note.getPitch())   # find mirror pitch around axis (by adding difference)
            note.setPitch(invertedPitch)                                # and update it

      # now, all notes have been updated

   @staticmethod
   def merge(material1, material2):
      """
      Merges material2 into material1 - material1 is modified to include material2.
      Instrument and channel assignments aren't checked - it is up to the user to
      ensure that they are compatible.
      material1: Part or Score
      material2: Part or Score (same as material1)
      """
      # do some basic error checking
      if not isinstance(material1, (Part, Score)):
         raise TypeError(f"Mod.merge(): material1 must be a Part or Score - (it was {type(material1)}).")
      if not (type(material1) == type(material2)):
         raise TypeError(f"Mod.merge(): material1 and material2 must be the same type - (they were {type(material1)} and {type(material2)}).")

      # define helper functions
      def mergePart(part1, part2):
         """Does the actual merging of two parts."""
         for phrase in part2.getPhraseList():
            part1.addPhrase(phrase.copy())  # copy() to avoid modifying original phrase in material2

      def mergeScore(score1, score2):
         for part in score2.getPartList():
            score1.addPart(part)

      # do the work
      if isinstance(material1, Score):
         mergeScore(material1, material2)
      elif isinstance(material1, Part):
         mergePart(material1, material2)


   @staticmethod
   def mutate(phrase):
      """Mutates the phrase by changing one pitch and one rhythm value."""

      # do some basic error checking
      if type(phrase) is not Phrase:
         raise TypeError("Unrecognized material type " + str(type(phrase)) + " - expected Phrase.")

      # pick random pitch between highest and lowest in phrase
      minPitch = phrase.getLowestPitch()
      maxPitch = phrase.getHighestPitch()
      newPitch = random.randint(minPitch, maxPitch)

      # pick random note in phrase to modify
      note = random.choice(phrase.getNoteList())

      # update pitch for selected note
      note.setPitch(newPitch)

      # pick random duration from phrase note
      durations = [note.getDuration() for note in phrase.getNoteList()]
      newDuration = random.choice(durations)

      # pick random note in phrase to modify
      note = random.choice(phrase.getNoteList())

      # update duration for selected note
      note.setDuration(newDuration)

   @staticmethod
   def normalize(material):
      """Increase note volumes proportionally in material, so the loudest note is at maximum level."""

      maxDynamic = 0

      # check type of material and execute the appropriate code
      if type(material) == Score:

         for part in material.getPartList():
            for phrase in part.getPhraseList():
               for note in phrase.getNoteList():
                  maxDynamic = max(maxDynamic, note.getDynamic)

         diff = 127 - maxDynamic

         for part in material.getPartList():
            for phrase in material.getPhraseList():
               for note in phrase.getNoteList():
                  note.setDynamic(note.getDynamic + diff)

      elif type(material) == Part:

         for phrase in material.getPhraseList():
            for note in phrase.getNoteList():
               maxDynamic = max(maxDynamic, note.getDynamic)

         diff = 127 - maxDynamic

         for phrase in material.getPhraseList():
            for note in phrase.getNoteList():
               note.setDynamic(note.getDynamic + diff)

      elif type(material) == Phrase:

         for note in material.getNoteList():
            maxDynamic = max(maxDynamic, note.getDynamic)

         diff = 127 - maxDynamic

         for note in material.getNoteList():
            note.setDynamic(note.getDynamic + diff)

      else:   # error check
         raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Phrase, Part, or Score." )

   @staticmethod
   def palindrome(material):
      """Extend the material by adding all notes backwards."""

      # check type of material
      if type(material) not in [Phrase, Part, Score]:
            raise TypeError("Unrecognized material type " + str(type(material)) + " - expected Phrase, Part, or Score.")

      # create copy of material to manipulate
      newMaterial = material.copy()

      # reverse new material and shift to end of material
      Mod.retrograde(newMaterial)
      Mod.shift(newMaterial, material.getStartTime())

      # merge new material into original material
      Mod.merge(material, newMaterial)

   @staticmethod
   def quantize(material, quantum, scale=CHROMATIC_SCALE, key=0):
      """Rounds (quantizes) the start time and duration of each note in material to fit multiples of quantum (e.g., 1.0),
         using the specified scale (e.g., MAJOR_SCALE), and the specified tonic (0 means C, 1 means C sharp, 2 means D, and so on)."""

      def quantizeNote(note):
            """Helper function to quantize a note."""

            if note.getPitch() != REST:             # ignore rests

                  interval = note.getPitch() % 12
                  while interval not in scale:        # if pitch is not in the scale...
                     interval -= 1                       # lower pitch by one semitone

                  # calculate new duration as a multiple of quantum
                  newDuration = round(note.getDuration() / quantum) * quantum
                  note.setDuration(newDuration)

      def quantizePhrase(phrase):
         """Helper function to quantize a phrase."""

         for note in phrase.getNoteList():
               quantizeNote(note)

      def quantizePart(part):
         """Helper function to quantize a part."""

         for phrase in part.getPhraseList():
            quantizePhrase(phrase)

      def quantizeScore(score):
         """Helper function to quantize a score."""

         for part in score.getPartList():
            quantizePart(part)

         # check type of steps
         if type(quantum) is not int:
            raise TypeError( "Unrecognized quantum type " + str(type(quantum)) + " - expected int." )

         # check type of material and execute the appropriate code
         if type(material) == Score:
            quantizeScore(material)

         elif type(material) == Part:
            quantizePart(material)

         elif type(material) == Phrase:
            quantizePhrase(material)

         elif type(material) == Note:
            quantizeNote(material)

         else:   # error check
            raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Note, Phrase, Part, or Score." )

   @staticmethod
   def randomize(material, pitchAmount, durationAmount=0, volumeAmount=0):
      """
      Randomizes pitch (and optionally duration and dynamic) of notes in material.
      - material:    Note, Phrase, Part, or Score
      - pitchAmount:    maximum integer variance for pitch randomization (in MIDI pitch)
      - durationAmount: maximum float variance for duration randomization (in seconds)
      - volumeAmount:   maximum integer variance for volume randomization (MIDI 0-127)
      """
      # do some basic error checking
      if not isinstance(material, (Note, Phrase, Part, Score)):
         raise TypeError(f'Mod.randomize(): material must be a Note, Phrase, Part, or Score (it was {type(material)})')
      elif not isinstance(pitchAmount, int):
         raise TypeError(f'Mod.randomize(): steps must be an integer (it was {type(pitchAmount)})')

      # support methods
      def randomizeNote(note):
         """Does the work of randomizing a note."""

         if not note.isRest():  # rests aren't randomizable, so skip the work
            # pitch randomization
            if pitchAmount != 0:
               pitch = note.getPitch()
               pitchShift = random.randint(-pitchAmount, pitchAmount)
               newPitch = min(127, max(0, pitch + pitchShift))  # clamp to 0-127
               note.setPitch(newPitch)

            # duration randomization
            if durationAmount != 0:
               duration = note.getDuration()
               durationShift = random.uniform(-durationAmount, durationAmount)
               newDuration = max(0.01, duration + durationShift)  # don't allow negative durations
               note.setDuration(newDuration)

            # volume randomization
            if volumeAmount != 0:
               volume = note.getDynamic()
               volumeShift = random.randint(-volumeAmount, volumeAmount)
               newVolume = min(127, max(0, volume + volumeShift))  # clamp to 0-127
               note.setDynamic(newVolume)
      ### end randomizeNote()

      def randomizePhrase(phrase):
         for note in phrase.getNoteList():
            randomizeNote(note)

      def randomizePart(part):
         for phrase in part.getPhraseList():
            randomizePhrase(phrase)

      def randomizeScore(score):
         for part in score.getPartList():
            randomizePart(part)

      # time to actually do the work
      if isinstance(material, Score):
         randomizeScore(material)
      elif isinstance(material, Part):
         randomizePart(material)
      elif isinstance(material, Phrase):
         randomizePhrase(material)
      elif isinstance(material, Note):
         randomizeNote(material)


   @staticmethod
   def repeat(material, times):
      """Repeat the material a number of times."""
      times = int(times)

      # check type of times
      if type(times) is not int:
         raise TypeError( "Unrecognized times type " + str(type(times)) + " - expected int." )

      # check type of material and execute the appropriate code
      if type(material) == Score:

         scoreCopy = material.copy()

         for i in range(times):

            newScore = scoreCopy.copy()

            Mod.shift(newScore, material.getEndTime())
            Mod.merge(material, newScore)

      elif type(material) == Part:
         partCopy = material.copy()

         for i in range(times):
            newPart = partCopy.copy()

            Mod.shift(newPart, material.getEndTime())
            Mod.merge(material, newPart)

      elif type(material) == Phrase:

         notes = material.copy().getNoteList()

         for i in range(times):
            for note in notes:
               material.addNote(note)

      else:   # error check
         raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Phrase, Part, or Score." )

   @staticmethod
   def retrograde(material):
      """
      Reverses the start times of notes in the material.
      material: Phrase, Part, or Score (Notes do not have start times)
      """
      # do some basic error checking
      if not isinstance(material, (Phrase, Part, Score)):
         raise TypeError(f'Mod.retrograde(): material must be a Phrase, Part, or Score (it was {type(material)})')

      # define helper functions
      def retrogradePhrase(phrase):
         """Does the work of retrograding."""
         noteList = phrase.copy().getNoteList()  # extract note list
         phrase.empty()                          # clear the phrase

         for note in noteList[::-1]:  # reverse the order of notes
            phrase.addNote(note)      # add them back in reverse order

      def retrogradePart(part):
         partEndTime   = part.getEndTime()

         for phrase in part.getPhraseList():
            retrogradePhrase(phrase)  # reverse the phrase
            # the retrograded phrase needs to start as far from the beginning of the part as
            # the original phrase was from the end of the part
            distanceFromEnd = partEndTime - (phrase.getStartTime() + phrase.getEndTime())
            Mod.shift(phrase, distanceFromEnd)

      def retrogradeScore(score):
         scoreEndTime   = score.getEndTime()

         for part in score.getPartList():
            retrogradePart(part)  # reverse the part
            # the retrograded part needs to start as far from the beginning of the score as
            # the original part was from the end of the score
            distanceFromEnd = scoreEndTime - (part.getStartTime() + part.getEndTime())
            Mod.shift(part, distanceFromEnd)


      # do the work
      if isinstance(material, Score):
         retrogradeScore(material)
      elif isinstance(material, Part):
         retrogradePart(material)
      elif isinstance(material, Phrase):
         retrogradePhrase(material)


   @staticmethod
   def rotate(phrase, times=1):
      """Move the notes around a number of steps, which each step involving the first note becoming the second,
         second the third, and so forth with the last becoming first."""

      # do some basic error checking
      if type(phrase) is not Phrase:
         raise TypeError("Unrecognized material type " + str(type(phrase)) + " - expected Phrase.")
      elif type(times) is not int:
         raise TypeError("Unexpected times type " + str(type(phrase)) + " - expected int.")

      noteList = phrase.getNoteList()
      for i in range(times):
         lastNote = noteList.pop(-1)     # remove last note in phrase
         noteList.insert(0, lastNote)    # prepend it to front of noteList

   @staticmethod
   def shake(material, amount=20):
      """Randomly adjusts the volume of notes to create uneven loudness."""

      # check type of amount
      if type(amount) is not int:
         raise TypeError( "Unrecognized time type " + str(type(amount)) + " - expected int." )

      # define helper functions
      def shakePhrase(phrase):
         """Helper function to shake a phrase."""

         for note in phrase.getNoteList():

            newDynamic = note.getDynamic() + random.randint(-amount, amount)
            newDynamic = max(0, min(newDynamic, 127))

            note.setDynamic(newDynamic)

      def shakePart(part):
         """Helper function to shake a part."""

         for phrase in part.getPhraseList():
            shakePhrase(phrase)

      def shakeScore(score):
         """Helper function to shake a score."""

         for part in score.getPartList():
            shakePart(part)

      # check type of material and execute the appropriate code
      if type(material) == Score:
         shakeScore(material)

      elif type(material) == Part:
         shakePart(material)

      elif type(material) == Phrase:
         shakePhrase(material)

      else:   # error check
         raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Phrase, Part, or Score." )

   @staticmethod
   def shift(material, time):
      """
      Shifts the start time of the material by 'time' (in QN's, i.e. 1.0 is a single QN).
      material: Phrase, Part, or Score (since Notes do not have a start time)
      time:     float or int (positive or negative)
      """
      # do some basic error checking
      if not isinstance(material, (Phrase, Part, Score)):
         raise TypeError(f'Mod.shift(): material must be a Phrase, Part, or Score (it was {type(material)})')
      if not isinstance(time, (int, float)):
         raise TypeError(f'Mod.shift(): time must be a number (it was {type(time)})')

      # define helper functions
      def shiftPhrase(phrase, time):
         """Does the work of shifting a phrase."""
         newStartTime = phrase.getStartTime() + time
         newStartTime = max(0, newStartTime)  # don't allow negative start times
         phrase.setStartTime(newStartTime)

      def shiftPart(part, time):
         for phrase in part.getPhraseList():
            shiftPhrase(phrase, time)

      def shiftScore(score, time):
         for part in score.getPartList():
            shiftPart(part, time)

      # do the work
      if isinstance(material, Score):
         shiftScore(material, time)
      elif isinstance(material, Part):
         shiftPart(material, time)
      elif isinstance(material, Phrase):
         shiftPhrase(material, time)



   @staticmethod
   def shuffle(material):
      """Randomise the order of notes without repeating any note."""

      # define helper functions
      def shufflePhrase(phrase):
         """Helper function to shuffle a phrase."""

         random.shuffle(phrase.getNoteList())

      def shufflePart(part):
         """Helper function to shuffle a part."""

         for phrase in part.getPhraseList():
            shufflePhrase(phrase)

      def shuffleScore(score):
         """Helper function to shuffle a score."""

         for part in score.getPartList():
            shufflePart(part)

      # check type of material and execute the appropriate code
      if type(material) == Score:
         shuffleScore(material)

      elif type(material) == Part:
         shufflePart(material)

      elif type(material) == Phrase:
         shufflePhrase(material)

      else:   # error check
         raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Phrase, Part, or Score." )

   @staticmethod
   def spread(material):
      """Randomly adjusts all Notes' pan value to create an even spread across the stereo spectrum."""

      # define helper functions
      def spreadPhrase(phrase):
         """Helper function to spread a phrase."""

         for note in phrase.getNoteList():
            note.setPan(random())

      def spreadPart(part):
         """Helper function to spread a part."""

         for phrase in part.getPhraseList():
            spreadPhrase(phrase)

      def spreadScore(score):
         """Helper function to spread a score."""

         for part in score.getPartList():
            spreadPart(part)

      # check type of material and execute the appropriate code
      if type(material) == Score:
         spreadScore(material)

      elif type(material) == Part:
         spreadPart(material)

      elif type(material) == Phrase:
         spreadPhrase(material)

      else:   # error check
         raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Phrase, Part, or Score." )

   @staticmethod
   def tiePitches(material):
      """Joins consecutive pitches in material, creating a longer note."""

      # define helper functions
      def tiePhrase(phrase):
         """Helper function to tie pitches in a phrase."""

         index = phrase.getSize() - 2
         while index > -1:

            currNote = phrase.getNote(index)
            nextNote = phrase.getNote(index + 1)

            if currNote.getPitch() == nextNote.getPitch():

               newDuration = currNote.getDuration() + nextNote.getDuration()
               currNote.setDuration(newDuration)

               phrase.removeNote(index + 1)

            index -= 1

      def tiePart(part):
         """Helper function to tie pitches in a part."""

         for phrase in part.getPhraseList():
            tiePhrase(phrase)

      def tieScore(score):
         """Helper function to tie pitches in a score."""

         for part in score.getPartList():
            tiePart(part)

      # check type of material and call the appropriate function
      if type(material) == Score:
         tieScore(material)

      elif type(material) == Part:
         tiePart(material)

      elif type(material) == Phrase:
         tiePhrase(material)

      else:   # error check
         raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Phrase, Part, or Score." )

   @staticmethod
   def tieRests(material):
      """Joins consecutive rests in material, creating a longer note."""

      # define helper functions
      def tiePhrase(phrase):
         """Helper function to tie rests in a phrase."""

         index = phrase.getSize() - 2
         while index > -1:

               currNote = phrase.getNote(index)
               nextNote = phrase.getNote(index + 1)

               if currNote.getPitch() == nextNote.getPitch() == REST:

                  newDuration = currNote.getDuration() + nextNote.getDuration()
                  currNote.setDuration(newDuration)

                  phrase.removeNote(index + 1)

               index -= 1

      def tiePart(part):
         """Helper function to tie rests in a part."""

         for phrase in part.getPhraseList():
            tiePhrase(phrase)

      def tieScore(score):
         """Helper function to tie rests in a score."""

         for part in score.getPartList():
            tiePart(part)

      # check type of material and call the appropriate function
      if type(material) == Score:
         tieScore(material)

      elif type(material) == Part:
         tiePart(material)

      elif type(material) == Phrase:
         tiePhrase(material)

      else:   # error check
         raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Phrase, Part, or Score." )


   @staticmethod
   def transpose(material, steps, scale=CHROMATIC_SCALE, key=0):
      """
      Transposes the material up or down in scale degrees.
      - material: Note, Phrase, Part, or Score
      - steps:    integer number of scale steps (positive or negative)
      - scale:    list of pitch offsets in the octave (default: chromatic scale)
      - key:      root MIDI pitch offset (default: 0)
      """
      # do some basic error checking
      if not isinstance(material, (Note, Phrase, Part, Score)):
         raise TypeError(f'Mod.transpose(): material must be a Note, Phrase, Part, or Score (it was {type(material)})')
      elif not isinstance(steps, int):
         raise TypeError(f'Mod.transpose(): steps must be an integer (it was {type(steps)})')

      # define support methods
      def transposeNote(note):
         """transposeNote does the work of the transpose method."""
         pitch  = note.getPitch()

         if note.isRest():  # rests aren't transposable, so we can skip the work
            pass

         elif not isinstance(pitch, int) or (pitch < 0 or pitch > 127):  # if pitch isn't an integer MIDI pitch, transposing won't work
            pass

         else:  # otherwise, we can start transposing
            pitchClass = (pitch - key) % 12
            octave     = (pitch - key) // 12
            degree     = None

            # find the degree in the scale
            if pitchClass in scale:  # use the pitch in the scale
               degree = scale.index(pitchClass)
            else:                    # find the nearest lower pitch in scale
               pitchClassesInScale = [s for s in scale if s <= pitchClass]
               scalePitchClass = None

               if pitchClassesInScale:
                  scalePitchClass = max(pitchClassesInScale)
               else:                 # there isn't a nearest lower pitch, so move down an octave
                  scalePitchClass = max(scale)
                  octave = octave - 1

               degree = scale.index(scalePitchClass)

            # transpose within the scale
            newDegree = degree + steps

            # adjust octave as needed
            octaveShift, newDegree = divmod(newDegree, len(scale))
            newOctave = octave + octaveShift

            # if newDegree is negative, move down an octave
            if newDegree < 0:
               newDegree = newDegree + len(scale)
               newOctave = newOctave - 1

            # find transposed pitch
            newPitch = key + newOctave * 12 + scale[newDegree]

            # clamp to MIDI pitch range
            newPitch = min(127, (max(0, newPitch)))

            note.setPitch(newPitch)
      #### end transposeNote()

      def transposePhrase(phrase):
         for note in phrase.getNoteList():
            transposeNote(note)

      def transposePart(part):
         for phrase in part.getPhraseList():
            transposePhrase(phrase)

      def transposeScore(score):
         for part in score.getPartList():
            transposePart(part)

      # time to actually do the work
      if isinstance(material, Score):
         transposeScore(material)
      elif isinstance(material, Part):
         transposePart(material)
      elif isinstance(material, Phrase):
         transposePhrase(material)
      elif isinstance(material, Note):
         transposeNote(material)
      else:   # error check
         raise TypeError( "Unrecognized material type " + str(type(material)) + " - expected Note, Phrase, Part, or Score." )

#### Read and Write ################################################################
#######################################################################################
from music import *
import os
import mido

# read a MIDI file into a Score using the Read.midi() function
class Read:
   """Read class provides functionality to read MIDI files into transcription data structures."""

   @staticmethod
   def midi(score, filename):
      """Import a standard MIDI file to a Score."""
      if score is None:
         print("Read.midi error: The score is not initialised! I'm doing it for you.")
         score = Score()

      score.empty()   # clear any existing data

      print("\n--------------------- Reading MIDI File ---------------------")
      try:
         # open and read the MIDI file
         midiFile = mido.MidiFile(filename)

         # set the score title to the filename
         score.setTitle(os.path.basename(filename))

         # process each track
         for trackIndex, track in enumerate(midiFile.tracks):
            part = Part()
            # part.setTitle(f"Track {trackIndex}") # Optional: name part by track index or name

            phrasesForPart = []
            # stores the logical end time in beats for each phrase in phrasesForPart
            phraseCurrentLogicalEndTimeBeats = []

            activeNotesOnTrack = {}      # key=(channel, pitch), value=list of (start_time_ticks, velocity)
            absoluteTimeTicksTrack = 0   # cumulative time in ticks for the current track

            for msg in track:
               absoluteTimeTicksTrack += msg.time

               if msg.type == 'program_change':
                  part.setInstrument(msg.program)
                  part.setChannel(msg.channel)

               elif msg.type == 'set_tempo':
                  tempoBpm = 60000000 / msg.tempo
                  score.setTempo(tempoBpm)

               elif msg.type == 'time_signature':
                  score.setTimeSignature(msg.numerator, msg.denominator)

               elif msg.type == 'key_signature':
                  # Placeholder for key signature handling if JMC constants for keys are defined
                  # And a mapping from mido key string to key integer is available.
                  # For now, we are skipping it as in the previous version.
                  # score.setKeySignature(mido_key_to_jmusic_int(msg.key))
                  # score.setKeyQuality(...) # Major/minor if discernible
                  pass

               elif msg.type == 'note_on' and msg.velocity > 0:   # note on
                  key = (msg.channel, msg.note)
                  if key not in activeNotesOnTrack:
                     activeNotesOnTrack[key] = []
                  activeNotesOnTrack[key].append( (absoluteTimeTicksTrack, msg.velocity) )

               elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):   # note off
                  key = (msg.channel, msg.note)
                  if key in activeNotesOnTrack and activeNotesOnTrack[key]:
                     startTimeTicks, velocity = activeNotesOnTrack[key].pop(0)
                     if not activeNotesOnTrack[key]:   # clean up if list is empty
                        del activeNotesOnTrack[key]

                     noteStartTimeBeats = startTimeTicks / midiFile.ticks_per_beat
                     noteEndTimeBeats = absoluteTimeTicksTrack / midiFile.ticks_per_beat

                     if noteEndTimeBeats <= noteStartTimeBeats:
                        continue

                     durationBeats = noteEndTimeBeats - noteStartTimeBeats

                     targetPhraseIndex = -1
                     for phraseIdx in range(len(phrasesForPart)):
                        # A phrase is suitable if this note starts at or after the phrase's current logical end time
                        # (with a small tolerance for notes that might slightly precede the 'official' end due to rounding)
                        # jMusic uses a 0.08 beat tolerance.
                        if phraseCurrentLogicalEndTimeBeats[phraseIdx] <= noteStartTimeBeats + 0.08:
                           targetPhraseIndex = phraseIdx
                           break

                     # create new phrase if no suitable existing phrase found
                     if targetPhraseIndex == -1:
                        newPhrase = Phrase()
                        newPhrase.setStartTime(noteStartTimeBeats)
                        phrasesForPart.append(newPhrase)
                        phraseCurrentLogicalEndTimeBeats.append(noteStartTimeBeats)
                        targetPhraseIndex = len(phrasesForPart) - 1

                     # get reference to current phrase and its logical end time
                     currentSelectedPhrase = phrasesForPart[targetPhraseIndex]
                     currentPhraseLogicalEnd = phraseCurrentLogicalEndTimeBeats[targetPhraseIndex]

                     # add rest if there's a gap between current phrase end and note start
                     if noteStartTimeBeats > currentPhraseLogicalEnd:
                        restDuration = noteStartTimeBeats - currentPhraseLogicalEnd
                        if restDuration > 0.01:   # only add rest if gap is significant
                           restNote = Note(REST, restDuration)
                           currentSelectedPhrase.addNote(restNote)
                           phraseCurrentLogicalEndTimeBeats[targetPhraseIndex] += restDuration

                     # add the actual note and update phrase end time
                     jmusicNote = Note(msg.note, durationBeats, velocity)
                     currentSelectedPhrase.addNote(jmusicNote)
                     phraseCurrentLogicalEndTimeBeats[targetPhraseIndex] = noteEndTimeBeats

            # End of message loop for track
            # Handle any notes still active at the end of the track (e.g., if no note_off)
            # For simplicity, these are currently ignored if not explicitly closed.
            # A more robust solution might end them at the time of the last MIDI event in the track.

            # add all phrases to the part
            for createdPhrase in phrasesForPart:
               if createdPhrase.getNoteList():
                  part.addPhrase(createdPhrase)

            # add part if it has phrases or an instrument was set
            if part.getPhraseList() or part.getInstrument() != -1:
               score.addPart(part)

         # end of track loop
         print(f"MIDI file '{filename}' read into score '{score.getTitle()}'")

      except FileNotFoundError:   # file not found
         print(f"Read.midi error: File not found - {filename}")

      except Exception as e:   # catch any other errors
         print(f"Read.midi error: Could not read MIDI file '{filename}'.")
         print(f"Error details: {e}")

      print("-------------------------------------------------------------")

      # return score, whether modified or new
      return score

# write a MIDI file from a Score, Part, Phrase, or Note using the Write.midi() function
class Write:

   @staticmethod
   def midi(material, filename):
      """Write a standard MIDI file from a Score, Part, Phrase, or Note."""
      # start timing and print header
      print("\n----------------------------- Writing MIDI File ------------------------------")

      # do necessary datatype wrapping
      if type(material) == Note:
         material = Phrase(material)
      if type(material) == Phrase:   # no elif - we need to successively wrap from Note to Score
         material = Part(material)
         material.setInstrument(-1)     # indicate no default instrument (needed to access global instrument)
      if type(material) == Part:     # no elif - we need to successively wrap from Note to Score
         material = Score(material)

      if type(material) == Score:
         # we are good - let's write it then!
         score = material   # by now, material is a score, so create an alias (for readability)

         # create a new MIDI file with 480 ticks per beat (standard)
         midiFile = mido.MidiFile(ticks_per_beat=480)

         # handle each part in the score
         for partIndex, part in enumerate(score.getPartList()):
            # print part information
            partTitle = part.getTitle() if part.getTitle() else ""
            print(f"    Part {partIndex} '{partTitle}' to Track on Ch. {part.getChannel()}: ", end="")

            # create a new track for this part
            track = mido.MidiTrack()
            midiFile.tracks.append(track)

            # if this is the first track, add the score title as a meta message
            if partIndex == 0 and score.getTitle():
               # use 'track_name' for the score title on the first track
               track.append(mido.MetaMessage('track_name', name=score.getTitle(), time=0))

            # set track name
            trackName = part.getTitle() if part.getTitle() else f"Track {partIndex}"
            track.append(mido.MetaMessage('track_name', name=trackName, time=0))

            # set tempo (microseconds per beat)
            tempo = part.getTempo() if part.getTempo() > 0 else score.getTempo()
            microsecondsPerBeat = int(60000000 / tempo)
            track.append(mido.MetaMessage('set_tempo', tempo=microsecondsPerBeat, time=0))

            # set time signature if available
            if hasattr(score, 'getNumerator') and hasattr(score, 'getDenominator'):
               numerator = score.getNumerator()
               denominator = score.getDenominator()
               track.append(mido.MetaMessage('time_signature',
                                           numerator=numerator,
                                           denominator=denominator,
                                           time=0))

            # set instrument via program change
            instrument = part.getInstrument()
            if instrument >= 0:
               track.append(mido.Message('program_change',
                                       program=instrument,
                                       channel=part.getChannel(),
                                       time=0))

            # collect all notes from all phrases
            noteEvents = []

            for phraseIndex, phrase in enumerate(part.getPhraseList()):
               dotCount = phrase.getSize()
               print(f" Phrase {phraseIndex}:" + "." * dotCount, end="")

               # get phrase start time in ticks
               phraseStartTicks = int(phrase.getStartTime() * 480)

               # apply phrase instrument if set
               phraseInstrument = phrase.getInstrument()
               if phraseInstrument >= 0:
                  noteEvents.append({
                     'tick': phraseStartTicks,
                     'msg': mido.Message('program_change',
                                       program=phraseInstrument,
                                       channel=part.getChannel(),
                                       time=0)
                  })

               # apply phrase tempo if set
               phraseTempo = phrase.getTempo()
               if phraseTempo > 0:
                  phraseMicrosecondsPerBeat = int(60000000 / phraseTempo)
                  noteEvents.append({
                     'tick': phraseStartTicks,
                     'msg': mido.MetaMessage('set_tempo',
                                          tempo=phraseMicrosecondsPerBeat,
                                          time=0)
                  })

               # process each note in the phrase
               for noteIndex in range(phrase.getSize()):
                  note = phrase.getNote(noteIndex)

                  # get note parameters
                  pitch = note.getPitch()

                  # skip rests
                  if pitch < 0:
                     continue

                  # convert note timing to ticks
                  noteStartTime = phrase.getNoteStartTime(noteIndex)
                  noteTicks = phraseStartTicks + int(noteStartTime * 480)

                  # calculate note duration in ticks
                  durationTicks = int(note.getDuration() * 480)

                  # get note velocity (dynamic)
                  velocity = note.getDynamic()

                  # create note_on event
                  noteEvents.append({
                     'tick': noteTicks,
                     'msg': mido.Message('note_on',
                                       note=pitch,
                                       velocity=velocity,
                                       channel=part.getChannel(),
                                       time=0)
                  })

                  # create note_off event
                  noteEvents.append({
                     'tick': noteTicks + durationTicks,
                     'msg': mido.Message('note_off',
                                       note=pitch,
                                       velocity=0,
                                       channel=part.getChannel(),
                                       time=0)
                  })

            # sort events by tick
            noteEvents.sort(key=lambda event: event['tick'])

            # convert absolute ticks to delta ticks
            previousTick = 0
            for event in noteEvents:
               deltaTicks = event['tick'] - previousTick
               event['msg'].time = deltaTicks
               previousTick = event['tick']
               track.append(event['msg'])

            # end of track
            track.append(mido.MetaMessage('end_of_track', time=0))

            print() # newline after processing all phrases for a part

         # ensure filename ends with .mid
         if not filename.lower().endswith('.mid'):
            filename += '.mid'

         # save the MIDI file
         midiFile.save(filename)

         # print footer
         print(f"MIDI file '{os.path.abspath(filename)}' written from score '{score.getTitle()}'.")
         print("------------------------------------------------------------------------------\n")

      else:   # error check
         print(f'Write.midi(): Unrecognized type {type(material)}, expected Note, Phrase, Part, or Score.')


#######################################################################################
#### Tests ############################################################################
#######################################################################################

def _playNote():
   note = Note(C4, HN)        # create a middle C half note
   Play.midi(note)            # and play it!

def _furElise():
   # theme has some repetition, so break it up to maximize economy
   # (also notice how we line up corresponding pitches and durations)
   pitches0   = [REST]
   durations0 = [HN]
   pitches1   = [E5, DS5, E5, DS5, E5, B4, D5, C5]
   durations1 = [SN, SN,  SN, SN,  SN, SN, SN, SN]
   pitches2   = [A4, REST, C4, E4, A4, B4, REST, E4]
   durations2 = [EN, SN,   SN, SN, SN, EN, SN,   SN]
   pitches3   = [GS4, B4, C5, REST, E4]
   durations3 = [SN,  SN, EN, SN,   SN]
   pitches4   = [C5, B4, A4]
   durations4 = [SN, SN, EN]

   # create an empty phrase, and construct theme from the above motifs
   theme = Phrase()
   theme.addNoteList(pitches0, durations0)
   theme.addNoteList(pitches1, durations1)
   theme.addNoteList(pitches2, durations2)
   theme.addNoteList(pitches3, durations3)
   theme.addNoteList(pitches1, durations1)  # again
   theme.addNoteList(pitches2, durations2)
   theme.addNoteList(pitches4, durations4)

   # create a copy of the theme, and play after the first theme ends
   theme2 = theme.copy()
   theme2.setStartTime( theme.getEndTime() )

   # debug
   noteList = theme.getNoteList()
   startTime = 0
   for i in range(len(noteList)):
      startTime += int(noteList[i].getDuration() * 1000)
      print( "#" + str(i+1) + ": start " + str(startTime) + "ms: " + str(noteList[i]), end="" )

   # play it
   Play.midi(theme)
   Play.midi(theme2)

def _playAudioSample():
   # load audio sample
   # a = AudioSample("test_sound.wav")
   # a = AudioSample("A4_440Hz.mp3")
   a = AudioSample("Vundabar - Smell Smoke - 03 Tar Tongue.mp3")
   a.play()

#######################################################################################

if __name__ == '__main__':
   # _playNote()
   _furElise()
   # _playAudioSample()
