

'''
Skype Auto Answer is to Answer the Skype incoming call automatically

@author: John Chen (johnsofteng at gmail.com) 
@requires: Python 2.6 or newer (not yet 3.0) , Skype4Py webpage<https://developer.skype.com/wiki/Skype4Py>} 
@license: GPL License (see the accompanying LICENSE file for more information) 
@copyright: S{copy} 2009-2010 John Chen

'''

import sys, time
import Skype4Py

AllowedCallTargets = set (['echo123', 'echo223']);



class receive_set:
    def __init__(self):
        pass
    def OnCall(self, call, status):
        print "status is ", status, " Peer is: ", call.PartnerHandle, " Show name is ", call.PartnerDisplayName
        print "length of active calls are ",len(self.skype.ActiveCalls)
        inprogress = False
        if (status == Skype4Py.clsRinging) and (call.Type == Skype4Py.cltIncomingP2P or call.Type == Skype4Py.cltIncomingPSTN):
            for curr in self.skype.ActiveCalls:
                print "Call status is ", curr.Type, " status is ", curr.Status
                if curr.Status == Skype4Py.clsInProgress :
                    inprogress = True
            if not inprogress:
                call.Answer()
        if (status == Skype4Py.clsInProgress):
            print "Call's video send status is ",call.VideoSendStatus, " Recv status is ", call.VideoReceiveStatus, " Video Status is ",call.VideoStatus
#            cmd  = self.skype.Command("ALTER CALL <id> START_VIDEO_SEND")
#            self.skype.SendCommand(cmd)

#        if (status == "ROUTING") and (not call.PartnerHandle in AllowedCallTargets):
 #           call.Finish()
  #          print 'Terminating call'

    def OnCallVideoReceiveStatusChanged(self, status):
        pass

    def OnCallVideoSendStatusChanged(self, status):
        pass

    def OnCallVideoStatusChanged(self, status):
        pass

    def OnAttach(self, status):
        print 'API attachment status:'+self.skype.Convert.AttachmentStatusToText(status)
        if status == Skype4Py.apiAttachAvailable:
            self.skype.Attach()
            
    def start(self):
        self.skype = Skype4Py.Skype()
        self.skype.OnAttachmentStatus = self.OnAttach
        self.skype.OnCallStatus = self.OnCall


    def Attach(self):
        self.skype.Attach()

    def Callout(self, callee):
        self.skype.PlaceCall(callee)


if __name__ == "__main__":
    rec = receive_set()
    rec.start()
    rec.Attach()

    while 1:
        time.sleep(1)
    
