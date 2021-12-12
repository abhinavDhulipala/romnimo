from multiprocessing.context import Process
from typing import List
from board_gui import run_gui
from multiprocessing.managers import SharedMemoryManager
import os
import bluetooth

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
ble where this computer acts as server and anopther simulates our peripehral code
"""
def comp_to_comp_listener(shared_mem: List):
    print(shared_mem)

def comp_to_pi_listener(shared_mem: List):
    print(shared_mem)

# test server to demo/test asynch events with commandline promps
def test_server_inline(env='local'):
    funcs = {
        'local': test_asynch_local,
        'c2c': comp_to_comp_listener,
        'c2pi': comp_to_pi_listener
    }
    with SharedMemoryManager() as smm:
        robot_states = smm.ShareableList([0] * 2)
        gui = Process(target=run_gui, kwargs={'shared_robot_states': robot_states})

        gui.start()
        gui.join()
        print(robot_states)

if __name__ == '__main__':
    test_server_inline('test')