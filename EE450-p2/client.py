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
network_input = deque()
network_output = deque()
timer1 = time.time()
current_state = "idle"
current_msg= ""
sendFlag=True 


# You can keep your code simple by keeping a state transition table as a
# python dictionary (dictionary of lists or dictionary of dictionaries for
# example).  Again, for this simple program, you can make this a global
# variable.
state_transition_table = {}
state_transition_table["idle"]={}
state_transition_table["idle"]["hello"]="s1"
state_transition_table["idle"]["hi"]="idle"

state_transition_table["s1"]={}
state_transition_table["s1"]["three"]="s2"
state_transition_table["s1"]["red"]="s1"
state_transition_table["s1"]["ok"]="F"
state_transition_table["s1"]["done"]="s1"
state_transition_table["s2"]={}
state_transition_table["s2"]["five"]="s3"
state_transition_table["s2"]["green"]="s3"
state_transition_table["s2"]["ok"]="F"
state_transition_table["s2"]["done"]="s2"
state_transition_table["s3"]={}
state_transition_table["s3"]["one"]="s4"
state_transition_table["s3"]["blue"]="s3"
state_transition_table["s3"]["ok"]="F"
state_transition_table["s3"]["done"]="s3"
state_transition_table["s4"]={}
state_transition_table["s4"]["pink"]="s4"
state_transition_table["s4"]["ok"]="F"
state_transition_table["s4"]["done"]="s4"
state_transition_table["s3"]["seven"]="s5"
state_transition_table["s3"]["red"]="s3"
state_transition_table["s5"]={}
state_transition_table["s5"]["six"]="s2"
state_transition_table["s5"]["orange"]="s5"
state_transition_table["s5"]["ok"]="F"
state_transition_table["s5"]["done"]="s5"
state_transition_table["F"]={}
state_transition_table["F"]["bye"]="idle"


def handle_io():
    # This is likley the only function you'll want to edit.
    validRes=0;
    global our_socket, local_input, network_input, network_output
    global current_state, timer1
    global state_transition_table
    global current_msg
    global sendFlag


    command_table={}
    command_table["h"]="hi"
    command_table["r"]="red"
    command_table["g"]="green"
    command_table["p"]="pink"
    command_table["b"]="blue"
    command_table["o"]="orange"
    command_table["d"]="done"
    current_time = time.time()

    # Did you get something from the server?
    #
    # 1) Are you expecting something from the server, but nothing came?  Has
    # it been 3 seconds?  If so, re-send your message by appending it to the
    # left side of the network_output queue and return.  If it hasn't been 3
    # seconds, there's nothing to do but wait a little longer (so return).
    # Remember to print error messages when you need to resend.
    #
    # 2) Are you expecting something from the server, and something came?
    # Does what you received make sense for the protocol?  If not, re-send
    # your message by appending it to the left side of the network_output
    # queue, and return.
    # Remember to print error messages when you don't get what you expect.
    try:
        # Pop will *remove* the message from the FIFO queue, and return it.
        msg_from_server = network_input.pop()
        # Great- we got a message from the server.
        print("Got message %s" % msg_from_server)
        # Do some things.
        if state_transition_table[current_state].has_key(msg_from_server) :
        	
            current_state=state_transition_table[current_state][msg_from_server]
           
            sendFlag=True
            print("ha")
            if current_state=="F" :
            	network_output.appendleft("bye")
            	current_msg="bye"
            
            return
        else:
            print("Wrong message from server, attempt to resent current messge: %s" % current_msg )
            sendFlag=False
            network_output.appendleft(current_msg)
            
            return
            
            
        
    except IndexError:
        # No message from server.
        # Do some things - like check if a timeout has expired.
        #print("no response")
        if not sendFlag:
        	#print("return")
        	return
        pass
    except Exception as e:
        print("Unhandled exception: %s" % e)
        raise

    # Do we have keyboard input?
    #
    # 1) Have we handled our last message ok?  (e.g.  Did we get a response
    # back from the server and did the response make sense?) If we haven't
    # handled our last message ok, we cannot move on to new keyboard input.
    #
    # Send a message by appending it to the left side of the network_output
    # queue a the message onto the network_output queue.  E.g.
    # network_output.appendleft(mesg)
    # (Or change the code if you wish to send some other way)
    #
    # 2) If we're ready to move on, great!  Pop the next keyboard message,
    # check if it follows protocol and if so, keep going.
    # Remember to print error messages if the keyboard input does not follow
    # protocol.
    try:
        input = local_input.pop()

        # Do some things
        if command_table.has_key(input) and  state_transition_table[current_state].has_key(command_table[input]):
            current_msg=command_table[input]
            if state_transition_table[current_state].has_key(current_msg):
            	sendFlag=False
            
            	network_output.appendleft(current_msg)
        else :
        	print("wrong keyboard input, please give command again")
        return
    except IndexError:
        # Probably do nothing, but wait.
        pass
    except Exception as e:
        print("Unhandled exception: %s" % e)
        raise
    return

