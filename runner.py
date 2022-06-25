import cv2
import numpy as np
import math

from motor import Motor, motor_delay

#라즈베리파이 카메라 사용 선언
cap = cv2.VideoCapture(-1)

#영상의 x,y크기 정의
size_x = 640
size_y = 480

#영상 크기 설정
cap.set(cv2.CAP_PROP_FRAME_WIDTH, size_x)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, size_y)

left_motor = Motor(30, 22, 21)
right_motor = Motor(25, 24, 23)

cur_state = 0
def motor_control(cur_state, state, speed):
	if cur_state == state:
		return

	else:
		if state == 0: # stop
			# left_motor.motor_stop()
			# right_motor.motor_stop()
			left_motor.go(speed)
			right_motor.go(speed)
			cur_state = state

		elif state == 1: # left
			left_motor.motor_stop()
			right_motor.go(speed)
			cur_state = state

		elif state == 2: # right
			right_motor.motor_stop()
			left_motor.go(speed)
			cur_state = state
		
		elif state == 4: # rotate
			right_motor.go(speed)
			left_motor.back(speed)
			cur_state = state

while True :
	ret, frame = cap.read() #1프레임을 읽음
	
	hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) #처리하기 위해 HSV컬러로 변경함
	'''빨간색 읽기위한 코드'''
	#색상 1 계산
	low_red = np.array([0, 80, 70]) #리스트보다 array가 처리속도가 빠름, numpy로 array 만들어줌
	high_red = np.array([30, 255, 255])
	mask1 = cv2.inRange(hsv_frame, low_red, high_red) #범위 이내의 값은 그대로 출력, 이외는 0
	#색상 2 계산
	lower_red = np.array([150, 80, 70])
	upper_red = np.array([180, 255, 255])
	mask2 = cv2.inRange(hsv_frame, lower_red, upper_red)
	
	#색상 1 계산한 값과 색상 2 계산한 결과를 합쳐줌
	mask_red = mask1 + mask2
	
	'''분리된 이미지 변환'''
	red = cv2.bitwise_and(frame, frame, mask=mask_red) # 이전 스텝에서 저장한 결과를 원본 영상에서 분리하여 red로 저장(범위 1과 2를 더하면서 분리한 영상이 손상됨)
	
	frame_gray = cv2.cvtColor(red, cv2.COLOR_BGR2GRAY) # 처리하기 편하게 하기 위해 GRAY영상(흑백)으로 변환하여 frame_gray로 저장
	_, img_binary = cv2.threshold(frame_gray, 80, 255, 0) #흑백의 정도가 80~255까지인 부분만 분리하여 img_binary로 저장
	contours, hierarchy = cv2.findContours(img_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #흑백 이미지를 기반으로 임계범위(등고선)를 추출, 화면에 인식된 모든 지점을 저장함(여러개)
	'''인식된 여러 등고선 중 가장 큰 등고선을 선택하여 maxArea[1]로 저장함'''
	maxArea = [0,0]
	for cnt in contours:#여러 등고선이 저장된 contours중 순차적으로 돌아가며 해당 데이터를 cnt에 저장
		size = cv2.contourArea(cnt) #인식된 데이터의 면적을 size에 저장
		if size > maxArea[0] : #이떄의 면적이 이전 면적보다 클 경우 해당 데이터를 가장 큰 데이터로 저장함
			maxArea[0] = size #처리를 위해 등고선의 면적을 저장해둠
			maxArea[1] = cnt #이때의 등고선 데이터를 저장함 -> 결국 마지막 데이터는 가장 클 때의 데이터가 됨
		
	if maxArea[0] != 0 : #인식된 등고선 데이터가 있을 때,
		'''이미지 정밀도를 조절하여 등고선을 깔끔하게(근사화) 만들어주고 등고선을 적색으로 그려줌'''
		epsilon = 0.05 * cv2.arcLength(maxArea[1], True) # 근사화를 위한 임계값 설정(0.05가 커질수록 둔해짐)
		approx = cv2.approxPolyDP(maxArea[1], epsilon, True) #등고선을 근사화하여 도형에 가깝게 만들고 점(꼭짓점)을 좌표를 추출함
		cv2.drawContours(frame, [approx], 0, (0, 0, 255), 5) #위에서 근사화한 등고선 점 데이터를 적색 선을 그려줌
		'''인식된 부표의 각도, 너비를 구함'''
		cornerList = [0, 0, 0, 0] #점의 좌표를 저장할 List
		lengthList = [0, 0, 9999999, 9999999]
		if len(approx) == 4 : #점의 개수가 4개이면 사각형으로 인식 -> 처리 시작 
			'''꼭짓점의 좌표 위치를 비교하여 점의 위치를 찾아 배열함'''
			# cornerList[3] cornerList[2]
			# cornerList[1] cornerList[0]
			for point in approx :
				lenFromZero = point[0][0]**2 + point[0][1]**2
				if lenFromZero > lengthList[0] : # 우측 하단 점일 경우
					lengthList[0] = lenFromZero
					cornerList[0] = point[0] 
				if lengthList[3] > lenFromZero : # 좌측 상단 점일 경우
					lengthList[3] = lenFromZero 
					cornerList[3] = point[0]
				
					lenFromMax = (size_x - point[0][0])**2 + point[0][0]**2
					if lenFromMax > lengthList[1] : #우측 하단 점일 경우
						lengthList[1] = lenFromMax
						cornerList[1] = point[0]
					if lengthList[2] > lenFromMax : #우측 상단 점일 경우
						lengthList[2] = lenFromMax
						cornerList[2] = point[0]

			if cornerList[0].any() and cornerList[1].any() and cornerList[2].any() and cornerList[3].any() : # 읽은 데이터에 누락된 데이터가 존재하지 않는다면,
				'''처리한 데이터를 바탕으로 점과 선을 그어줌'''
				cv2.circle(frame, tuple(cornerList[0]), 5, (255, 255, 0), 3) # 우측 하단 점 표시
				cv2.circle(frame, tuple(cornerList[3]), 5, (0, 255, 255), 3) # 좌측 상단 점 표시
				
				cv2.circle(frame, tuple(cornerList[1]), 5, (255, 0, 0), 3) # 좌측 하단 점 표시
				cv2.circle(frame, tuple(cornerList[2]), 5, (0, 255, 0) ,3) # 우측 상단 점 표시
				
				cv2.line(frame, tuple(cornerList[0]), tuple(cornerList[2]), (255, 128, 128), 3) # 오른쪽 선 표시
				cv2.line(frame, tuple(cornerList[3]), tuple(cornerList[1]), (255, 128, 128), 3) # 왼쪽 선 표시

				'''점의 집합의 중심 모멘트를 통해 중심점의 좌표를 계산함'''
				M = cv2.moments(approx) # 원의 모멘트를 계산함(이 중 중심 모멘트를 계산)
				cX = int(M['m10'] / M['m00']) # 중심 데이터를 분리(x축)
				cY = int(M['m01'] / M['m00']) # 중심 데이터를 분리(y축)
				cv2.circle(frame, (cX, cY), 3, (255, 0, 0), -1) # 중심점 표시
				
				cv2.imshow('frame', frame)

				#print("중심점 x좌표", cX) # 중심점 좌표 출력
				if (cX + 10) > size_x/2 or (cX - 10) < size_x/2:
					print("물체가 중심에 위치함")
					motor_control(cur_state, 0, 130)
				elif cX > size_x/2:
					print("물체가 오른쪽에 위치함")
					motor_control(cur_state, 2, 130)
				elif cX < size_x/2:
					print("물체가 왼쪽에 위치함")
					motor_control(cur_state, 1, 130)
				
				# '''삼각함수를 이용하여 상단 점에서 하단 점까지 그은 선의 길이를 측정함'''
				# lineRight_Length = math.hypot(cornerList[0][0] - cornerList[2][0], cornerList[0][1] - cornerList[2][1]) #오른쪽
				# lineLeft_Length = math.hypot(cornerList[1][0] - cornerList[3][0], cornerList[1][1] - cornerList[3][1]) #왼쪽

				# '''사각형의 각도를 계산함, -90도가 수평, 커지면 반시계방향, 작아지면 시계방향으로 회전하였을 경우'''
				# angleBottom = math.atan2(cornerList[3][0] - cornerList[2][0], cornerList[3][1] - cornerList[2][1])
				# angleBottom = math.degrees(angleBottom)

				# #print("각도", angleBottom) # 각도 출력
				# if angleBottom == -90 :
				# 	print("수평")
				# elif angleBottom > -90 :
				# 	print("반시계방향으로 회전됨")
				# elif angleBottom < -90 : 
				# 	print("시계방향으로 회전됨")
	else:
		cv2.imshow('frame', frame)
		motor_control(cur_state, 4, 65)

	cv2.waitKey(1)