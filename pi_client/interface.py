from gpiozero import PololuDRV8835Robot, DigitalOutputDevice

class PololuTIRSLKRobot(PololuDRV8835Robot):
	
	"""
	We are using the Polulu DRV8838 motor controllers through
	the TIRSLK Chassis. This means current doesn't determine direction
	rather a direction bit (Ports P5.4 for L and P5.5 for R) to determine
	direction
	:param int left_dir, right_dir:
		The two corresponding GPIO pins for use to carry the direction
		bit(s). Represents two states (forward & backwards)
	"""
	def __init__(self, left_dir=17, right_dir=27):
		self.left_dir = DigitalOutputDevice(left_dir)
		self.right_dir = DigitalOutputDevice(right_dir)
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
		self.left_motor.backward(speed)
		
	def forward(self, speed=1):
		self._left_motor(speed, True)
		self._right_motor(speed, True)
		
	def backward(self, speed=1):
		self._left_motor(speed, False)
		self._right_motor(speed, False)
		
	def left(self, speed=1):
		self._left_motor(speed, True)
		self._right_motor(speed, False)
		
	def right(self, speed=1):
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
		
		

if __name__ == '__main__':
	from time import sleep
	robot = PololuTIRSLKRobot()
	speed, rest = .2, 5
	print('forward')
	robot.forward(speed)
	sleep(rest)
	print('backward')
	robot.backward(speed)
	sleep(rest)
	print('switch')
	robot.switch_dir()
	sleep(rest)
	print('left')
	robot.left(speed)
	sleep(rest)
	print('right')
	robot.right(speed)
	sleep(rest)
	