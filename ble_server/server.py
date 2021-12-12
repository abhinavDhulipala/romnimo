from multiprocessing.context import Process
from typing import List
from board_gui import run_gui
from multiprocessing.managers import SharedMemoryManager
import os

"""
simulate the ble incoming data types. expect to see a stop command for each robot
"""
def test_asynch(shared_mem: List):
    p = input('send packet to server: expects robot_id (1 or 2) ')
    while p != 'q':
        if p.isnumeric():
            num = int(p)
            num -= 1
            if num < 2:
                shared_mem[num] = 1
        p = input('send packet to server: expects robot_id (1 or 2) ')

def ble_listener(shared_mem: List):
    print(shared_mem)

def server(env=os.getenv('ENV')):
    with SharedMemoryManager() as smm:
        robot_states = smm.ShareableList([0] * 2)
        listener_func = test_asynch if env == 'test' else ble_listener
        gui = Process(target=run_gui, kwargs={'shared_robot_states': robot_states})
        gui.start()
        listener_func(robot_states)
        gui.join()
        print(robot_states)

if __name__ == '__main__':
    server('test')