from multiprocessing.context import Process
from typing import List
from board_gui import run_gui
from multiprocessing.managers import SharedMemoryManager
from time import sleep
from config import Config
import socket
import select

car1_mac_addr = 'B8:27:EB:D6:59:32'
car2_mac_addr = 'B8:27:EB:E6:68:D5'

"""
simulate the ble incoming data types. expect to see a stop command for each robot
"""
def test_asynch_local(shared_mem: List):
    p = input('send packet to server: expects robot_id (1 or 2) ')
    while p != 'q':
        if p.isnumeric():
            num = int(p)
            num -= 1
            if num < 2:
                shared_mem[num] = 1
        p = input('send packet to server: expects robot_id (1 or 2) ')

"""
@param: addr:str car mac address to send commands to
@param: commands:List shared list representing a command that a car must receive
@param: car_num:int car [1 | 2] to identify one of the 2 cars
"""
def send_to_car(addr, commands, robot_state, car_num):

    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((addr, car_num))

    index = car_num - 1


    while commands[index] != 'quit':
        to_send = commands[index]
        # -1 is the do-nothing state.
        if to_send + 1:
            print(f'sending... {to_send} {commands}')
            s.send(bytes(str(to_send), 'UTF-8'))
            commands[index] = -1

            # I/O blocking op
            msg = s.recv(Config.BUFF_SIZE)

            print(f'msg received {msg}')
            robot_state[index] = int(msg == b'stopped')

    print('connection closed')

def pid_aruco_delivery(array):
    def netcat(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, int(port)))
        print(f'array for pid {array}')

        try:
            while True:
                if any(array) and not any([i < 0 for i in array]):
                    s.sendall(bytearray(' '.join(map(str, array)), 'UTF-8'))
                sleep(.25)
        except Exception as e:
            print(f'closed due to exception {e}')
            s.shutdown(socket.SHUT_WR)
            s.close()
    netcat('192.168.42.4', 40000)


def server_inline(env='local'):
    server_funcs = {
        'local': test_asynch_local,
        'netcat_pos': pid_aruco_delivery
    }
    assert env in server_funcs, 'invalid server function'

    with SharedMemoryManager() as smm:
        robot_states = smm.ShareableList([0] * 2)
        robot_commands = smm.ShareableList([-1] * 2)
        car1_deg_and_pos = smm.ShareableList([0, 0, 0])
        gui = Process(target=run_gui, kwargs={
            'shared_robot_states': robot_states,
            'shared_robot_commands': robot_commands,
            'shared_robot_loc': car1_deg_and_pos})
        car2_command = Process(target=send_to_car, args=(car2_mac_addr, robot_commands, robot_states, 2))

        car1_command = Process(target=send_to_car, args=(car1_mac_addr, robot_commands, robot_states, 1))
        gui.start()
        #car2_command.start()
        #car1_command.start()
        sleep(.05)
        server_funcs[env](car1_deg_and_pos)
        #car2_command.join()
        #car1_command.join()
        gui.join()
        print('done')


if __name__ == '__main__':
    server_inline('netcat_pos')
