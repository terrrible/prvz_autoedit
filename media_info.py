import subprocess
import os, sys

sys.path.append(os.path.join(os.path.dirname(__file__)))
tool_path = 'ffprobe.exe'
#tool_path = 'D:\\Work\\tools\\ffmpeg\\ffprobe.exe'
framerate = 25.0

def getLength(filename):
	print 'MEDIA_INFO getting framecount for >>>', filename
	tmp = [tool_path, '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames', '-of', 'default=noprint_wrappers=1:nokey=1', filename]
	result = subprocess.Popen(tmp, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	#print result.stdout.readlines()
	try:
		return int([x for x in result.stdout.readlines()][0])
	except ValueError:
		print '####'*15
		print 'MEDIA_INFO bad or missing preview file ...'
		print '####'*15
		return 000


def _seconds(value):
    if isinstance(value, str):  # value seems to be a timestamp
        _zip_ft = zip((3600, 60, 1, 1/framerate), value.split(':'))
        return sum(f * float(t) for f,t in _zip_ft)
    elif isinstance(value, (int, float)):  # frames
        return value / framerate
    else:
        return 0

def _timecode(seconds):
    return '{h:02d}:{m:02d}:{s:02d}:{f:02d}' \
            .format(h=int(seconds/3600),
                    m=int(seconds/60%60),
                    s=int(seconds%60),
                    f=int(round((seconds-int(seconds))*framerate)))

def _frames(seconds):
    return seconds * framerate

def timecode_to_frames(timecode, start=None):
    return _frames(_seconds(timecode) - _seconds(start))

def frames_to_timecode(frames, start=None):
    return _timecode(_seconds(frames) + _seconds(start))
#print getLength('\\\\omega\\woody\\3_post\\ep031\\sh0101\\preview\\ep031_sh0101_comp_v001.mov')
#print getLength('\\\\omega\\woody\\2_prod\\ep031\\sh0101\\preview\\ep031_sh0101_anim_v011.mov')
