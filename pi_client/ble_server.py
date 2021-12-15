import socket

serverMACAddress = 'B8:27:EB:D6:59:32'
port = 1
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.connect((serverMACAddress, port))
while 1:
    text = input('input char to send ')
    if text == "quit":
        break
    s.send(bytes(text, 'UTF-8'))
s.close()
