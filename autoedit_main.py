# -*- coding: utf-8 -*-
import os
import sys
import shutil
from pprint import pprint
from time import time
import json

sys.path.append('D:\\Work\\Scripts\\modules\\colorama-0.3.9')
sys.path.append(os.path.join(os.path.dirname(__file__)))
from colorama import init, Fore, Back, Style
init(autoreset=True)

ffmgeg_path = 'Y:/tools30/utilities/ffmpeg/windows/bin/ffmpeg.exe'

sys.path.append('//PAROVOZ-FRM01//Shotgun//utils2')
sys.path.append(r'//parovoz-frm01//tank//shared_core//studio//install//core//python//tank_vendor')
#sys.path.append(r'D://Work//Scripts//other')

import media_info

import decode_shot_code as dsc
import helpers
from shotgun_api3 import Shotgun

SERVER_PATH = 'https://parovoz.shotgunstudio.com' # make sure to change this to https if your studio uses it.
SCRIPT_NAME = 'dmityscripts'
SCRIPT_KEY = 'd8337d21a847a212b98e6f012737eee6d12dff7b74ed71fba7771d278370b585'

SG = Shotgun(SERVER_PATH, SCRIPT_NAME, SCRIPT_KEY)

serv = 'omega'
#PRJ = ''
processes_dict = {'3_post':['comp', 'comp2d', 'render'], '2_prod':['asmbl', 'anim', 'anim2d', 'layout', 'cut']}
version_file_dict = {'sh_name':'sh_name', 'filename':'filename', 'time':0000, 'stage':'stage', 'proc':'proc', 'framecount':'000', 'path':'path'}

def DEBUG():
	project = get_prj_id('woody')
	print SG.find('Asset', [['project.Project.id', 'is', project], ['custom_entity01_sg_assets_custom_entity01s.CustomEntity01.code', 'is', 'ep043'], ['sg_type_one.CustomEntity04.code', 'is', 'locs']], ['code'])

def get_all_prj_eps(prj_name):
	project = get_prj_id(prj_name)
	active_episodes = SG.find('CustomEntity01',[['project.Project.id', 'is', project],['sg_status_list', 'is', 'ip']],['code', 'description', 'sg_name'])
	return sorted([[i['code'], i['sg_name']] for i in active_episodes])

def get_ep_pattern(ep, prj_name):
	#sginfo = dsc.ShotCodeInfo(ep+'_sh0101_comp_v000',  helpers.ProjectHelper.woody_id)
	sginfo = get_SG_INFO(ep+'_sh0101_cut_v000', prj_name)
	#print 'get_ep_pattern sg info', sginfo
	sginfo._task_fields.append('entity.Shot.sg_sequence.Sequence.sg_episode.CustomEntity01.sg_dir')
	try:
		sg_ep_pattern = sginfo.get_task(SG)['entity.Shot.sg_sequence.Sequence.sg_episode.CustomEntity01.sg_dir']
		if sg_ep_pattern: return sg_ep_pattern.translate(None,"',").split(' ')
	except Exception:
		print "can't get ep_pattern from SG"
		pass

def get_prj_id(prj_name):
	if prj_name == 'woo-woo': prj_name = 'woowoo'
	project_id = prj_name + '_id'
	return eval('helpers.ProjectHelper.' + project_id)

def get_SG_INFO(prw_filename, prj_name):
	print '%%%%%%%'
	project = get_prj_id(prj_name)
	print 'project in get_SG_INFO', project
	return dsc.ShotCodeInfo(prw_filename,  project)

def update_sg_episode_field(data, ep_name, prj_name):
	project = get_prj_id(prj_name)
	active_episodes = SG.find('CustomEntity01',[['project.Project.id', 'is', project],['sg_status_list', 'is', 'ip']],['code', 'description', 'sg_name'])
	print 'EP NAME:', ep_name
	#print 'active_episodes:', active_episodes
	ep_id = [i['id'] for i in active_episodes if i['code'] == ep_name][0]
	SG.update("CustomEntity01", ep_id, {'sg_dir':', '.join(data)})

