
#skype auto answer GUI


'''
Skype Auto Answer is a tool can Answer the specified Skype incoming call automatically

@author: John Chen (johnsofteng at gmail.com)
@requires: Python 2.6 or newer (not yet 3.0) <http://www.python.org/>,
            Skype4Py 1.0.31.0 <https://developer.skype.com/wiki/Skype4Py>,
            wxPython 2.8.10.1 <http://www.wxpython.org/>
            skype 3.8.0.188(Windows XP/Vista)
@website: http://skypeautoanswer.sourceforge.net/
@license: GPL License (see the accompanying LICENSE file for more information)
@copyright: S{copy} 2009-2010 John Chen

'''

import wx
import sys, re
import time
import Skype4Py
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin

__version__ = '0.0.1'
__author__ = 'John Chen'
__email__ =' johnsofteng at gmail.com'
__license__ = 'GNU GPL License <http://www.gnu.org/copyleft/gpl.html>'
__description__ = '''
Skype Auto Answer is a tool
which can Answer the specified Skype incoming
call automatically'''
__website__ ='http://skypeautoanswer.sourceforge.net/'
__abouticon__ = 'res/SkypeHeadset.png'
__copyright__ = '(C) 2009-2010 John Chen'

exe_name = "Skype Auto Answer"
ID_EXIT = 1
ID_ABOUT = 2

ID_ADD_TO = 3
ID_DELETE_BACK = 4

skypeid = re.compile(u"\(([\w.,]{5,151})\)\s*$")

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent,size):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER)
        ListCtrlAutoWidthMixin.__init__(self)

class SkypeAutoAnswer(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(590, 400),
                          style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION |	 wx.CLOSE_BOX)

        self.buddylist = {}
        self.buddy_index = 0
        self.answer_set = set()
        self.video_auto_send = True
        menu_file = wx.Menu()
        menu_file.Append(ID_EXIT, '&Quit\tCtrl+Q',"Quit %s"%exe_name)

        menu_help = wx.Menu()
        menu_help.Append(ID_ABOUT, '&About', "About %s"%exe_name)
        
        menubar = wx.MenuBar()
        menubar.Append(menu_file, '&File')
        menubar.Append(menu_help, '&Help')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnAbout, id=ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnExit, id=ID_EXIT)

        panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)


        hbox_personal = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(panel, -1, 'Skype User')
        hbox_personal.Add(st1, 0, wx.TOP|wx.LEFT|wx.RIGHT, 5)
        self.tc_user = wx.TextCtrl(panel, -1,style=wx.TE_READONLY)
#        self.tc_user.SetEditable(False)
        self.tc_user.SetBackgroundColour(panel.GetBackgroundColour())
        self.tc_user.SetValue("Echo123")
        hbox_personal.Add(self.tc_user, -1)
        
        vbox.Add(hbox_personal, 0, wx.TOP|wx.BOTTOM, 5)
        
        hbox_top = wx.BoxSizer(wx.HORIZONTAL)
        

        friend_list = wx.StaticBox(panel, -1, 'Friends List')
        friendlist_boxsizer = wx.StaticBoxSizer(friend_list, wx.VERTICAL)
        self.friends = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER,size=(240, 180))
