import xml.etree.ElementTree as ET
#import os, sys
from pprint import pprint

import autoedit_main
#sys.path.append('//PAROVOZ-FRM01//Shotgun//utils2')
#sys.path.append(r'//parovoz-frm01//tank//shared_core//studio//install//core//python//tank_vendor')

import helpers
from shotgun_api3 import Shotgun

SERVER_PATH = 'https://parovoz.shotgunstudio.com' # make sure to change this to https if your studio uses it.
SCRIPT_NAME = 'dmityscripts'
SCRIPT_KEY = 'd8337d21a847a212b98e6f012737eee6d12dff7b74ed71fba7771d278370b585'

SG = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)
#path = os.path.abspath(r'\\omega\woody\1_pre\ep040\animatic\timecodes\ep040_timecodes.xml')

#path = sys.argv[1]
framerate = 25.0

#raw_input("Press the <ENTER> key to continue...")
def update_sg_episode_field(path, data, ep_name, prj_name):
	project = autoedit_main.get_prj_id(prj_name)
	active_episodes = SG.find('CustomEntity01',[['project.Project.id', 'is', project],['sg_status_list', 'is', 'ip']],['code', 'description', 'sg_name'])
	#print data
	print 'EP NAME:', ep_name
	#print 'active_episodes:', active_episodes
	ep_id = [i['id'] for i in active_episodes if i['code'] == ep_name][0]
	SG.update("CustomEntity01", ep_id, {'sg_dir':', '.join(data)})

def parse_ep_name(path):
	return path.rsplit('\\', 1)[1].split('_')[0]

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

def init_parsing(path, ep_name, prj_name):
	out_path = path.replace('.xml', '.sg')
	root = ET.parse(path).getroot()
	L1 = []
	print '1@', path
	print '2@', out_path
#print root.findall(".")
	new = root.findall("./sequence/media/video/track/clipitem")
#print root.findall("./sequence/media/video/track/clipitem")

	for child in new:
		L2 = {}
		items = list(child)
		for n in items:
			L2[n.tag] = n.text
		L1.append([child.get('id'), L2])
	for j,i in enumerate(L1):
		start = int(i[1]['start'])
		end = int(i[1]['end'])
		print j+1, frames_to_timecode(start + 1, start='00:00:00:00'), frames_to_timecode(end, start='00:00:00:00')

	z = [i[1]['name'] for i in L1]
	pprint([i[1]['name'] for i in L1])

#write string for sg
	with open(out_path, 'a') as f1: f1.write(str(z))
	update_sg_episode_field(path, z, ep_name, prj_name)