def configure_path(prj_name='', sh_name='', prw='', proc='', edt='', filenm ='', ep=''):
	path = os.path.abspath(r'\\{server}\\{project}\\{process}\\{episode}\\{shot}\\{preview}\\{edit}\\{filename}'.format(server=serv, project=prj_name, process=proc, episode=ep, shot=sh_name, preview=prw, edit=edt, filename=filenm))
	return path

def collect_prws2(path, stage, sh_name, ep_name, prj_name):
	coll_lst_dict = {}
	for proc in processes_dict[stage]:#for ['comp', 'render'] или ['anim', 'layout', 'cut']
		if proc == 'cut': path = configure_path(prj_name=prj_name, sh_name=sh_name, prw='cut', proc='2_prod', ep=ep_name)
		#prw_filename_list = sorted([name for name in os.listdir(path) if proc in name.split('_') and 'wav' not in name])#sort current proc previews by version
		prw_filename = get_latest_filename(path, proc, 'mov')
		#print '@DEBUG ', proc, prw_filename
		if prw_filename != False:
			coll_lst_dict[proc] = dict(sh_name=sh_name,
										filename=prw_filename,
										time=os.stat(path+'\\'+prw_filename).st_mtime,
										stage=stage,
										proc=proc,
										framecount='000',
										path=path)
		#else:
			#coll_lst_dict[proc] = 'no prw'
	#print coll_lst_dict
	return coll_lst_dict

def get_preview_framecount(prw_filename_path):
		return media_info.getLength(prw_filename_path)

def get_shot_prws2(sh_name, ep_name, prj_name):
	print '----------------------------------------------------------'
	t2 = time()
	prw_dict = {sh_name:{}}
	for stage in sorted(processes_dict.keys(), reverse=True):#for stage in ['3_post', '2_prod'], может быть уже не нужна сортировка?
		path = configure_path(prj_name=prj_name, sh_name=sh_name, prw='preview', proc=stage, ep=ep_name)# path to preview folder in the given process
		if os.path.exists(path):
			#prw_dict[stage] = collect_prws2(path, stage, sh_name, ep_name)
			prw_dict[sh_name].update(collect_prws2(path, stage, sh_name, ep_name, prj_name))
			'''append
			[['id001_sh0101_comp_v017.mov', 1508168554.0, '3_post', 'comp', 97],
			['id001_sh0101_render_v002.mov', 1507326908.0, '3_post', 'render', 97],
			['id001_sh0101_anim_v003.mov', 1507312039.0, '2_prod', 'anim', 97],
			['id001_sh1201_cut_v001.mov', 1502707227.0, '2_prod', 'cut', 319]]
			'''
 		else:
			print 'folder--> %s doesn\'t exist' % path
			pass
	if prw_dict[sh_name] == {}:
		prw_dict[sh_name] = 'empty'
	#prw_list_expanded =  [el for lst in prw_list for el in lst]
	#pprint(prw_list_expanded)
	#pprint(sorted(prw_list_expanded, lambda x, y: cmp(x[1], y[1]), reverse=True))
	#return sorted(prw_list_expanded, lambda x, y: cmp(x[1], y[1]), reverse=True)#return list sorted by time
	t3 = time()
	print 'function get_shot_prws2 takes %f' %(t3-t2)
	#print 'COMPLETE PRW LIST FOR A SHOT ...'
	#pprint(prw_dict)
	return prw_dict