#        self.friends = AutoWidthListCtrl(panel,(240, 180))
        self.friends.InsertColumn(0, "", width=215)
        friendlist_boxsizer.Add(self.friends)
        friendlist_boxsizer.Add(wx.StaticLine(panel, -1,size=(240, -1)),flag=wx.TOP|wx.BOTTOM,border=5)
        friendlist_boxsizer.Add(wx.StaticText(panel, -1, 'ID not in friend list'),flag=wx.BOTTOM,
                                border = 5)
        self.not_friend_tc = wx.TextCtrl(panel, -1,size=(240, -1))
        self.not_friend_tc.SetEditable(False)
        self.not_friend_tc.SetBackgroundColour(panel.GetBackgroundColour())
        friendlist_boxsizer.Add(self.not_friend_tc)
        hbox_top.Add(friendlist_boxsizer, 0, wx.TOP|wx.LEFT, 10)


        action_buttons = wx.BoxSizer(wx.VERTICAL)
        self.buttonAddTo = wx.Button(panel, ID_ADD_TO, '>>', size=(50,28))
        self.buttonDeleteBack = wx.Button(panel, ID_DELETE_BACK, '<<', size=(50,28))
        action_buttons.Add(self.buttonAddTo, 0, flag=wx.TOP, border=40)
        action_buttons.Add(self.buttonDeleteBack,0, flag=wx.TOP, border=40)
        hbox_top.Add(action_buttons, 0, flag=wx.LEFT|wx.RIGHT, border=5)

        self.Bind(wx.EVT_BUTTON, self.OnAddTo, id = ID_ADD_TO)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteBack, id = ID_DELETE_BACK)

        answer_list = wx.StaticBox(panel, -1, 'Auto Answer List')
        answerlist_boxsizer = wx.StaticBoxSizer(answer_list, wx.VERTICAL)
        self.answers = wx.ListCtrl(panel, -1, style=wx.LC_REPORT|wx.LC_NO_HEADER,size=(240, 230))
        self.answers.InsertColumn(0, "", width=215)
        answerlist_boxsizer.Add(self.answers,1)

        hbox_top.Add(answerlist_boxsizer, 1, wx.TOP|wx.RIGHT,10)

#        hbox_top.Add(wx.StaticText(panel, -1, "hello", (5,5)), 1, wx.RIGHT, 5)

        vbox.Add(hbox_top, 0, wx.BOTTOM, 5)
        #vbox.Add(sometime, 1, wx.BOTTOM, 100)
        
        panel.SetSizer(vbox)

        
        self.skype = Skype4Py.Skype()
        self.skype.OnAttachmentStatus = self.OnAttach
        self.skype.OnCallStatus = self.OnCall
        self.skype.OnCallVideoSendStatusChanged = self.OnCallVideoSendStatusChanged
#        self.skype.OnCallVideoStatusChanged = self.OnCallVideoStatusChanged
        self.Attach()

        self.Centre()
        self.Show(True)

    def Attach(self):
        self.skype.Attach()
        
    def OnAttach(self, status):
       # print 'API attachment status: '+ self.skype.Convert.AttachmentStatusToText(status)
        if status == Skype4Py.apiAttachAvailable:
            self.skype.Attach()
        elif status == Skype4Py.apiAttachSuccess:
            if(len(self.skype.CurrentUser.DisplayName) != 0):
                self.tc_user.SetValue(self.skype.CurrentUser.DisplayName)
            elif(len(self.skype.CurrentUser.FullName) !=0):
                self.tc_user.SetValue(self.skype.CurrentUser.FullName)
            else:
                self.tc_user.SetValue(self.skype.CurrentUser.Handle)
            for friend in self.skype.Friends:
#                self.friends.InsertStringItem(sys.maxint, friend.Handle)
                if(len(friend.DisplayName) != 0):
                    index = self.friends.InsertStringItem(sys.maxint, friend.DisplayName+'('+friend.Handle+')')
                elif(len(friend.FullName) != 0):
                    index = self.friends.InsertStringItem(sys.maxint, friend.FullName+'('+friend.Handle+')')                
                else:
                    index = self.friends.InsertStringItem(sys.maxint, friend.Handle+'('+friend.Handle+')')