def run_loop():
    global our_socket, local_input, network_input, network_output,sendFlag,UDP_IP,UDP_PORT, ids,idsKnown,ips,ports,myPeerName, myIP,myPORT
    watch_for_write = []
    watch_for_read = [sys.stdin, our_socket]
    MNUMCount=0;
    MNUMArr={};
    MNUMTimes={};
    idsKnown=[]
    ips=[]
    ports=[]
    while True:
        try:
            # Use select to wait for input from either stdin (0) or our
            # socket (i.e.  network input).  Select returns when one of the
            # watched items has input, or has outgoing buffer space or has
            # an error.
            
            input_ready, output_ready, except_ready = select.select(watch_for_read, watch_for_write, watch_for_read,3)
			
            MNUMTimesCopy=MNUMTimes;
            for k,v in MNUMTimesCopy.items():
                if v<5:
                    data=MNUMArr[k];
                    DST=re.findall("\d+",data)[1]
                    UDP_IP=ips[idsKnown.index(DST)]
                    UDP_PORT=int(ports[idsKnown.index(DST)])
                    print("resend message: ",data)
                    our_socket.sendto(data.encode('utf-8'),(UDP_IP, UDP_PORT))
                    MNUMTimesCopy[k]+=1;
                    print(v);
                else:
                    print("********************")
                    print("ERROR: Gave up sending to ",k)
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
                        else:
                            return
                        MESSAGE="SRC:"+myPeerName+";DST:"+DST+";PNUM:3;HCT:1;MNUM:"+format(MNUMCount, '03d')+";VL:;MESG:"+MESSAGE[8:]
                        MNUMArr[format(MNUMCount, '03d')]=MESSAGE;
                        MNUMTimes[format(MNUMCount, '03d')]=0;
                        MNUMCount+=1;
                       
                        print(MESSAGE)
                        
                        print(UDP_IP," ",UDP_PORT) 
                        our_socket.sendto(MESSAGE.encode('utf-8'),(UDP_IP, UDP_PORT))
                        
                    
                if item == our_socket:
                    data, server = our_socket.recvfrom(4096)
                    print("Got message %s" % data.decode('utf-8'))
                    SRC=str(re.findall("\d+",data.decode('utf-8'))[0])
                    DST=str(re.findall("\d+",data.decode('utf-8'))[1])
                    PNUM=str(re.findall("\d+",data.decode('utf-8'))[2])
                    
                    MNUM=str(re.findall("\d+",data.decode('utf-8'))[4]);
                    

                   

                    if PNUM=="4":
                        
                        if  MNUM in MNUMTimes:
                           
                            MNUMArr.pop(MNUM)
                           
                            MNUMTimes.pop(MNUM)
                            

                        continue

                    MESSAGE="SRC:"+DST+";DST:"+SRC+";PNUM:4;HCT:1;MNUM:"+MNUM+";VL:;MESG:ACK"
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

     