def check_out_path(path, ver_filename_path):
	if not os.path.exists(path):
		print 'MAKING DIR ---> %s' % path
		os.makedirs(path)
		create_version_file(ver_filename_path)
		#with open(ver_filename_path, 'w') as ver_file: ver_file.write('filename\ntime\nstage\nproc\n000\npath')#create 'version' file
	elif not os.path.exists(ver_filename_path):
		create_version_file(ver_filename_path)
		#with open(ver_filename_path, 'w') as ver_file: ver_file.write('filename\ntime\nstage\nproc\n000\npath')#create 'version' file
	else:
		with open(ver_filename_path, 'r+') as ver_file:
			try:
				data_ver_file = json.load(ver_file)
				if type(data_ver_file) != type(version_file_dict): data_ver_file = {}
			except ValueError:
				#data_ver_file = [i.strip() for i in ver_file.readlines()]
				data_ver_file = {}
				print 'VALUE ERROR', ver_file.read()
			if len(data_ver_file) != len(version_file_dict):
				verfile_template = list(version_file_dict)
				data_list = list(data_ver_file)
				missed_items = [item for item in verfile_template if item not in data_list]
				print 'DATA', data_ver_file
				print 'MISSED ITEM', missed_items
				for i in missed_items:
					data_ver_file[i] = version_file_dict[i]
					#missed_index = version_file_dict.index(i)
					#print 'MISSED INDEX', missed_index
					#data.insert(missed_index, i)
				print 'NEW DATA 2', data_ver_file
				ver_file.seek(0)
				json.dump(data_ver_file, ver_file)
				#ver_file.seek(0)
				#for d in data:
					#ver_file.write(d+'\n')

def create_version_file(ver_filename_path):
	'''create or reformat .version file'''
	try:
		ver_file = open(ver_filename_path, 'w')
		print 'OPENING IN "W" mode'
	except IOError:
		ver_file = open(ver_filename_path, 'r+')
		ver_file.truncate()
		print 'OPENING IN "R+" mode'
	#with open(ver_filename_path, 'r+') as ver_file:
	json.dump(version_file_dict, ver_file)#create 'version' file
	ver_file.close()
	return json.load(open(ver_filename_path, 'r'))
		#for d in version_file_dict.values():
			#ver_file.write(d+'\n')#create 'version' file

def update_version_file(ver_filename_path, edit_filename_path, prw_container, frame_count):
	'''write to .version file'''
	with open(ver_filename_path, 'r+') as ver_file:
		ver_file.seek(0)
		#map(lambda x: ver_file.write(str(x)+'\n'), prw_container)
		#ver_file.truncate()
		json.dump(prw_container, ver_file)
	#allshots_prw_lst.append(["file '" + edit_filename_path + "'", frame_count])
	
