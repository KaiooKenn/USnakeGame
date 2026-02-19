class SOUND_PLAYER:
    def __init__(self, sounds):
        self.sounds = sounds
        self.index = 0
        # fmt: off
        self.MELODY = [
    'B4', 'A4', 'G#4', 'A4', 'C5',
    'D5', 'C5', 'B4', 'C5', 'E5',
    'F5', 'E5', 'D#5', 'E5',
    'B5', 'A5', 'G#5', 'A5', 'B5', 'A5', 'G#5', 'A5', 'C6',
    'A5', 'C6', 'G5', 'A5', 'B5', 'A5',
    'G5', 'A5', 'G5', 'A5', 'B5', 'A5',
    'G5', 'A5', 'G5', 'A5', 'B5', 'A5', 'G5', 'F#5', 'E5',

    'E5', 'F5', 'G5', 'G5', 'A5', 'G5', 'F5', 'E5', 'D5',
    'E5', 'F5', 'G5', 'G5', 'A5', 'G5', 'F5', 'E5', 'D5',
    'C5', 'D5', 'E5', 'E5', 'F5', 'E5', 'D5', 'C5', 'B4',
    'C5', 'D5', 'E5', 'E5', 'F5', 'E5', 'D5', 'C5', 'B4',

    'B4', 'A4', 'G#4', 'A4', 'C5',
    'D5', 'C5', 'B4', 'C5', 'E5',
    'F5', 'E5', 'D#5', 'E5',
    'B5', 'A5', 'G#5', 'A5', 'B5', 'A5', 'G#5', 'A5', 'C6',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'G#5', 'A5', 'B5', 'G#5', 'E5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'B5', 'G#5', 'E5', 'A5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'G#5', 'A5', 'B5', 'G#5', 'E5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'B5', 'G#5', 'E5', 'A5'
]
        # fmt: on

    def __iter__(self):
        return self

    def __next__(self):
        self.index = (self.index + 1) % len(self.MELODY)
        return self.sounds[self.MELODY[self.index]]