#                self.friends.SetItemData(index, index)


    def OnExit(self, event):
        dlg = wx.MessageDialog(self, 'Are you sure to quit %s?'%exe_name,
                               'Please Confirm', wx.YES_NO|wx.NO_DEFAULT|wx.ICON_QUESTION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Close(True)

    def OnAbout(self, event):
        about = wx.AboutDialogInfo()

        about.SetIcon(wx.Icon(__abouticon__, wx.BITMAP_TYPE_PNG))
        about.SetName(exe_name)
        about.SetVersion(__version__)
        about.SetDescription(__description__)
        about.SetCopyright(__copyright__)
        about.SetWebSite(__website__)
        about.SetLicence(__license__)
        about.AddDeveloper(__author__)

        wx.AboutBox(about)
#        dlg = wx.MessageDialog(self, exe_name+'\t\n''2009\t','About',
#                               wx.OK|wx.ICON_INFORMATION)
#        dlg.ShowModal()
#        dlg.Destroy()

    def OnAddTo(self, event):
        #print "OnAdd to"
        item = -1
        selected_count = self.friends.GetSelectedItemCount()
        if(selected_count == 0):
         #   print "No body is selected in friends"
            return
        else:
            item = self.friends.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            while item != -1:
                select_item = self.friends.GetItemText(item)
                reg_ret = skypeid.findall(select_item)
                if len(reg_ret) == 1:
                    select_user = reg_ret[0]
              #      print "item selected: "+select_user
                    if select_user in self.answer_set:
               #         print "already in the set"
                        pass
                    else:
                #        print "Add to the set"
                        self.answer_set.add(select_user)
                        self.answers.InsertStringItem(sys.maxint, select_item)
                item = self.friends.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

            for i in reversed(range(0,self.friends.GetItemCount())):
                if self.friends.GetItemState(i, wx.LIST_STATE_SELECTED):
#                    print self.friends.GetItemText(i)+" is selected?"
                    self.friends.DeleteItem(i)
                
        self.friends.RefreshItems(0,self.friends.GetItemCount() - 1)
        
    def OnDeleteBack(self, event):
#        print "On Delete Back"
        item = -1
        selected_count = self.answers.GetSelectedItemCount()
        if(selected_count == 0):
#            print "No body is selected in answer_list"
            return
        else:
            item = self.answers.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            while item != -1:
                select_item = self.answers.GetItemText(item)
                reg_ret = skypeid.findall(select_item)
                if len(reg_ret) == 1:
                    select_user = reg_ret[0]
    #                print "item selected: "+select_user
                    if select_user in self.answer_set:
    #                    print "already in the set, remove it"
                        self.answer_set.remove(select_user)
                        self.friends.InsertStringItem(sys.maxint, select_item)
                    else:
                        pass
    #                    print "it is not in the set"
                item = self.answers.GetNextItem(item, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

            for i in reversed(range(0,self.answers.GetItemCount())):
                if self.answers.GetItemState(i, wx.LIST_STATE_SELECTED):
#                    print self.answers.GetItemText(i)+" is selected?"
                    self.answers.DeleteItem(i)
                
        self.answers.RefreshItems(0,self.answers.GetItemCount() - 1)

    def OnCall(self, call, status):
#        print "status is ", status, " Peer is: ", call.PartnerHandle, " Show name is ", call.PartnerDisplayName
#        print "length of active calls are ",len(self.skype.ActiveCalls)
        inprogress = False
        if (status == Skype4Py.clsRinging) and (call.Type == Skype4Py.cltIncomingP2P or call.Type == Skype4Py.cltIncomingPSTN):
            for curr in self.skype.ActiveCalls:
#                print "Call status is ", curr.Type, " status is ", curr.Status
                if curr.Status == Skype4Py.clsInProgress :
                    inprogress = True
            if not inprogress and call.PartnerHandle in self.answer_set:
                call.Answer()
        if (status == Skype4Py.clsInProgress):
#            pass
            if self.video_auto_send == True and (call.VideoStatus == Skype4Py.cvsSendEnabled or call.VideoStatus == Skype4Py.cvsBothEnabled) and call.VideoSendStatus == Skype4Py.vssAvailable:
                call.StartVideoSend()
            
#            print "Call's video send status is ",call.VideoSendStatus, " Recv status is ", call.VideoReceiveStatus, " Video Status is ",call.VideoStatus

    def OnCallVideoStatusChanged(self, call, status):
#        print call," new video status is ",status
        if self.video_auto_send == True and (call.VideoStatus == Skype4Py.cvsSendEnabled or call.VideoStatus == Skype4Py.cvsBothEnabled) and status == Skype4Py.vssAvailable:
            call.StartVideoSend()

    def OnCallVideoSendStatusChanged(self, call, status):
#        print call," new status is ",status
        if self.video_auto_send == True and status == Skype4Py.vssAvailable and (call.PartnerHandle in self.answer_set) and (call.Type == Skype4Py.cltIncomingP2P or call.Type == Skype4Py.cltIncomingPSTN):
            call.StartVideoSend()

app = wx.App()
frame_icon = wx.Icon('res/frameico.ico', wx.BITMAP_TYPE_ICO)
frame = SkypeAutoAnswer(None, -1, exe_name)
frame.SetIcon(frame_icon)
app.MainLoop()