def make_ep_job_list(sh_name, prw_container, ep_name, EP_JOB_LIST, prj_name):
	'''
	prw_container = ['ep013_sh0102_comp_v008.mov', 1508499626.0, '3_post', 'comp', 161]
	'''
	t0 = time()
	prw_filename = prw_container['filename']
	prw_date = prw_container['time']
	prw_stage = prw_container['stage']
	prw_proc = prw_container['proc']

	#sginfo = dsc.ShotCodeInfo(prw_filename,  helpers.ProjectHelper.woody_id)
	print 'prw_filename', prw_filename
	print 'prj_name', prj_name
	try:
		print 'TRY'
		SG_INFO = get_SG_INFO(prw_filename, prj_name)
		print 'SG_INFO', SG_INFO
		SG_INFO.process = 'cut'
		SG_frame_count = int(SG_INFO.get_task(SG)['entity.Shot.sg_cut_out'])
		print 'SG_frame_count', SG_frame_count
		if SG_frame_count == None: SG_frame_count = 0
	except:
		print 'EXCEPT'
		SG_frame_count = 0

	#print '### SG_INFO', SG_INFO
	#print '### SG_frame_count', SG_frame_count
	edit_dir_path = configure_path(prj_name=prj_name, sh_name=sh_name, prw='preview', proc='3_post', edt='autoedit', ep=ep_name)
	prw_filename_path = configure_path(prj_name=prj_name, sh_name=sh_name, prw='preview', proc=prw_stage, filenm=prw_filename, ep=ep_name)
	if prw_proc == 'cut': prw_filename_path = configure_path(prj_name=prj_name, sh_name=sh_name, prw='cut', proc=prw_stage, filenm=prw_filename, ep=ep_name)
	ver_filename_path = configure_path(prj_name=prj_name, sh_name=sh_name, prw='preview', proc='3_post', filenm='.version', edt='autoedit', ep=ep_name)
	prw_out_name = prw_filename.rsplit('_',2)[0] + '_edit_%04d.png'
	edit_filename_path = os.path.join(edit_dir_path, prw_out_name)
	check_out_path(edit_dir_path, ver_filename_path)
	prw_frame_count = media_info.getLength(prw_filename_path)
	prw_frame_count_log = prw_frame_count

	#render png sequence
	cmd = ffmgeg_path + ' -i ' + prw_filename_path + ' -r 25 ' + edit_filename_path

	prw_files_list_to_del = []
	error_code = {'SG':0, 'LAST_SYNC':0}

	with open(ver_filename_path, 'r+') as ver_file:
		print 'opening .version file for read', ver_filename_path
		try:
			data_ver_file = json.load(ver_file)
			print 'using JSON...'
			filename = data_ver_file['filename']
		except ValueError:
			print 'JSON not found. Creating empty >>>'
			data_ver_file = create_version_file(ver_filename_path)
		data_prw_filename = data_ver_file['filename']
		data_prw_date = data_ver_file['time']
		#data_prw_stage = data_ver_file['stage']
		data_prw_proc = data_ver_file['proc']
		data_prw_framecount = int(data_ver_file['framecount'])
		#data_prw_path = data_ver_file['path']
		#sh_name = data_ver_file['sh_name']

		#if the given preview framecount differs from SG cut out
		if prw_frame_count != SG_frame_count:
			#prw_frame_count_log = str(prw_frame_count) + '||SG MISMATCH:' + str(SG_frame_count) + u'LAST UPDATE: ' + data_prw_framecount
			error_code['SG'] = 1

		#if the given preview framecount is the same as SG cut out and differs from last SYNC
		if prw_frame_count == SG_frame_count and prw_frame_count != data_prw_framecount:
			#prw_frame_count_log = str(prw_frame_count) + '|| LAST SYNC MISMATCH'  + data_prw_framecount
			#get overframes to delete
			error_code['LAST_SYNC'] = 1

		prw_files_list_to_del = check_overframes(edit_dir_path, SG_frame_count, data_prw_framecount)

		#if the given preview file is differs from it was at last SYNC OR given preview file is the same as it was at last sync BUT the date is differs 
		if prw_stage == 'empty':
			print 'empty shot'
			job_type = 'empty'
		elif data_prw_filename != prw_filename or data_prw_filename == prw_filename and data_prw_date != prw_date:
			print 'shot for update\n', cmd
			job_type = 'update'
		else:
			print 'Version without any changes\n'
			job_type = 'keep'

		EP_JOB_LIST.append({'job_type':job_type,
							'ver_filename_path':ver_filename_path,
							'sh_name':sh_name,
							'edit_filename_path':edit_filename_path,
							'prw_frame_count':prw_frame_count,
							'SG_frame_count':SG_frame_count,
							'prw_container':prw_container,
							'cmd': cmd,
							'prw_filename_path':prw_filename_path,
							'prw_proc':prw_proc,
							'previous_prw_proc':data_prw_proc,
							'previous_prw_framecount':data_prw_framecount,
							'prw_files_list_to_del':prw_files_list_to_del,
							'error_code':error_code})
	t1 = time()
	print 'function make_ep_job_list takes %f' %(t1-t0)
	print '----------------------------------------------------------', '\n'

def check_overframes(edit_dir_path, SG_frame_count, data_prw_framecount):
	obsolete_frame_count = data_prw_framecount - SG_frame_count
	prw_files_list = sorted([i for i in os.listdir(edit_dir_path) if 'png' in i])
	#print 'DEBUG CHECK OVERFRAMES'
	#print obsolete_frame_count
	#print len(prw_files_list)
	#print SG_frame_count
	if obsolete_frame_count > 0 and len(prw_files_list) > SG_frame_count:
		prw_files_list_to_del = map(lambda x: os.path.join(edit_dir_path, x), prw_files_list[-obsolete_frame_count:])
		print '\n'+'###'*15
		print 'Obsolete files to delete:'
		pprint(prw_files_list_to_del)
		print '###'*15+'\n'
		return prw_files_list_to_del

