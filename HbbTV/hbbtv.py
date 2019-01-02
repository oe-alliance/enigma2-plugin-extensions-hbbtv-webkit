from Screens.Screen import Screen
from Screens.ChannelSelection import ChannelSelection
from Components.ActionMap import ActionMap
from enigma import eTimer, eServiceReference
from boxbranding import getMachineBuild

import os, struct, vbcfg

from vbipc import VBController

class HbbTVWindow(Screen):
	skin = """
		<screen name="HbbTVWindow" position="0,0" size="1280,720" backgroundColor="transparent" flags="wfNoBorder" title="HbbTV Plugin">
		</screen>
		"""
	def __init__(self, session, url=None, app_info=None):
		from enigma import getDesktop
		self.width = getDesktop(0).size().width()
		self.height = getDesktop(0).size().height()
		
		if (self.width > 1920):
			self.width = 1920
		elif (self.width < 720):
			self.width = 720
			
		if (self.height > 1080):
			self.height = 1080
		elif (self.height < 576):
			self.height = 576
		
		vbcfg.g_vmpegposition = vbcfg.getvmpegPosition()
		vbcfg.g_position = vbcfg.getPosition()
		vbcfg.osd_lock()

		Screen.__init__(self, session)

		self._url = url
		self._info = app_info

		if getMachineBuild() in ('dags7252'):
			self.servicelist = self.session.instantiateDialog(ChannelSelection)

		self.onLayoutFinish.append(self.start_hbbtv_application)

		self._close_timer = eTimer()
		self._close_timer.callback.append(self.stop_hbbtv_application)

		try:
			if self._cb_set_title not in vbcfg.g_main.vbhandler.onSetTitleCB:
				vbcfg.g_main.vbhandler.onSetTitleCB.append(self._cb_set_title)
		except Exception:
			pass

		try:
			if self._cb_close_window not in vbcfg.g_main.vbhandler.onCloseCB:
				vbcfg.g_main.vbhandler.onCloseCB.append(self._cb_close_window)
		except Exception:
			pass


	def _cb_set_title(self, title=None):
		vbcfg.DEBUG("pate title: %s" % title)
		if title is None:
			return
		self.setTitle(title)

	def _cb_close_window(self):
		self._close_timer.start(1000)

	def start_hbbtv_application(self):
		#print "=========== start_hbbtv_application  ================"
		vbcfg.g_main.vbhandler.soft_volume = -1
		self.setTitle(_('HbbTV Plugin'))
		vbcfg.DEBUG("Starting HbbTV")

		#vbcfg.DEBUG("url : %s" % self._url and self._url)
		vbcfg.DEBUG("info: %s" % self._info and self._info)

		if self._info and self._info["control"] == 1 and vbcfg.g_channel_info is not None:
			os.system("run.sh restart %d %d %s" % (self.width, self.height, self._info["url"]))
		else:
			if self._url is not None:
				os.system("run.sh restart %d %d %s" % (self.width, self.height, self._url))
			else:
				os.system("run.sh restart %d %d %s" % (self.width, self.height, self._info["url"]))
				
		vbcfg.g_main._timer_update_video_size.start(100)


	def stop_hbbtv_application(self):
		#print "=========== stop_hbbtv_application  ================"
		self._close_timer.stop()
		self._close_timer = None
		
		vbcfg.g_main._timer_update_video_size.stop()

		try:
			if self._cb_set_title in vbcfg.g_main.vbhandler.onSetTitleCB:
				vbcfg.g_main.vbhandler.onSetTitleCB.remove(self._cb_set_title)
		except Exception:
			pass

		try:
			if self._cb_close_window in vbcfg.g_main.vbhandler.onCloseCB:
				vbcfg.g_main.vbhandler.onCloseCB.remove(self._cb_close_window)
		except Exception:
			pass

		from enigma import getDesktop, gMainDC
		dsk = getDesktop(0)
		desktop_size = dsk.size()
		gMainDC.getInstance().setResolution(desktop_size.width(), desktop_size.height())

		#print "========= stop_hbbtv_application:: g_position: ", vbcfg.g_position, "  ==================="
		vbcfg.setvmpegPosition(vbcfg.g_vmpegposition)
		vbcfg.setPosition(vbcfg.g_position)
		vbcfg.osd_unlock()
		dsk.paint()

		if getMachineBuild() not in ('dags7252'):
			vbcfg.set_bgcolor("0")
		vbcfg.DEBUG("Stop HbbTV")

		os.system("run.sh stop")

		if getMachineBuild() in ('dags7252'):
			cur_channel = self.servicelist.getCurrentSelection()
			cur_channel = cur_channel.toString()
			self.session.nav.playService(eServiceReference(cur_channel))

		self.close()

