from socket import *

import packet
import sys
import random

# setup
sender = socket(AF_INET, SOCK_DGRAM)
port = input("Port: ")
host = input("Host: ")
addr = (host,int(port))
num = input("number of file: ")
file_list = []
for i in range(int(num)):
  fname = input("file name ke-" + str(i+1) + ": ")
  file_list.append(fname)

print("\n")
print("PROGRESS")

while(len(file_list) != 0):

  f = open(file_list[0], "rb")
  DATA = f.read(packet.MAX_DATA_SIZE)
  num_of_packet = 0

  # Hitung jumlah packet yang dapat dibuat
  while(len(DATA) != 0):
    DATA = f.read(packet.MAX_DATA_SIZE)
    num_of_packet += 1

  f.close()

  # Mulai proses pembuatan paket
  fc = open(file_list[0], "rb")
  DATA = fc.read(packet.MAX_DATA_SIZE)
  i = 1
  ID = random.randrange(15)

  while(DATA):
    NEXT_DATA = fc.read(packet.MAX_DATA_SIZE)

    # Selama bukan paket terakhir
    if(len(NEXT_DATA) != 0):
      TYPE = "0000"
    else:
      TYPE = "0010"
    
    # Make HEADER = TYPE + ID
    str_header = TYPE + format(ID, "04b")
    HEADER = int(str_header,2).to_bytes(1,"big")

    # Make SEQUENCE_NUMBER
    SEQUENCE_NUMBER = i.to_bytes(2, "big")

    # Make LENGTH
    LENGTH = (len(DATA) // 1000).to_bytes(2, "big")

    # Make PACKET
    PACKET = packet.Packet(HEADER, SEQUENCE_NUMBER, LENGTH, DATA).encode()
    sender.sendto(PACKET, addr)

    # Wait response
    reply, addr = sender.recvfrom(packet.MAX_PACKET_SIZE)

    # Print progress bar
    rep_id = int.from_bytes(reply[0:1], byteorder="big") & 0x0f
    progress = int.from_bytes(reply[1:3], byteorder="big")
    persentase = "{0:.1f}".format(100 * (progress / num_of_packet))
    terisi = 65 * progress // num_of_packet
    kosong = 65 - terisi
    progress_bar = '=' * terisi + '-' * kosong + ' ' + persentase + "% " + "file ID " + str(rep_id)
    print(progress_bar + '\r', end='')

    # Iterate
    DATA = NEXT_DATA
    i += 1
    
    REPLY_TYPE = int.from_bytes(reply[0:1], byteorder="big") >> 4

    if(REPLY_TYPE == packet.FIN_ACK):
      print("file with ID", ID, "sent!")
  
  del file_list[0]
  fc.close()

sender.close()