def remove_overframes(prw_files_list_to_del):
	if prw_files_list_to_del:
		for file in prw_files_list_to_del:
			print 'removing obsolete file:', file
			os.remove(file)

def get_latest_filename(chk_path, chk_str, chk_ext=''):
	l1 = sorted([i for i in os.listdir(chk_path) if chk_str in i and chk_ext in i])
	#print 'DEBUG get_latest_filename: sorted list', l1
	if len(l1) > 0:
		return l1[-1]
	else:
		return False

def get_latest_vers_postfix(filename):
	if not filename:
		return int(000)
	else:
		try:
			return int(os.path.splitext(filename)[0].rsplit('_',1)[1].replace('v',''))#return version in "00x" format
		except ValueError:
			return int(000)

def get_autoedit_ver(master_ep, prj_name):
	autoedit_output_path = configure_path(prj_name=prj_name, sh_name='edit', proc='3_post', ep=master_ep)
	current_latest = get_latest_filename(autoedit_output_path, 'edit', 'mov')
	current_postfix = get_latest_vers_postfix(current_latest)
	#print 'DEBUG get_autoedit_ver: current_latest, current_postfix', current_latest, current_postfix
	return str(current_postfix+1).zfill(3)#return version in "00x" format

def get_sedit(master_ep, prj_name):
	sedit_path = configure_path(prj_name=prj_name, sh_name='sedit', proc='3_post', ep=master_ep)
	sedit_filename = get_latest_filename(sedit_path, 'sedit') 
	if sedit_filename:
		return os.path.join(sedit_path, sedit_filename)
	else:
		m = 150
		print '\n', '-'*m, 'NO SEDIT', '\n', '-'*m
		return 'NO SEDIT'
	
def get_master_ep(ep_pattern):
	#print 'DEBUG ep_pattern', ep_pattern
	try:
		return [i for i in ep_pattern if 'ep' in i][0].split('_')[0]
	except:
		return [i for i in ep_pattern if 'id' in i][0].split('_')[0]

def export_autoedit(ep_pattern, allshots_prw_lst, prj_name):
	print Back.YELLOW + Fore.WHITE + Style.BRIGHT + 'START EXPORT'

	#get target episode from ep_pattern
	master_ep = get_master_ep(ep_pattern)

	#path to .prwpathlist
	edit_allshots_prw_path = configure_path(prj_name=prj_name, sh_name='edit', proc='3_post', filenm='.prwpathlist', ep=master_ep)
	edit_allshots_prw_dir = os.path.dirname(os.path.abspath(edit_allshots_prw_path))
	#check path and write to .prwpathlist:
	if not os.path.exists(edit_allshots_prw_dir):
		print 'MAKING DIR ---> %s' % edit_allshots_prw_dir
		os.makedirs(edit_allshots_prw_dir)
	with open(edit_allshots_prw_path, 'a+') as f1:
		print 'CREATE OR COPY', edit_allshots_prw_path, '\n'
		f1.truncate()
		for i in allshots_prw_lst:
			f1.write(i + '\n') 

	autoedit_ver = get_autoedit_ver(master_ep, prj_name)
	sedit_filename_path = get_sedit(master_ep, prj_name)
	edit_allshots_prw_path = configure_path(prj_name=prj_name, sh_name='edit', proc='3_post', filenm='.prwpathlist', ep=master_ep)
	edit_allshots_out_path = configure_path(prj_name=prj_name, sh_name='edit', proc='3_post', filenm=master_ep + '_edit_v'+ autoedit_ver + '.mov', ep=master_ep)
	edit_allshots_out_path_TMP = 'd:\\temp\\autoedits\\' + prj_name + '\\\\'+ master_ep + '_edit_v' + autoedit_ver + '.mov'
	edit_allshots_out_path_TMP = os.path.abspath(edit_allshots_out_path_TMP)
	cmd = ffmgeg_path + ' -r 25 -f concat -safe 0 -i ' + edit_allshots_prw_path + ' -i ' + sedit_filename_path + ' -c:v libx264 -c:a aac -pix_fmt yuv420p -profile baseline -refs 2 -crf 21 -r 25 -shortest -y ' + edit_allshots_out_path_TMP 
	print  Fore.YELLOW + cmd + '\n'
	os.system(cmd)
	shutil.copy2(edit_allshots_out_path_TMP, edit_allshots_out_path)

