import socket
import pickle
import sys
from collections import namedtuple
import random
import time
import datetime
import hashlib


host=""

N=int(raw_input("No of Packets:"))
data_pkt = namedtuple('data_pkt', 'seq_num checksum data_type data')
ack_pkt = namedtuple('ack_pkt', 'seq_num zero_field data_type')


def create(port):
    c=socket.socket(socket.AF_INET, socket.SOCK_STREAM);
    c.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        c.connect((host, port))
    except:
        print "No available server"
        c.close()
        exit(0)
    return c

c=create(12345)
ack_socket=create(23456)

def checksum_calc(message):
    return hashlib.md5(message).hexdigest()


def main():
    prob_loss=0.0
    lost_seq_num = []
    print_message = []
    packet_lost = False
    exp_seq_num = 0
    ack_seq=0
    while True:
        data1 = c.recv(1024)
        c.send("hi")
        if data1=="completed":
            print "-------------------"
            print "Received!!"
            exit()
        # print data1
        data= pickle.loads(data1)
        print data
        seq_num, checksum, message = data[0], data[1], data[2]
        rand_loss = random.random()

        if rand_loss <= prob_loss:
            print("Packet loss, sequence number = ", seq_num)
            packet_lost = True
            if len(lost_seq_num) == 0:
                lost_seq_num.append(seq_num)
            if len(lost_seq_num) > 0:
                if seq_num not in lost_seq_num and (seq_num>min(lost_seq_num)):
                    lost_seq_num.append(seq_num)
        else:
            print seq_num ,exp_seq_num
            if checksum != checksum_calc(message):
                print("Packet dropped, checksum doesn't match!")
            if seq_num == exp_seq_num:
                print "+++++++++++++++++++++++++++++++++++++"
                ack_seq = int(seq_num)+1
                if ack_seq<10:
                    ack_socket.send(str(ack_seq)+'a')
                if ack_seq>=10:
                    ack_socket.send(str(ack_seq))
                print ack_seq
                print_message.append(seq_num)
                with open('test_output', 'ab') as file:
                    file.write(message)
                exp_seq_num += 1
            else:
                ack_socket.send("ys")
                print "nothing"
            # if ack_seq==N:
            #     print "received successfully"
            #     exit()
if __name__ == "__main__":
    main()
