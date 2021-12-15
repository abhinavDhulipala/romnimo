from interface import PololuTIRSLKRobot 
import socket
from time import sleep
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.context import Process
from aruco_pd_client import run


def execute_one(state: int, robot, speed) -> bytes:
	
	diff = abs(robot.orient - state)
	for _ in range(diff):
		if diff > 0:
			robot.left(speed)
			sleep(1)
			robot.stop()
		else:
			robot.right(speed)
			sleep(1)
			robot.stop()
		sleep(.2)
			
	
	robot.forward(speed)		
	
	"""
	replace with stop detection. Potentially from bump sensors
	"""
	sleep(2)
	robot.stop()
	"""
	account for momentum & send stop state back
	"""
	sleep(.5)
	return b'stopped'
	
	
def main():
	hostMACAddress = 'B8:27:EB:D6:59:32'
	port = 1
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
		speed = .4

		orient_aruco_proc = Process(target=run, kwargs={
			'port': 4000,
			'array': point_and_deg
		})

		orient_aruco_proc.start()

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
	
	