def get_prw_by_flag(prw_list_complete, export_flag, sh_name):
	#processes_dict = {'3_post':['comp', 'comp2d', 'render'], '2_prod':['asmbl', 'anim', 'anim2d', 'layout', 'cut']}
	proc_sort_list_init = processes_dict['3_post'] + processes_dict['2_prod']
	#proc_sort_list = ['comp', 'render', 'anim', 'layout', 'cut']
	proc_sort_list = proc_sort_list_init
	#print 'DEBUG prw_list_complete'
	#pprint(prw_list_complete)

	#get preview if export_flag is 'by TIME'
	if export_flag not in proc_sort_list:
		print 'get_preview_framecount by time ...'
		prw_list_complete_expanded = [el for lst in [i.values() for i in prw_list_complete.values()] for el in lst]
		prw_by_flag = sorted(prw_list_complete_expanded, key=lambda k: k['time'], reverse=True)[0]
		return prw_by_flag
	
	#get preview if export_flag was set
	try:
		prw_by_flag = prw_list_complete[sh_name][export_flag]
	except KeyError:
		prw_by_flag = []

	#get preview if given export_flag doesnt exist, find it by brute force'
	while not prw_by_flag:
		proc_sort_list = proc_sort_list[proc_sort_list.index(export_flag)+1:]
		if proc_sort_list == []:
			#proc_sort_list = ['comp', 'render', 'anim', 'layout', 'cut']
			proc_sort_list = proc_sort_list_init
			proc_sort_list.reverse()
		export_flag = proc_sort_list[0]
		try:
			prw_by_flag = prw_list_complete[sh_name][export_flag]
		except KeyError:
			prw_by_flag = []
	else:
		print 'get_preview_framecount by proc:', prw_by_flag
		return prw_by_flag

def make_log(EP_JOB_LIST):
	gui_log = []
	for task in EP_JOB_LIST:
		error_log = ''
		epname = task['edit_filename_path'].rsplit('\\',1)[1].rsplit('_',3)[0].upper()
		eppart = ''
		color = ''
		if epname == 'ID001':
			eppart = 'intro'
		elif epname == 'ID555':
			eppart = 'songs'

		if task['job_type'] == 'update' and color != 'red':
			bg_color = 'green'
		else:
			bg_color = 'white'

		if task['error_code']['SG'] == 1:
			color = 'red'
			bg_color = 'pink'
			error_log = 'SG: ' + str(task['SG_frame_count']) + ' frames'
		else:
			color = 'black'
		

		#print '{col} {eppart} |{shot} ==> frame count: {frames}'.format(col=color, eppart=eppart, shot = task['edit_filename_path'].rsplit('\\',1)[1].rsplit('_',2)[0].upper(), frames = task['prw_frame_count'])
		#gui_log.append(color  + ' {eppart} |{shot} ==> frame count: {frames}'.format(eppart=eppart, shot = task['edit_filename_path'].rsplit('\\',1)[1].rsplit('_',2)[0].upper(), frames = task['prw_frame_count_log']))
		gui_log.append({'shot':task['edit_filename_path'].rsplit('\\',1)[1].rsplit('_',2)[0].upper(),
						'frames':task['prw_frame_count'],
						'eppart':eppart,
						'prw_filename_path':task['prw_filename_path'],
						#'bg_color':bg_color,
						'job_type':task['job_type'],
						'prw_proc':task['prw_proc'],
						'previous_prw_proc':task['previous_prw_proc'],
						'error_log':error_log})

	#ep_length = sum([i['prw_frame_count'] for i in EP_JOB_LIST])
	return gui_log

def get_episode_length(EP_JOB_LIST):
	ep_length_by_sg = sum([i['SG_frame_count'] for i in EP_JOB_LIST])
	ep_length_by_prw = sum([i['prw_frame_count'] for i in EP_JOB_LIST])
	return ep_length_by_sg, ep_length_by_prw

