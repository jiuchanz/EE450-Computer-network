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
sendFlag=False 
inputPop=True

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
state_transition_table["s2"]["green"]="s2"
state_transition_table["s2"]["ok"]="F"
state_transition_table["s2"]["done"]="s2"
state_transition_table["s3"]={}
state_transition_table["s3"]["one"]="s4"
state_transition_table["s3"]["blue"]="s3"
state_transition_table["s3"]["ok"]="F"
state_transition_table["s3"]["done"]="s3"
state_transition_table["s4"]={}
state_transition_table["s4"]["pink"]="s4"
state_transition_table["s4"]["two"]="s5"
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

    global inputPop
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
        if state_transition_table[current_state].has_key(msg_from_server) and state_transition_table[current_state][msg_from_server]!=current_state :
        	
            current_state=state_transition_table[current_state][msg_from_server]
            inputPop=True
            sendFlag=False
           
            if current_state=="F" :
            	network_output.appendleft("bye")
            	current_msg="bye"
            if current_state=="idle" :
                sendFlag=False 
                inputPop=True
                
            return
        else:
            print("Wrong message from server, attempt to resent current messge: %s" % current_msg )
            timer1=time.time()
            inputPop=False
            sendFlag=True
            network_output.appendleft(current_msg)
            
            return
            
            
        
    except IndexError:
        # No message from server.
        # Do some things - like check if a timeout has expired.
        #print("no response")
        current_time=time.time()
        

        if sendFlag and (current_time-timer1)>3:
            network_output.appendleft(current_msg)
       	    print("no response from server over 3 seconds, resend the msg")
            sendFlag=True
            inputPop=False
            timer1=time.time()
            return
        
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
        if inputPop:
            input = local_input.pop()
            inputPop=False
        else :
            return

        # Do some things
        if command_table.has_key(input) and  state_transition_table[current_state].has_key(command_table[input])  :
            current_msg=command_table[input]
            if state_transition_table[current_state].has_key(current_msg):
            	sendFlag=True
                inputPop=False
                timer1=time.time()
            	network_output.appendleft(current_msg)

        else :
            print("wrong keyboard input, please give command again")
            inputPop=True
        return
    except IndexError:
        # Probably do nothing, but wait.
        pass
    except Exception as e:
        print("Unhandled exception: %s" % e)
        raise
    return

def run_loop():
    global our_socket, local_input, network_input, network_output
    watch_for_write = []
    watch_for_read = [sys.stdin, our_socket]
    while True:
        try:
            # Use select to wait for input from either stdin (0) or our
            # socket (i.e.  network input).  Select returns when one of the
            # watched items has input, or has outgoing buffer space or has
            # an error.
            if len(network_output) > 0:
                watch_for_write = [our_socket]
            else:
                watch_for_write = []
            input_ready, output_ready, except_ready = select.select(watch_for_read, watch_for_write, watch_for_read, 3)    
            
            for item in input_ready:
                if item == sys.stdin:
                    data = sys.stdin.readline().strip()
                    if len(data) > 0:
                        print("Received local input: %s" % data)
                        local_input.appendleft(str(data)) 
                    else:
                        pass
                if item == our_socket:
                    data = our_socket.recv(1024).decode('utf-8')
                    if len(data) > 0:
                        print("Received from network: %s" % data)
                        network_input.appendleft(str(data))
                    else:
                        our_socket.close()
                        return
            
            # Though the amount of data you are writing to the socket will
            # not overload the outgoing buffer...it is good practice to
            # only write to sockets when you know their outgoing buffer
            # is not full.
            for item in output_ready:
                if item == our_socket:
                    try:
                        msg_to_send = network_output.pop()
                        
                        # Normally you want to check the return value of
                        # send() to make sure you were able to send all the
                        # bytes.  Our messages are so short, we don't bother
                        # doing that here.
                        our_socket.send(msg_to_send.encode('utf-8'))
                    except IndexError:
                        pass
                    except Exception as e:
                        print("Unhandled send exception: %s" % e)
            
            for item in except_ready:
                if item == our_socket:
                    our_socket.close()
                    return
        
        # Catch ^C to cancel and end program.
        except KeyboardInterrupt:
            our_socket.close()
            return
        except Exception as e:
            print("Unhandled exception 0: %s" % e)
            return
        handle_io()

def connect_to_server():
    global our_socket
    # "Good" server at port 65520
    # "Bad" server at port 65521
    server_address = ('steel.isi.edu', 65520)
    our_socket.connect(server_address)
    return

if __name__ == "__main__":
    connect_to_server()
    run_loop()

     
