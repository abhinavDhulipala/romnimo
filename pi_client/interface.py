from gpiozero import PololuDRV8835Robot, DigitalOutputDevice
from picamera.array import PiRGBArray
from picamera import PiCamera
from lineDetection import get_vertical_edge, get_horizontal_edge
from time import sleep

class PololuTIRSLKRobot(PololuDRV8835Robot):
	
	"""
	We are using the Polulu DRV8838 motor controllers through
	the TIRSLK Chassis. This means current doesn't determine direction
	rather a direction bit (Ports P5.4 for L and P5.5 for R) to determine
	direction
	:param int left_dir, right_dir:
		The two corresponding GPIO pins for use to carry the direction
		bit(s). Represents two states (forward & backwards)
		
	add variable for orientation tracking. on every actual turn adjust orientation var
	0 -> left
	1 -> facing "down" or south
	2 -> right 
	3 -> turn around
	"""
	def __init__(self, left_dir=17, right_dir=27):
		self.left_dir = DigitalOutputDevice(left_dir)
		self.right_dir = DigitalOutputDevice(right_dir)
		self.orient: int = 1
		super().__init__()
		
		

	def _left_motor(self, speed=1, forward=True):
		if forward:
			self.left_dir.on()
		else:
			self.left_dir.off()
		self.left_motor.backward(speed)
		
	def _right_motor(self, speed=1, forward=True):
		if forward:
			self.right_dir.on()
		else:
			self.right_dir.off()
		self.right_motor.backward(speed)
		
	def backward(self, speed=.1):
		self._left_motor(speed, True)
		self._right_motor(speed, True)
		
	def forward(self, speed=.1):
		self._left_motor(speed, False)
		self._right_motor(speed, False)
		
	def left(self, speed=1):
		self.orient = (self.orient - 1) % 4
		self._left_motor(speed, True)
		self._right_motor(speed, False)
		
	def right(self, speed=1):
		self.orient = (self.orient + 1) % 4
		self._left_motor(speed, False)
		self._right_motor(speed, True)
	
	"""
	Switch direction of both motors to the opposite direction
	"""
	def switch_dir(self):

		if self.left_dir.value:
			self.left_dir.off()
		else:
			self.left_dir.on()
			
		if self.right_dir.value:
			self.right_dir.off()
		else:
			self.right_dir.on()
	
	
	def reverse(self):
		self.switch_dir()
		
	def stop(self):
		self._left_motor(0)
		self._right_motor(0)
	
	def pd_control(self, speed, k_p, k_d):
		prev_err = getCVError()	# implement this function to get the error using cv
		while True:
			curr_err = getCVError()
			feedback = k_p * curr_err + k_d * (curr_err - prev_err)
			left_speed = speed + feedback
			right_speed = speed - feedback
			self._left_motor(left_speed, True)
			self._right_motor(right_speed, True)
			sleep(50)

		
def run_function(robot):
	camera = PiCamera()
	camera.resolution = (640, 480)
	camera.framerate = 15
	rawCapture = PiRGBArray(camera, size=(640, 480))

	image = None
	# robot = PololuTIRSLKRobot()
	robot.forward(0.03)
	speed, rest = .07, 0.5
	standard_vwidth = None
	standard_hwidth = None
	change_dir = False
	i = 0

	# options = {
	# 	0 : up,
  #   1 : right,
	# 	4 : down,
	# 	9 : left,
	# }

	# Initialization for the first frame
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		image = frame.array
		standard_vwidth = get_vertical_edge(image)
		standard_hwidth = get_horizontal_edge(image)
		rawCapture.truncate(0)
		break

	print('forward')
	robot._right_motor(speed - 0.02, False)
	robot._left_motor(speed, False)

	while change_dir == False:
		for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			image = frame.array
			rawCapture.truncate(0)
			break
		
		curr_width = get_vertical_edge(image)
		end_of_block = get_horizontal_edge(image)
		if (end_of_block < 150 and i > 2):
			robot.stop()
			print("STOP")
			# send to server
			return 'stop', robot.orient

		left_speed, right_speed = robot.pd_control(speed, 0.01, 0.01, 0, standard_vwidth, curr_width)
		left_speed = max(0.08, min(0.1, left_speed))
		right_speed = max(0.067, min(0.072, right_speed))
		robot._right_motor(right_speed, False)
		robot._left_motor(left_speed, False)
		i += 1
		sleep(rest)

if __name__ == '__main__':
	pass
	