def run_global_list(EP_JOB_LIST, render_seq_flag, force_upd_flag=False):
	#list with all exported sequences paths and framecount statuses: ["file '\\\\path_to_edit_dir\\id001_sh9104_edit_%04d.png'", <framecount>, <framecoutn with log>] 
	allshots_prw_lst = []
	#print 'EP_JOB_LIST'
	#pprint(EP_JOB_LIST)
	for task in EP_JOB_LIST:
		#print '\n'
		#print 'DEBUG start'
		#pprint(allshots_prw_lst)
		#print 'JOB TYPE', task['job_type']
		#print 'SHOT NAME', task['sh_name']
		prw_files_list_to_del = task['prw_files_list_to_del']
		ver_filename_path = task['ver_filename_path']
		edit_filename_path = task['edit_filename_path']
		prw_container = task['prw_container']
		prw_frame_count = task['prw_frame_count']
		remove_overframes(prw_files_list_to_del)

		if force_upd_flag == True: task['job_type'] = 'update'

		if render_seq_flag == True:
			concat_string = "file '" + edit_filename_path + "'"
		else:
			concat_string = "file '" + task['prw_filename_path'] + "'"

		if task['job_type'] == 'update' and render_seq_flag == True:
			print 'START RENDER SEQUENCE\n', task['cmd']
			'''start update sequence'''
			os.system(task['cmd'])
		elif task['job_type'] == 'empty':
			concat_string = None
		
		if concat_string:
			allshots_prw_lst.append(concat_string)
			update_version_file(ver_filename_path, edit_filename_path, prw_container, prw_frame_count)

	#raw_input("Press the <ENTER> key to continue...")
	return allshots_prw_lst

def make_prw_container(prw_list_complete, export_flag, sh_name):
	prw_container = version_file_dict
	#if len([j for i,j in prw_list_complete.values()[0].iteritems() if j != 'no prw']) > 0:
	if prw_list_complete.values() != ['empty']:
		prw_container = get_prw_by_flag(prw_list_complete, export_flag, sh_name)
		prw_filename_path = os.path.join(prw_container['path'], prw_container['filename'])
		prw_container['framecount'] = get_preview_framecount(prw_filename_path)
		#print 'make_prw_container with framecount >>>', prw_container, '\n'
		print 'make_prw_container with framecount ...', '\n'
	else:
		print 'no any preview for shot', prw_list_complete.keys()[0]
		'''get shot name for empty shot from dict key'''
		prw_container['sh_name'] = prw_list_complete.keys()[0]
		prw_container['stage'] = 'empty'
	return prw_container
	
def init_editorial_export(ep, export_flag, ep_pattern, prj_name):
	#DEBUG()
	#global PRJ
	#PRJ = prj_name

	EP_JOB_LIST = []

	master_ep = get_master_ep(ep_pattern)#убрать, название эпизода должно приходить из GUI
	sedit = get_sedit(master_ep, prj_name)

	for i in ep_pattern:
		ep, sh = i.split('_', 1)

		''' get list of previews with all processes sorted by time and take the first preview: prw_list_complete = 
		[['id001_sh0101_comp_v017.mov', 1508168554.0, '3_post', 'comp', 97], ['id001_sh0101_render_v002.mov', 1507326908.0, '3_post', 'render', 97]
		, ['id001_sh0101_anim_v003.mov', 1507312039.0, '2_prod', 'anim', 97], ['id001_sh1201_cut_v001.mov', 1502707227.0, '2_prod', 'cut', 319]]
		'''		
		prw_list_complete = get_shot_prws2(sh, ep, prj_name)
		prw_container = make_prw_container(prw_list_complete, export_flag, sh)
		print 'PREVIEW TO EDIT >>> ', prw_container['filename']

		#update "edit" sequence
		make_ep_job_list(sh, prw_container, ep, EP_JOB_LIST, prj_name)
	#pprint(EP_JOB_LIST)
	return EP_JOB_LIST, sedit
