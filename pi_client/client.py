from interface import PololuTIRSLKRobot 
import socket
from time import sleep
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.context import Process
from aruco_pd_client import run

def pd_control(speed, error, prev_err, k_p, k_d):
    return speed + k_p * error + k_d * (error - prev_error)


def execute_one(state: int, robot, speed) -> bytes:
    prev_err = 0	
    while robot.postion() == old_grid:
        desired = state * 90
        current = robot.degrees()
        old_grid = robot.position()
        error = desired - current
        
        control_input = pd_control(speed, error, prev_err, .01, .01)
        left_speed = control_input + speed
        right_speed = control_input - speed
        prev_err = error
        robot._left_motor(left_speed, False)
        robot._right_motor(right_speed, False)
    robot.stop()
    sleep(.5)
    return b'stopped'
	
	
	
	
def main():
    hostMACAddress = 'B8:27:EB:E6:68:D5'
    port = 2
    backlog = 1
    size = 1024
    s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    s.bind((hostMACAddress,port))
    print('socket bound')
    s.listen(backlog)
    log_dir_from_int = {i: dr for i, dr in zip(range(-1, 4),
    ['stay', 'up', 'right', 'down', 'left'])}
    with SharedMemoryManager() as smm:
        point_and_deg = smm.ShareableList([0, 0, 0])
        robot = PololuTIRSLKRobot(orient_pipe=point_and_deg)
        speed = .1

        orient_aruco_proc = Process(target=run, args=(point_and_deg,))
        robot.stop()
        sleep(.5)
        orient_aruco_proc.start()
        x = 0
        while not any(point_and_deg):
            sleep(1)
        

        try:
            client, address = s.accept()
            print(f'client {client}')
            print(address)
            while True:
                data = client.recv(size)
                if data:
                    data_int = int(data)
                    print(log_dir_from_int.get(data_int, f'invalid dir sent {data_int}'))
                    out = execute_one(data_int, robot, speed)
                    client.send(out)
        except Exception as e:
            print(f"Closing socket due to {e}")
            client.close()
            s.close()
        orient_aruco_proc.join()

if __name__ == "__main__":
	main()
	
	
