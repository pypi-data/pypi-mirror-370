import warnings
with warnings.catch_warnings(): #pydub prints a warning if ffmpeg or avlib aren't installed, but we don't care
    warnings.simplefilter('ignore')
    from pydub import AudioSegment
import os
import logging
import re
import typing

def convert_wav_to_polaris_raw(input: str, output: str | None = None, nxt_trim: bool = False) -> str | None:
    '''Converts a wav file to a raw file with the appropriate parameters for use in a Polaris Anima.
    If no output path/filename is specified, it will use the input filename with '.RAW' in the same directory.
    Returns filename (with path) if successful. Returns None if failed.
    
    If nxt_trim is True, output files will be trimmed to NXT-compatible lenghts. Note that this will only work with the standard naming scheme.'''
    _log = logging.getLogger('Sound')

    # Polaris compatible sound specifications
    _SAMPLE_RATE = 44100
    _CHANNELS = 1 # mono
    _BIT_DEPTH = 2 # 16-bit

    # NXT-compatible sound lengths (in milliseconds)
    _NXT_HUM_LENGTH = 19.9 * 1000
    _NXT_SWING_LENGTH = 5.9 * 1000
    _NXT_POWERON_LENGTH = 2.9 * 1000

    try:
        #open the file
        _log.debug(f'Opening audio file: {input}')
        sound: AudioSegment = AudioSegment.from_file(input, format='wav')

        # set sound to proper parameters
        _log.debug(f'Converting file to parameters: Sample Rate = {_SAMPLE_RATE}, Channels = {_CHANNELS}, Bit Depth = {_BIT_DEPTH*8}-bit')
        sound = sound.set_frame_rate(_SAMPLE_RATE)
        sound = sound.set_channels(_CHANNELS)
        sound = sound.set_sample_width(_BIT_DEPTH)

        # get output path and filename
        # if no output is specified, use '{basename}.RAW' in the same directory
        if not output:
            dir = os.path.dirname(os.path.realpath(input))
            output = os.path.join(dir, os.path.splitext(os.path.basename(input))[0] + '.RAW')

        # if output didn't include a directory, default to the same directory as the input
        if not os.path.dirname(output):
            dir = os.path.dirname(os.path.realpath(input))
            output = os.path.join(dir, output)

        # if output includes a directory, check to make sure it exists (or create if necessary)
        else:
            dir = os.path.dirname(output)
            # if it's a relative path, use the input file location as the base
            if not os.path.isabs(dir):
                output = os.path.join(os.path.dirname(os.path.realpath(input)), output)
            
            # create dir (if needed)
            if not os.path.exists(dir) or not os.path.isdir(dir):
                os.mkdir(os.path.dirname(output))
        
        # if output is a directory with no filename, append the default filename
        if os.path.isdir(output):
            output = os.path.join(output, os.path.splitext(os.path.basename(input))[0] + '.RAW')

        # if requested, trim files to length that works with NXTs
        if nxt_trim:
            # figure out effect type based on filename. Will only work with default naming scheme
            # I might make this more robust using regex patters to match any filename, but that will come later.
            if "HUM_" in output:
                trim_length = _NXT_HUM_LENGTH
            elif "SMOOTHSWING" in output:
                trim_length = _NXT_SWING_LENGTH
            elif "POWERON" in output:
                trim_length = _NXT_POWERON_LENGTH
            else:
                trim_length = 0
            # trim the file
            if trim_length:
                sound = sound[:trim_length] # type: ignore

        # write output file
        _log.debug(f'Writing output file: {output}')
        sound.export(output, format='raw')
        return output

    except Exception as e:
        _log.error(e)
        return None

# This next bit is to attempt to automatically translate source sound font names to Polaris default names using regexps.
class _Effect_RE(object):
    '''Holds regular expressions for pattern matching during file conversion'''
    # yeah, this is probably overkill as a data structure, but it makes the code read easier when it gets to regexp matching time
    def __init__(self, searches: list[str], polaris_sub: str | typing.Callable) -> None:
        '''searches: regexp patterns to use on source filenames.
        polaris_sub: regexp to use when as substitute pattern, or function to define the match'''
        super().__init__()
        self.searches = searches
        self.polaris_sub = polaris_sub

