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


def receive_from_car(commands, car_num):
    host_mac = 'E4:A4:71:17:4A:0C'
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.bind((host_mac, car_num))
    client, addr = s.accept()
    try:
        print(f'pi {car_num} := {addr}')
        while True:
            stop_state = client.recv(Config.BUFF_SIZE)
            if stop_state:
                stop_int = int(stop_state)
                print(stop_state)
                commands[car_num] = stop_int
    except Exception as e:
        print(f'socket closed due to {e}')
        client.close()
        s.close()



def server_inline(env='local'):
    server_funcs = {
        'local': test_asynch_local,
        'c2pi': receive_from_car
    }
    assert env in server_funcs, 'invalid server function'

    with SharedMemoryManager() as smm:
        robot_states = smm.ShareableList([0] * 2)
        robot_commands = smm.ShareableList([-1] * 2)
        gui = Process(target=run_gui, kwargs={
            'shared_robot_states': robot_states,
            'shared_robot_commands': robot_commands})
        """car1_command = Process(target=send_to_car, args=(car1_mac_addr,
                                                         robot_states,
                                                         robot_commands,
                                                         1))
                                                         """

        car1_command = Process(target=send_to_car, args=(car1_mac_addr,
                                                         robot_commands,
                                                         robot_states,
                                                         1))
        gui.start()
        car1_command.start()
        # car1_receive.start()
        sleep(.05)
        server_funcs[env](robot_states)
        car1_command.join()
        # car1_receive.join()
        gui.join()
        print('done')


if __name__ == '__main__':
    server_inline()
