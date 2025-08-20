"""
📡 Caelus Musical Constants

Standard musical notation constants and mappings.
"""

# Clef definitions
CLEF_SIGNS = {
    'treble': {'sign': 'G', 'line': '2'},
    'bass': {'sign': 'F', 'line': '4'},
    'alto': {'sign': 'C', 'line': '3'},
    'tenor': {'sign': 'C', 'line': '4'},
}

# Common instruments with default clefs
INSTRUMENTS = {
    'piano': {'clef': 'treble', 'transposition': 0},
    'violin': {'clef': 'treble', 'transposition': 0},
    'viola': {'clef': 'alto', 'transposition': 0},
    'cello': {'clef': 'bass', 'transposition': 0},
    'bass': {'clef': 'bass', 'transposition': -12},
    'flute': {'clef': 'treble', 'transposition': 0},
    'clarinet': {'clef': 'treble', 'transposition': -2},
    'trumpet': {'clef': 'treble', 'transposition': -2},
    'horn': {'clef': 'treble', 'transposition': -7},
    'trombone': {'clef': 'bass', 'transposition': 0},
    'percussion': {'clef': 'treble', 'transposition': 0},
}

# Default MusicXML divisions (quarter note = 2)
DEFAULT_DIVISIONS = 2

# ABC note duration mappings
ABC_DURATIONS = {
    '1': 1,    # eighth note
    '2': 2,    # quarter note
    '4': 4,    # half note
    '8': 8,    # whole note
    '/2': 0.5, # sixteenth note
    '/4': 0.25, # thirty-second note
}

# ABC octave modifiers
ABC_OCTAVE_MODIFIERS = {
    ',': -1,   # comma lowers octave
    "'": 1,    # apostrophe raises octave
}

# Default key signatures (number of sharps/flats)
KEY_SIGNATURES = {
    'C': 0, 'G': 1, 'D': 2, 'A': 3, 'E': 4, 'B': 5, 'F#': 6, 'C#': 7,
    'F': -1, 'Bb': -2, 'Eb': -3, 'Ab': -4, 'Db': -5, 'Gb': -6, 'Cb': -7,
}

# Time signatures
TIME_SIGNATURES = {
    '4/4': {'beats': 4, 'beat_type': 4},
    '3/4': {'beats': 3, 'beat_type': 4},
    '2/4': {'beats': 2, 'beat_type': 4},
    '6/8': {'beats': 6, 'beat_type': 8},
    '9/8': {'beats': 9, 'beat_type': 8},
    '12/8': {'beats': 12, 'beat_type': 8},
}