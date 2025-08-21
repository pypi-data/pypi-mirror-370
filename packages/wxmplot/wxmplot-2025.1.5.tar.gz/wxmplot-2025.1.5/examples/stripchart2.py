#!/usr/bin/python
import time
import numpy as np
import sys
import wx
from datetime import datetime
from wx.lib import masked
from floatcontrol import FloatCtrl
from wxmplot import PlotPanel


def next_data():
    "simulated data"
    t0 = time.time()
    lt = time.localtime(t0)
    dt0 = datetime.fromtimestamp(t0)

    tmin, tsec = lt[4], lt[5]
    u = np.random.random()
    v = np.random.random()
    x = np.sin( (u + tsec)/3.0) + tmin/30. + v/5.0
    return dt0, x


def next_data2():
    "simulated data"
    t0 = time.time()
    dt0 = datetime.fromtimestamp(t0)

    lt = time.localtime(t0)
    tmin, tsec = lt[4], lt[5]
    u = np.random.random()
    v = np.random.random()
    x = 13.0*np.sin((u + tsec)/1.0) + (tmin+tsec/10)/2. + v/2.
    return dt0, x

class StripChartFrame(wx.Frame):
    def __init__(self, parent, ID, **kws):
        kws["style"] = wx.DEFAULT_FRAME_STYLE|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL

        wx.Frame.__init__(self, parent, ID, '',
                         wx.DefaultPosition, wx.Size(-1,-1), **kws)
        self.SetTitle("wxmplot StripChart Demo")

        self.tmin = 30.0

        self.SetFont(wx.Font(12,wx.SWISS,wx.NORMAL,wx.BOLD,False))
        menu = wx.Menu()
        menu_exit = menu.Append(-1, "E&xit", "Terminate the program")

        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File");
        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU,  self.OnExit, menu_exit)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        sbar = self.CreateStatusBar(2,wx.CAPTION)
        sfont = sbar.GetFont()
        sfont.SetWeight(wx.BOLD)
        sfont.SetPointSize(11)
        sbar.SetFont(sfont)
        self.SetStatusWidths([-3,-1])
        self.SetStatusText('',0)

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        btnpanel = wx.Panel(self, -1)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)

        b_on  = wx.Button(btnpanel, -1, 'Start',   size=(-1,-1))
        b_off = wx.Button(btnpanel, -1, 'Stop',    size=(-1,-1))

        b_on.Bind(wx.EVT_BUTTON, self.onStartTimer)
        b_off.Bind(wx.EVT_BUTTON, self.onStopTimer)

        tlabel = wx.StaticText(btnpanel, -1, '  Time range:')
        self.time_range = FloatCtrl(btnpanel,  size=(100, -1),
                                    value=abs(self.tmin), precision=1)

        btnsizer.Add(b_on,   0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)
        btnsizer.Add(b_off,  0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)
        btnsizer.Add(tlabel, 1, wx.GROW|wx.ALL|wx.ALIGN_LEFT|wx.LEFT, 0)
        btnsizer.Add(self.time_range, 0, wx.ALIGN_LEFT|wx.ALIGN_CENTER|wx.LEFT, 0)

        btnpanel.SetSizer(btnsizer)
        btnsizer.Fit(btnpanel)

        self.plotpanel = PlotPanel(self, messenger=self.write_message)
        self.plotpanel.BuildPanel()
        self.plotpanel.set_xlabel('Time from Present (s)')
        mainsizer.Add(btnpanel, 0,  wx.GROW|wx.ALIGN_LEFT|wx.LEFT, 0)
        mainsizer.Add(self.plotpanel, 1, wx.GROW|wx.ALL|wx.ALIGN_LEFT|wx.LEFT, 0)
        self.SetSizer(mainsizer)
        mainsizer.Fit(self)

        self.timer1 = wx.Timer(self)
        self.timer2 = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer1, self.timer1)
        self.Bind(wx.EVT_TIMER, self.onTimer2, self.timer2)

        self.Refresh()
        self.SetSize(self.GetBestVirtualSize())

        wx.CallAfter(self.onStartTimer)

    def write_message(self, msg, panel=0):
        """write a message to the Status Bar"""
        self.SetStatusText(msg, panel)

    def onStartTimer(self,event=None):
        t0, y0 = next_data()
        self.tlist = [t0]
        self.ylist = [y0]

        t2, y2 = next_data2()
        self.t2list = [t2]
        self.y2list = [y2]
        self.tmin_last = -10000
        self.time0    = time.time()

        self.tmin_last = -10000
        self.time0    = time.time()
        self.timer1.Start(105)
        self.timer2.Start(187)

    def onStopTimer(self,event=None):
        self.timer1.Stop()
        self.timer2.Stop()

    def onTimer1(self, event):
        etime = time.time() - self.time0
        self.tmin = float(self.time_range.GetValue())
        t1, y1 = next_data()
        self.tlist.append(t1)
        self.ylist.append(y1)
        if isinstance(t1, datetime):
            t1 = t1.timestamp()
            ts = [dt.timestamp()for dt in self.tlist]
        else:
            ts = [dt for dt in self.tlist]

        del_ts = np.array(ts)-t1
        mask = np.where(del_ts > -abs(self.tmin))

        ydat = np.array(self.ylist)[mask]
        tdat = np.array(self.tlist)[mask]

        n = len(self.ylist)
        print("Y1 ", n, ydat.min(), ydat.max())
        if n <= 2:
            self.plotpanel.plot(tdat, ydat)
        else:
            self.plotpanel.update_line(0, tdat, ydat, draw=True)
            self.write_message("update  %i points in %8.4f s" % (n,etime), panel=0)

    def onTimer2(self, event):
        etime = time.time() - self.time0
        self.tmin = float(self.time_range.GetValue())
        t1, y1 = next_data2()
        self.t2list.append(t1)
        self.y2list.append(y1)
        if isinstance(t1, datetime):
            t1 = t1.timestamp()
            ts = [dt.timestamp()for dt in self.t2list]
        else:
            ts = [dt for dt in self.t2list]

        del_ts = np.array(ts)-t1
        mask = np.where(del_ts > -abs(self.tmin))

        ydat = np.array(self.y2list)[mask]
        tdat = np.array(self.t2list)[mask]

        n = len(self.y2list)
        print("Y2 ", n, ydat.min(), ydat.max())

        if n <= 2:
            self.plotpanel.plot(tdat, ydat, side='right', ylabel='y2')
        else:
            self.plotpanel.update_line(1, tdat, ydat, side='right', draw=True)
            self.write_message("update  %i points in %8.4f s" % (n,etime), panel=1)

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self, "wxmplot example: stripchart app",
                              "About WXMPlot test", wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        self.Destroy()

app = wx.App()
f = StripChartFrame(None,-1)
f.Show(True)
app.MainLoop()
#
