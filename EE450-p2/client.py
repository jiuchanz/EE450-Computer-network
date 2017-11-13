#!/usr/bin/env python

"""
EE450 Homework 1 Client - STUB
Dr. Genevieve Bartlett
Fall 2017
"""

# You are not required to use any of the code in this stub,
# however you may find it a helpful starting point.

from collections import deque
import time
import socket
import sys
import select
import re
global addresses
global ports
global  UDP_IP 
global UDP_PORT 

# In general, globals should be sparingly used if at all.
# However, for this simple program it's *ok*.
# You are not required to use these, but you may find them helpful.
our_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local_input = deque()






def run_loop():
    global our_socket, local_input, network_input, network_output,sendFlag,UDP_IP,UDP_PORT, ids,idsKnown,ips,ports,myPeerName, myIP,myPORT
    import copy
    watch_for_write = []
    watch_for_read = [sys.stdin, our_socket]
    MNUMCount=0
    MNUMArr={}
    MNUMTimes={}
    MNUMIP={}
    MNUMPort={}
    idsKnown=[]
    ips=[]
    ports=[]
    relayID=""
    
    while True:
        try:
            # Use select to wait for input from either stdin (0) or our
            # socket (i.e.  network input).  Select returns when one of the
            # watched items has input, or has outgoing buffer space or has
            # an error.
            
            input_ready, output_ready, except_ready = select.select(watch_for_read, watch_for_write, watch_for_read,3)
            MNUMTimesCopy=copy.copy(MNUMTimes)
            for k,v in MNUMTimes.items():
                if v<=5 :
                    if v==0:
                        MNUMTimesCopy[k]+=1
                        continue
                    data=MNUMArr[k];
                    
                    UDP_IP=MNUMIP[k]
                    UDP_PORT=int(MNUMPort[k])
                    
                    print("resend message: ",data)
                    our_socket.sendto(data.encode('utf-8'),(UDP_IP, UDP_PORT))
                    MNUMTimesCopy[k]+=1
                    print(v)
                else:
                    data=MNUMArr[k];
                    DST=re.findall("\d+",data)[1]
                    print("********************")
                    print("ERROR: Gave up sending to ",DST)
                    print("********************")
                    MNUMArr.pop(k)
                    MNUMTimesCopy.pop(k)
            MNUMTimes=MNUMTimesCopy
            
            for item in input_ready:
            	
                if item == sys.stdin:
                    MESSAGE = sys.stdin.readline().strip()
                    if MESSAGE=="ids":
                        UDP_IP = 'steel.isi.edu'
                        UDP_PORT = 63682
                        MESSAGE="SRC:"+myPeerName+";DST:999;PNUM:5;HCT:1;MNUM:002;VL:;MESG:get map"
                        our_socket.sendto(MESSAGE.encode('utf-8'),(UDP_IP, UDP_PORT))
                        data, server = our_socket.recvfrom(4096)
                        print("Got message %s" % data.decode('utf-8'))
                        MESG=data.decode('utf-8').split(";")[6] 
                        ids=re.findall("\d+",MESG.split("and")[0])

                        addressIP=MESG.split("and")[1].split(",")

                        idsKnown=[]
                        ips=[]
                        ports=[]
                        for x in addressIP:
                            idsKnown.append(x.split("=")[0])
                            ips.append(re.search(r"(?<=\=).*?(?=\@)", x).group(0))
                            ports.append(x.split("@")[1])
                        idsKnown.append(myPeerName)
                        ips.append(myIP)
                        ports.append(myPORT)


                        print("")
                        print("********************")
                        print("Recently Seen Peers:")
                        peersStr=""
                        for x in ids:
                            peersStr+=(x+",")

                        print(peersStr)
                        print("Known addresses:") 
                        for i,j,k in zip(idsKnown,ips,ports):
                            print(i,j,k)
                        print("********************")
                    elif MESSAGE[:3]=="msg":
                        DST=MESSAGE[4:7]
                        
                        
                        if DST in idsKnown:
                            UDP_IP=ips[idsKnown.index(DST)]
                            UDP_PORT=int(ports[idsKnown.index(DST)])
                            MESSAGE="SRC:"+myPeerName+";DST:"+DST+";PNUM:3;HCT:1;MNUM:"+format(MNUMCount, '03d')+";VL:;MESG:"+MESSAGE[8:]
                            MNUMArr[format(MNUMCount, '03d')]=MESSAGE;
                            MNUMTimes[format(MNUMCount, '03d')]=0;
                            MNUMPort[format(MNUMCount, '03d')]=UDP_PORT
                            MNUMIP[format(MNUMCount, '03d')]=UDP_IP
                            MNUMCount+=1;

                            our_socket.sendto(MESSAGE.encode('utf-8'),(UDP_IP, int(UDP_PORT)))

                        else:
                            VL=[]
                            VL.append(myPeerName)
                            VLstr=",".join(VL)
                            relayID=DST
                            for x in range(0,3):

                                UDP_IP=ips[x]

                                UDP_PORT=int(ports[x])
                                if UDP_IP==myIP and UDP_PORT==int(myPORT):
                                    continue
                                data="SRC:"+myPeerName+";DST:"+DST+";PNUM:3;HCT:9;MNUM:"+format(MNUMCount, '03d')+";VL:;MESG:"+MESSAGE[8:]
                                our_socket.sendto(data.encode('utf-8'),(UDP_IP, int(UDP_PORT)))
                                print(UDP_IP,UDP_PORT)
                                MNUMPort[format(MNUMCount, '03d')]=UDP_PORT
                                MNUMIP[format(MNUMCount, '03d')]=UDP_IP
                                MNUMArr[format(MNUMCount, '03d')]=data;
                                MNUMTimes[format(MNUMCount, '03d')]=0;
                                MNUMCount+=1;

                        
                       
                        
                        
                    elif MESSAGE[:3]=="all": 
                        MESSAGE=MESSAGE[4:]
                        for ID,UDP_IP,UDP_PORT in zip(idsKnown,ips,ports):
                            if ID==myPeerName:
                             continue
                            data="SRC:"+myPeerName+";DST:"+ID+";PNUM:7;HCT:1;MNUM:"+format(MNUMCount, '03d')+";VL:;MESG:"+MESSAGE
                            MNUMArr[format(MNUMCount, '03d')]=data;
                            MNUMTimes[format(MNUMCount, '03d')]=0;
                            MNUMPort[format(MNUMCount, '03d')]=UDP_PORT
                            MNUMIP[format(MNUMCount, '03d')]=UDP_IP
                            MNUMCount+=1;
                            
                            
                            our_socket.sendto(data.encode('utf-8'),(UDP_IP, int(UDP_PORT)))

                    
                if item == our_socket:
                    data, server = our_socket.recvfrom(4096)
                    print("Got message %s" % data.decode('utf-8'))
                    SRC=str(re.findall("\d+",data.decode('utf-8'))[0])
                    DST=str(re.findall("\d+",data.decode('utf-8'))[1])
                    PNUM=str(re.findall("\d+",data.decode('utf-8'))[2])
                    HCT=str(re.findall("\d+",data.decode('utf-8'))[3])
                    MNUM=str(re.findall("\d+",data.decode('utf-8'))[4])
                    MESG=data.decode('utf-8').split(";")[6]
                    VL=data.decode('utf-8').split(";")[6].split(":")[1].split(",")


                   

                    if PNUM=="4" or PNUM=="8":

                        if  MNUM in MNUMTimes: 
                            MNUMArr.pop(MNUM)
                            MNUMTimes.pop(MNUM)
                        continue
                    elif PNUM=="7":
                         
                        print("SRC:"+SRC+"broadcasted:"+MESG)
                        MESSAGE="SRC:"+DST+";DST:"+SRC+";PNUM:8;HCT:1;MNUM:"+MNUM+";VL:;MESG:ACK"
                        our_socket.sendto(MESSAGE.encode('utf-8'),(UDP_IP, UDP_PORT))
                    elif PNUM=="3" :
                        MESSAGE="SRC:"+DST+";DST:"+SRC+";PNUM:4;HCT:1;MNUM:"+MNUM+";VL:;MESG:ACK"
                        our_socket.sendto(MESSAGE.encode('utf-8'),(UDP_IP, UDP_PORT))
                        if DST!=myPeerName: 
                            MESSAGE="SRC:"+DST+";DST:"+SRC+";PNUM:4;HCT:1;MNUM:"+MNUM+";VL:;MESG:ACK"
                            our_socket.sendto(MESSAGE.encode('utf-8'),(UDP_IP, UDP_PORT))
                            if HCT=="0":
                                print("********************")
                                print("Dropped message from "+SRC+" to "+DST+" - hop count exceeded")
                                print("MESG: "+MESG)
                            elif myPeerName in VL:
                                print("********************")
                                print("Dropped message from "+SRC+" to "+DST+" - peer revisited")
                                print("MESG: "+MESG)
                            else:
                                VL.append(myPeerName)
                                VLstr=",".join(VL)
                                HCT=str(int(HCT)-1)
                                for x in range(0,3):
                                    UDP_IP=ips[x]
                                    UDP_PORT=int(ports[x])
                                    MESSAGE="SRC:"+DST+";DST:"+SRC+";PNUM:3;HCT:"+HCT+";MNUM:"+MNUM+";VL:"+VLstr+";MESG:"+MESG
                                    our_socket.sendto(MESSAGE.encode('utf-8'),(UDP_IP, UDP_PORT))

                               


            
            
            
            # Though the amount of data you are writing to the socket will
            # not overload the outgoing buffer...it is good practice to
            # only write to sockets when you know their outgoing buffer
            # is not full.
            
        
        # Catch ^C to cancel and end program.
        except KeyboardInterrupt:
            our_socket.close()
            return
        except Exception as e:
            print("Unhandled exception 0: %s" % e)
            return
        #handle_io()

def connect_to_server():
    global our_socket
    
    global UDP_IP
    global UDP_PORT
    global myPeerName
    global myIP
    global myPORT
    UDP_IP = 'steel.isi.edu'
    UDP_PORT = 63682
    MESSAGE = "SRC:000;DST:999;PNUM:1;HCT:1;MNUM:001;VL:;MESG:register"
    our_socket = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP

    our_socket.sendto(MESSAGE.encode('utf-8'),(UDP_IP, UDP_PORT))
   
    
    # Receive response
    
    data, server = our_socket.recvfrom(4096)
    print("Got message %s" % data.decode('utf-8'))
    
    
    
    MESG=data.decode('utf-8').split(";")[6] 
    myPeerName=re.findall("\d+",MESG)[0]
    myIP= re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', MESG).group()
    myPORT=MESG.split("@")[1]

    print("Successfully registered. My ID is: ",myPeerName)
    
    #print(addressIP)
    #print(addresses)
    #print(ports)
    return

if __name__ == "__main__":
    connect_to_server()
    run_loop()

     
