# Lane Detection
import cv2
import numpy as np
import matplotlib.pyplot as plt

def make_coordinates(image,line_parameters):
    slope, intercept = line_parameters
    y1 = image.shape[0] # Image shape: (704,1279,3), y1= 704
    y2 = int(y1*(3/5)) # y2= 422.4
    x1 = int((y1-intercept)/slope)
    x2 = int((y2-intercept)/slope)
    return np.array([x1,y1,x2,y2])

def average_slope_intercept(image,lines):
    left_fit = []
    right_fit = []
    for line in lines:
        x1, y1, x2, y2 = line.reshape(4)
        parameters = np.polyfit((x1,x2),(y1,y2), 1) # To get the slope and y-intercept, polyfit- fits a 1st degree polynomial(y= mx+b)
        slope = parameters[0]
        intercept = parameters[1]
        if slope < 0:
            left_fit.append((slope,intercept))
        else:
            right_fit.append((slope,intercept))
    left_fit_average = np.average(left_fit, axis=0) # Calculate average slope and y-intercept vertically
    right_fit_average = np.average(right_fit, axis=0)
    left_line = make_coordinates(image,left_fit_average) # To get the coordinates to draw the line
    right_line = make_coordinates(image,right_fit_average)
    return np.array([left_line,right_line])

def canny(image):
    gray = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY) # Converting a color image to gray image to reduce computational complexity
    blur = cv2.GaussianBlur(gray,(5,5),0) # To reduce noise and smoothen the image
    canny = cv2.Canny(blur,50,150) # To detect the edges of the image using canny fn
    return canny

def display_lines(image, lines):
    line_image = np.zeros_like(image)
    if lines is not None: # to check if any line is detected, lines- 3-d array
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            # line- draws a line segment connecting 2 points, color of the line, line density
            cv2.line(line_image, (x1,y1), (x2,y2), (255,0,0), 10)
    return line_image

def region_of_interest(image): # Detect the lanes(enclosed region):
    height = image.shape[0] # To get the height of the image
    polygons = np.array([[(200,height),(1100,height),(550,250)]]) # Providing the 3 edge values of the triangle
    mask = np.zeros_like(image) # Create an array of zeros with the shape of the image (black image)
    # The mask will be an image which is completely black
    cv2.fillPoly(mask,polygons,255) # Fill the mask with our triangle(with color white)
    masked_image = cv2.bitwise_and(image,mask) # shows only the triangle in white color
    return masked_image # Modified mask

# To detect the lanes in Video
cap = cv2.VideoCapture("PATH") #insert relative path to video file here
while(cap.isOpened()):
    _, frame = cap.read() # To decode every video frame
    canny_image = canny(frame)
    cropped_image = region_of_interest(canny_image)
    lines = cv2.HoughLinesP(cropped_image,2, np.pi/180,100,np.array([]),minLineLength = 40,maxLineGap = 5)
    average_lines = average_slope_intercept(frame, lines)
    line_image = display_lines(frame, average_lines)
    combo_image = cv2.addWeighted(frame,0.8,line_image,1,1)
    cv2.imshow('result',combo_image)
    #cv2.waitKey(1) - wait 1ms in between frames
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