# Regex patterns to use when auto-renaming. Polaris names are included for various edge cases.
_patterns = {
    'clash': _Effect_RE(
        searches=[
            r'^cla*sh0*(\d+)\.wav$', # CFX, Proffie, Verso
            r'^clash \((\d*)\)\.wav$', # Xenopixel
            r'^clash_(\d*)_0\.wav$' # Polaris
        ],
        polaris_sub=r'CLASH_\1_0.RAW'
    ),
    'hum': _Effect_RE(
        searches=[
            r'^hum\w*?0*(\d*)\.wav$', # CFX, Proffie, Verso
            r'^hum \((\d*)\)\.wav$', # Xenopixel
            r'^hum_(\d*)\.wav$' # Polaris
        ],
        # lambda is necessary because some fonts just have one "hum.wav" with no number
        polaris_sub=lambda m: f'HUM_{int(m.group(1))-1}.RAW' if m.group(1) else 'HUM_0.RAW'
    ),
    'poweroff': _Effect_RE(
        searches=[
            r'^po*we*roff(\d*)\.wav$', # CFX
            r'^in0*(\d*)\.wav$', # Proffie
            r'^off(\d*)\.wav$', # Verso
            r'^in \((\d*)\)\.wav$', # Xenopixel
            r'^poweroff_(\d*)\.wav$' # Polaris
        ],
        polaris_sub=lambda m: f'POWEROFF_{int(m.group(1))-1}.RAW' if m.group(1) else 'POWEROFF_0.RAW'
    ),
    'poweron': _Effect_RE(
        searches=[
            r'^poweron(\d*)\.wav$', # CFX
            r'^out0*(\d*)\.wav$', # Proffie
            r'^on(\d*)\.wav$', # Verso
            r'^out \((\d*)\)\.wav$', # Xenopixel
            r'^poweron_(\d*)\.wav$' # Polaris
        ],
        polaris_sub=lambda m: f'POWERON_{int(m.group(1))-1}.RAW' if m.group(1) else 'POWERON_0.RAW'
    ),
    'smoothswing-high': _Effect_RE(
        searches=[
            r'^hswing(\d*)\.wav$', # CFX
            r'^swingh0*(\d*)\.wav$', # Proffie, Verso
            r'^swingh \((\d*)\)\.wav$', # Xenopixel
            r'^smoothswingh_(\d*)_0\.wav$' # Polaris
        ],
        polaris_sub=r'SMOOTHSWINGH_\1_0.RAW'
    ),
    'smoothswing-low': _Effect_RE(
        searches=[
            r'^lswing(\d*)\.wav$', # CFX
            r'^swingl0*(\d*)\.wav$', # Proffie, Verso
            r'^swingl \((\d*)\)\.wav$', # Xenopixel
            r'^smoothswingl_(\d*)_0\.wav$' # Polaris
        ],
        polaris_sub=r'SMOOTHSWINGL_\1_0.RAW'
    ),
    'swing': _Effect_RE(
        searches=[
            r'^swi*ng0*(\d*)\.wav$', # CFX, Proffie. No standard swings for Xenopixel
            r'^aswing(\d*)\.wav$', # Verso. Technically these are swing accents, but they'll do.
            r'^swing_(\d*)_0\.wav$'
        ],
        polaris_sub=r'SWING_\1_0.RAW'
    ),
    'beep': _Effect_RE(
        searches=[
            r'^beep.wav$' # This is it for now
        ],
        polaris_sub=r'BEEP.RAW'
    )
}

def get_polaris_filename(wav: str) -> str:
    '''Takes a wave file name as input and attempts to match it to a default Polaris Anima sound file name.
    You can pass in the file with or without a path; however, the return will only have the base file name.
    If it is unable to match the filename, it will return {wav_name}.RAW'''
    _log = logging.getLogger('Sound')

    wav = os.path.basename(wav)
    _log.debug(f'Matching filename: {wav}')

    for effect in _patterns.keys():
        _log.debug(f'Searching effect: {effect}')
        for search in _patterns[effect].searches:
            raw_name = re.sub(search, _patterns[effect].polaris_sub, wav, re.I)
            # if the pattern matched, raw_name will be the correct name to return. If not, it will be the same as wav
            if not raw_name == wav:
                _log.debug(f'Match found! Wav file: {wav} , Raw file: {raw_name}.')
                return raw_name
    
    # if we get here, no match was found
    raw_name = os.path.splitext(wav)[0] + '.RAW'
    _log.debug(f'No matching pattern found. Returning default name: {raw_name}')
    return raw_name