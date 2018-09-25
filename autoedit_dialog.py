# -*- coding: utf-8 -*-
import os, sys
import time
from PySide.QtUiTools import QUiLoader
from PySide.QtCore import QFile, QProcess

#sys.path.append(r'D:\Work\Scripts\python')
sys.path.append(os.path.join(os.path.dirname(__file__), "autoedit_main"))
#sys.path.append(os.path.join(os.path.dirname(__file__), "autoedit_mk_struct"))
import autoedit_main
import autoedit_mk_struct
import parse_xml
import media_info
import datetime

from PySide import QtCore, QtGui

class AutoeditDlg(QtGui.QWidget):

	def __init__(self):
		super(AutoeditDlg, self).__init__()

		self.initUI()

	def initUI(self):
		self.setWindowTitle('Autoedit Tool')


		self.loader = QUiLoader()
		uifile = QFile("dlg_ui.ui")
		uifile.open(QFile.ReadOnly)
		self.dialog = self.loader.load(uifile, parentWidget=self)
		uifile.close()

		self.dialog.run_button.clicked.connect(self.start_export)
		self.dialog.proc_comboBox.currentIndexChanged.connect(self.get_export_proc)
		self.dialog.prj_comboBox.currentIndexChanged.connect(self.load_episodes)
		self.dialog.ep_list.itemDoubleClicked.connect(self.read_config)
		self.dialog.ep_list.itemClicked.connect(self.loadPattern)
		self.dialog.folders_pushButton.clicked.connect(self.make_folders)
		self.dialog.xml_pushButton.clicked.connect(self.parse_xml)
		self.dialog.pushButton_updateseq.clicked.connect(self.start_update)
		self.dialog.debugButton.clicked.connect(self.debug)
		#self.dialog.ep_list.itemClicked.connect(self.clear)

		self.timer = QtCore.QTimer(self)
		self.show()
		self.load_episodes()

		#red_c = QtGui.QColor('red')
		#self.dialog.logOutput.setTextColor(red_c)
		#self.dialog.logOutput.append('TST')

	def load_episodes(self):
		self.dialog.ep_list.clear()
		#self.dialog.logOutput.append('loading..')
		self.prj_name = self.dialog.prj_comboBox.currentText()
		print 'send pro_name from gui', self.prj_name
		episodes = autoedit_main.get_all_prj_eps(self.prj_name)
		for ep in episodes:
			descr = ep[1]
			if ep[1] == None: descr = '' 
			self.dialog.ep_list.addItem(ep[0] + '	' + unicode(descr, "utf-8"))

	def loadPattern(self):
		self.dialog.plainTextEdit_pattern.clear()
		self.ep = self.dialog.ep_list.currentItem().text().split('\t')[0]
		if self.prj_name == 'woo-woo': self.prj_name = 'woowoo'
		ep_pattern = autoedit_main.get_ep_pattern(self.ep, self.prj_name)
		for i in ep_pattern:
			self.dialog.plainTextEdit_pattern.appendPlainText(i)

	def updatePattern(self):
		return [i for i in self.dialog.plainTextEdit_pattern.toPlainText().split('\n')]

	def parse_xml(self):
		if self.prj_name == 'woowoo': self.prj_name = 'woo-woo'
		xml_path = os.path.join(autoedit_main.configure_path(prj_name=self.prj_name, ep=self.ep, proc='1_pre'), 'animatic\\xml')
		xmlfilename = autoedit_main.get_latest_filename(xml_path, self.ep+'_eppattern', chk_ext='xml')
		xmlfilename_path = os.path.join(xml_path, xmlfilename)
		print 'found latest xml:', xmlfilename_path
		if self.prj_name == 'woo-woo': self.prj_name = 'woowoo'
		parse_xml.init_parsing(xmlfilename_path, self.ep, self.prj_name)
		
	def make_folders(self):
		ep_pattern = self.updatePattern() 
		while len(ep_pattern) > 0:
			for shot in ep_pattern:
				shot = shot.split('_')[1]
				path = autoedit_main.configure_path(prj_name=self.prj_name, sh_name=shot, prw='', proc='2_prod', edt='', filenm ='', ep=self.ep)
				#autoedit_mk_struct.init_struct(path)
				autoedit_mk_struct.check_path(path)

	def get_export_proc(self):
		return self.dialog.proc_comboBox.currentText()

	def findSet(self, typeObj, names):
		array = []
		for n in names:
			array.append(self.dialog.findChild(typeObj, n))
			if array[-1] == None:
				print "Can't find", n
		return array

	def write_log(self, ep_length_timecode, sedit):
		self.dialog.logOutput.clear()
		self.dialog.logOutput.setTextBackgroundColor(QtGui.QColor('yellow'))
		self.dialog.logOutput.append('START UPDATE: ' + self.ep)
		self.dialog.logOutput.append('Episode duration: ' + ep_length_timecode)
		self.dialog.logOutput.append('Episode sound: ' + sedit + '\n')

		html_main = """
						<html>
						<style type="text/css">
							p {color: red}
							div {color: blue}
							.bold {
								font-weight: 600;
									}
							.error {
								color: red;
								background: pink;
									}
						</style>
						<body>   
						<p>---------------------</p>
						CONTENT
						</body>   
						</html>
					"""
		html_text = []
		for task in self.EP_JOB_LIST:
			#shot_name = task['edit_filename_path'].rsplit('\\',1)[1].rsplit('_',2)[0].upper()
			shot_name = task['sh_name']
			frames = task['prw_frame_count']
			epname = task['edit_filename_path'].rsplit('\\',1)[1].rsplit('_',3)[0].upper()
			prw_proc = task['prw_proc']
			previous_prw_proc = task['previous_prw_proc']
			previous_prw_framecount = task['previous_prw_framecount']
			prw_frame_count = task['prw_frame_count']

			prw_datetime = datetime.datetime.fromtimestamp(task['prw_container']['time'])
			prw_date = prw_datetime.date().strftime('%d %b')
			prw_time = prw_datetime.time().strftime('%H:%M')
			#print 'DEBUG date', prw_datetime.date().strftime('%d %b')
			#print 'DEBUG date', prw_datetime.time().strftime('%H:%M')
			#print 'DEBUG date', datetime.date.today()
			if prw_date == datetime.date.today().strftime('%d %b'):
				prw_date = 'today'
			prw_dt = str(prw_date)+' '+str(prw_time)

			color = 'black'
			error_log = ''
			eppart = 'ep'
			if epname == 'ID001':
				eppart = 'intro'
				color = 'Slategray'
			elif epname == 'ID555':
				eppart = 'songs'
				color = 'Slategray'
			if task['job_type'] == 'update':
				bg_color = 'Mediumaquamarine'
			elif task['job_type'] == 'keep':
				bg_color = 'white'
			elif task['job_type'] == 'empty':
				bg_color = 'Salmon'
			if task['error_code']['SG'] == 1:
				error_log += 'SG: ' + str(task['SG_frame_count']) + ' frames'
			elif task['error_code']['LAST_SYNC'] == 1:
				error_log += 'LAST SYNC: ' + str(task['previous_prw_framecount']) + ' frames'
			
			#prog = 'explorer.exe'
			#args = [prw_filename_path]	
			#my_proc =  QProcess(self)
			#my_proc.start(prog, args)
			html_text.append('''<div style="color:{col};background:{bgcol}">
									<span class="bold">{ep}</span>&nbsp;&nbsp;{sh}&nbsp;&nbsp;&nbsp;&nbsp;
									{fr} frames&nbsp;&nbsp;&nbsp;&nbsp;
									<span class="bold">&nbsp;&nbsp;&nbsp;&nbsp;{last_prw}->{prw}</span>    
									&nbsp;&nbsp;<span class="error">{el}</span><span>    {dt}</span></div>

							'''.format(ep=eppart,
										sh=shot_name,
										fr=frames,
										el=error_log,
										prw=prw_proc,
										last_prw=previous_prw_proc,
										bgcol=bg_color,
										col=color,
										dt=prw_dt))

			#self.dialog.logOutput.append('{ep} {sh}    {fr}    {last_prw}->{prw}    {ec}'.format(ep=eppart, sh=shot_name, fr=str(frames)+' frames', ec=error_log, prw=prw_proc, last_prw=previous_prw_proc))
		ss = ''.join(html_text)
		#print '__', ss, '\n'
		self.dialog.logOutput.setHtml(html_main.replace('CONTENT', ss))
		
	def read_config(self):
		print 'START read_config'

		self.prj_name = self.dialog.prj_comboBox.currentText()
		self.ep = self.dialog.ep_list.currentItem().text()
		print self.prj_name
		print self.ep

		export_flag = self.get_export_proc()
		ep_pattern = self.updatePattern() 

		if self.prj_name == 'woowoo': self.prj_name = 'woo-woo'
		print 'send self.prj_name to init_editorial_export', self.prj_name
		self.EP_JOB_LIST, sedit = autoedit_main.init_editorial_export(self.ep, export_flag, ep_pattern, self.prj_name)
		QtGui.qApp.processEvents()

		gui_log = autoedit_main.make_log(self.EP_JOB_LIST)
		self.ep_length, ep_length_by_prw = autoedit_main.get_episode_length(self.EP_JOB_LIST)
		ep_length_timecode = media_info.frames_to_timecode(self.ep_length, start='00:00:00:00')
		ep_length_by_prw_timecode = media_info.frames_to_timecode(ep_length_by_prw, start='00:00:00:00')

		#self.write_log(gui_log, ep_length_timecode, sedit)
		self.write_log(ep_length_timecode, sedit)
		pal = QtGui.QPalette(self.dialog.label_ep_info.palette())
		self.dialog.label_ep_info.setAutoFillBackground(True)
		if self.ep_length != 8250:
			pal.setColor(QtGui.QPalette.Window, QtGui.QColor('red'))
		else:
			pal.setColor(QtGui.QPalette.Window, QtGui.QColor('gray'))
		self.dialog.label_ep_info.setPalette(pal)
		self.dialog.label_ep_info.setText(self.ep + '\n SG timecode: ' + ep_length_timecode + '\n PRW timecode: ' + ep_length_by_prw_timecode + '\n' + sedit)
		#return ep_pattern, ep_length, EP_JOB_LIST

	def start_export(self):
		self.pre_export()
		ep_pattern = self.updatePattern() 
		render_seq_flag = self.dialog.renderSeq.isChecked()
		allshots_prw_lst = autoedit_main.run_global_list(self.EP_JOB_LIST, render_seq_flag)
		if self.prj_name == 'woowoo': self.prj_name = 'woo-woo'
		autoedit_main.export_autoedit(ep_pattern, allshots_prw_lst, self.prj_name)

	def start_update(self):
		self.dialog.renderSeq.setChecked(True)
		force_upd_flag = self.dialog.checkBox_forceupd.isChecked()
		self.pre_export()
		render_seq_flag = True
		#self.ep_pattern = self.dialog.plainTextEdit_pattern.toPlainText()
		allshots_prw_lst = autoedit_main.run_global_list(self.EP_JOB_LIST, render_seq_flag, force_upd_flag)

	def pre_export(self):
		#print self.EP_JOB_LIST
		try:
			self.EP_JOB_LIST
		except:
			self.read_config()
		#self.start_export(self.ep_pattern, self.ep_length, self.EP_JOB_LIST)
	
	def debug(self):
		print self.dialog.plainTextEdit_pattern.toPlainText()

def main():
	app = QtGui.QApplication(sys.argv)
	GUI = AutoeditDlg()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
