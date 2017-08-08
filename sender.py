import socket
import pickle
from collections import namedtuple
import threading
import inspect
import time
import signal
import sys
import hashlib
import os
import datetime

W=int(raw_input("Window size:"))
Time=float(raw_input("Time_Out:"))
N=int(raw_input("No of packets:"))
T=float((0.0012)*(W/5))
starttime=0
num_pkts_sent = 0
num_pkts_acked = 0
seq_num = 0
window_low = 0
window_high = int(W)-1
total_pkts = 0
RTT = float(T)
pkts = []
done_transmitting = 0
starttime = 0
stoptime= 0
update_time=0
ACK=0

lock = threading.RLock() # for lock sth

port = 12345
host=""
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((host, port))
s.listen(5)
print 'Server is Listening to',host,":",port;

port1=23456
ack_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
ack_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
ack_socket.bind((host, port1))
ack_socket.listen(5)
print 'Ack_Server is Listening to',host,":",port1;

# ack_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# ack_port=23456
# host=socket.gethostname()
# ack_socket.bind((host, ack_port))
conn, addr = s.accept()
conn1, addr = ack_socket.accept()
# N =conn.recv(1024)
# print N

data_pkt = namedtuple('data_pkt', 'seq_num checksum  data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field ')

# def socket_function(pkts):
#     # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     # host = socket.gethostname()
#     # port = 12345
#     s.send(pkts)
#     s.close()

def checksum_calc(message):
    return hashlib.md5(message).hexdigest()

def pack(message, seq_num):
    pkt = data_pkt(seq_num, checksum_calc(message), message)
    my_list = [pkt.seq_num, pkt.checksum, pkt.data]
    packed_pkt = pickle.dumps(my_list)
    return packed_pkt



def send_file(file_content):
    global total_pkts
    global pkts
    global seq_num
    global num_pkts_sent
    global RTT
    global update_time
    pkts_to_send = []
    # total_pkts = N
    total_pkts = len(file_content)
    seq=0
    for item in file_content:
        pkts_to_send.append(pack(item, seq))
        seq += 1
    pkts=pkts_to_send
    current_max_window = min(int(W), int(total_pkts))
    # signal.setitimer(signal.ITIMER_REAL, RTT)
    update_time=time.time()
    while num_pkts_sent < current_max_window :
        if ACK == 0:
            conn.send(pkts[num_pkts_sent])
            if conn.recv(1024)=="hi":
                print "ll"
            print pkts[num_pkts_sent]
            num_pkts_sent += 1
        else:
            break


def ack_listen_thread():
    global window_high
    global window_low
    global num_pkts_sent
    global num_pkts_acked
    global total_pkts
    global ACK
    global done_transmitting
    global stoptime
    global update_time
    done_transmitting = 0
    while True:
        print "----------------"
        data =(conn1.recv(2))
        print data
        if len(data)>0:
            if data[len(data)-1]=='a':
                ACK = int(data[0])
            elif data!="ys":
                ACK= int(data)
        print data, ACK
        if ACK:
            # lock.acquire()
            if ACK >= window_low and ACK <total_pkts:
                # signal.alarm(0)
                # signal.setitimer(signal.ITIMER_REAL, RTT)
                print min(time.time()-update_time,T)
                if (time.time()-update_time) > T:
                    print "yes"
                    timer()
                temp_pckts_acked = ACK - window_low
                old_window_high = window_high
                window_high = min(window_high + ACK - window_low, total_pkts-1)
                window_low = ACK
                num_pkts_acked += temp_pckts_acked
                print int(window_high-old_window_high)
                for i in range(int(window_high-old_window_high)):
                    print "i am here"
                    conn.send(pkts[num_pkts_sent])
                    if conn.recv(1024)=="hi":
                        print "ll"
                    print "here"
                    # update_time=time.time()
                    print pkts[num_pkts_sent]
                    if num_pkts_sent < total_pkts-1:
                            num_pkts_sent += 1
            elif ACK == total_pkts:
                print("Transfer Complete!")
                conn.send("completed")
                done_transmitting = 1
                stoptime = time.time()
                print("Running Time:",str(stoptime-starttime))
                exit()
            # lock.release()


def timer():
    print "$$$$$$$$$$$$$$$"
    global pkts
    global window_low
    global window_high
    global total_pkts
    global ACK

    # window_high = int(W)-1
    # signal.signal(signal.SIGALRM, timer)
    resent_index = window_low
    if ACK == window_low:
        print ("Timeout sequence number ="+ str(ACK))
        # lock.acquire()
        print resent_index, window_high, total_pkts
        while resent_index <= window_high and resent_index < total_pkts:
            # signal.alarm(0)
            # signal.setitimer(signal.ITIMER_REAL, RTT)
            print pkts[resent_index]
            update_time=time.time()
            conn.send(pkts[resent_index])
            if conn.recv(1024)=="hi":
                print "ll"
            resent_index += 1
        # lock.release()


def main():
        global starttime
        starttime = time.time()
        # signal.signal(signal.SIGALRM, timer)
        try:
            file_content = []
            statinfo=os.stat('./test_file')
            filesize=statinfo.st_size
            packets=float(filesize/float(N))
            with open('./test_file', 'rb') as f:
                while True:
                    chunk = f.read(int(2))  # Read the file MSS bytes each time Foo
                    if chunk:
                        file_content.append(chunk)
                    else:
                        break
        except:
            sys.exit("Failed to open file!")
        print file_content
        send_file(file_content)
        threading.Thread(target=ack_listen_thread, args=()).start()
        # s.close()
if __name__ == "__main__":
    main()
