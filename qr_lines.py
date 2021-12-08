import cv2 
import numpy as np   
import imutils
from collections import defaultdict

def main():
    orig = cv2.imread("./final_0.jpg")
    w, h = 640, 360

    while True:
        ret, frame = True, orig.copy()
        if not ret:
            break
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        frame = cv2.resize(frame,dsize=(w, h))
        cv2.imshow('frame', frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = 255-frame
        thresh = cv2.adaptiveThreshold(frame, 255 ,cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 21, 10)
        cv2.imshow('threh', thresh)
        # print(thresh.shape)
        kernel = np.ones((4, 4), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations=1)
        cv2.imshow('erode', thresh)
        thresh_copy = cv2.cvtColor(thresh.copy(), cv2.COLOR_GRAY2BGR)
        # print(thresh.shape)
        contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # print(len(cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)))
        contours = imutils.grab_contours(contours)
        mask = cv2
        points = []
        for cnt in contours:
            if cv2.contourArea(cnt) < 5:
                continue
        	# compute the center of the contour
            M = cv2.moments(cnt)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            centerOfCircle = (cX, cY)
            points.append(centerOfCircle)
            cv2.circle(thresh_copy, centerOfCircle, radius=1, color=(0, 0, 255), thickness=2)
        cv2.imshow('points', thresh_copy)
        full_rect = cv2.minAreaRect(np.array(points))
        box = cv2.boxPoints(full_rect)
        # box = np.array(
        #     [[180.2321,10.106293 ],
        #     [485.4971,20.0],
        #     [490.45892,321.21793  ],
        #     [185.19394,326.01263  ]], dtype=np.float32)

        # print(box)
        thresh = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(thresh,[np.int0(box)],0,(0,0,255),2)
        cv2.imshow('rect', thresh)

        qr = np.float32([[0, 0], [23, 0], [23, 23], [0, 23]])
        matrix = cv2.getPerspectiveTransform(box, qr)

        # Horizontal lines
        for i in range(1, 23): #(0, i) -> (22, i)
            x_1, y_1, _ = np.int0(np.linalg.inv(matrix) @ np.array([0, i, 1]))
            x_2, y_2, _ = np.int0(np.linalg.inv(matrix) @ np.array([23, i, 1]))
            cv2.line(thresh, (x_1, y_1), (x_2, y_2), (0, 255, 0), 1, cv2.LINE_AA)
        # Vertical lines
        for i in range(1, 23): #(i, 0) -> (i, 22)
            x_1, y_1, _ = np.int0(np.linalg.inv(matrix) @ np.array([i, 0, 1]))
            x_2, y_2, _ = np.int0(np.linalg.inv(matrix) @ np.array([i, 23, 1]))
            cv2.line(thresh, (x_1, y_1), (x_2, y_2), (0, 255, 0), 1, cv2.LINE_AA)
        cv2.imshow('lines', thresh)

        res = np.zeros((23, 23))
        for x, y in points:
            i, j, _ = matrix @ np.array([x, y, 1])
            i, j = int(i), int(j)
            if i == 23 or j == 23 or i < 0 or j < 0:
                print(x, y)
                print(matrix @ np.array([x, y, 1]))
                continue
            res[j][i] = 1
        cv2.imwrite('huh.jpg', res)
        cv2.imshow('final qr', cv2.resize(res, (200, 200)))
if __name__ == "__main__":
    main()