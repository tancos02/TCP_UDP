import socket
import packet

receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = input("Port: ")
host = input("Host: ")
addr = (host, int(port))
receiver.bind(addr)

DATA_FILE = {}

while True:
  data,addr = receiver.recvfrom(packet.MAX_PACKET_SIZE)
  # get packet data
  HEADER = data[0:1]
  TYPE = int.from_bytes(HEADER, byteorder="big") >> 4
  ID = int.from_bytes(HEADER, byteorder="big") & 0x0f
  SEQUENCE_NUMBER = data[1:3]
  LENGTH = data[3:5]
  CHECKSUM = data[5:7]
  DATA = data[7:]
  print("packet ",str(ID)," sequence ",int.from_bytes(SEQUENCE_NUMBER, byteorder="big")," accepted")

  # validate checksum
  check = packet.Packet(HEADER, SEQUENCE_NUMBER, LENGTH, DATA).getCHECKSUM()
  if(check == CHECKSUM):
    
    # penggabungan data dari paket yang memiliki ID yang sama
    if ID in DATA_FILE:
      DATA_FILE[ID] += DATA
    else:
      DATA_FILE[ID] = DATA

    # Cek apakah sudah paket terakhir atau belum
    if(TYPE == packet.FIN):
      print("Making File......")
      TYPE_REPLY = "0011"
      fileName = "received_file_" + str(ID)
      f = open(fileName, "wb")
      f.write(DATA_FILE[ID])
      f.close()
      print("file ",fileName," received\n")
      del DATA_FILE[ID]
    else:
      TYPE_REPLY = "0010"

    # Make header
    str_header = TYPE_REPLY + format(format(ID, "04b"))
    HEADER_REPLY = int(str_header,2).to_bytes(1,"big")

    # Make packet
    PACKET_REPLY = packet.Packet(HEADER_REPLY, SEQUENCE_NUMBER, LENGTH, DATA).encode()
    receiver.sendto(PACKET_REPLY, addr)
    
  else:
    # jika hasil checksum tidak sama
    print("Packet is loss")
  
