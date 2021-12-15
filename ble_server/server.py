from multiprocessing.context import Process
from typing import List
from board_gui import run_gui
from multiprocessing.managers import SharedMemoryManager
from time import sleep
import socket

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
def send_to_car(addr, commands, car_num):
    assert car_num in {1, 2}, 'not a valid car id'
    port = car_num
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.connect((addr, port))
    # 0th index corresponds to the first cars command
    index = car_num - 1
    while commands[index] != 'quit':
        c = commands[index]
        if c:
            s.send(bytes(c, 'UTF-8'))
            commands[index] = ''
        sleep(.05)


def comp_to_pi_listener(shared_mem: List):
    print(shared_mem)



def server_inline(env='local'):
    server_funcs = {
        'local': test_asynch_local,
        'c2pi': comp_to_pi_listener
    }
    assert env in server_funcs, 'invalid server function'

    with SharedMemoryManager() as smm:
        robot_states = smm.ShareableList([0] * 2)
        robot_commands = smm.ShareableList([''] * 2)
        gui = Process(target=run_gui, kwargs={
            'shared_robot_states': robot_states,
            'shared_robot_commands': robot_commands})
        car1_command = Process(target=send_to_car, args=(car1_mac_addr,
                                                         robot_commands,
                                                         1))
        gui.start()
        car1_command.start()
        sleep(.05)
        server_funcs[env](robot_states)
        car1_command.join()
        gui.join()
        print('done')


if __name__ == '__main__':
    server_inline()
