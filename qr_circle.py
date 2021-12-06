import cv2
import numpy as np
from numpy.core.numeric import full
from qr_reader import detect_qr
from qr_example import get_real
from math import sin, cos, pi

def main():
    # cap = cv2.VideoCapture('./out.mp4')
    cap = cv2.VideoCapture('./out_2.mp4')
    # cap = cv2.VideoCapture(1)
    # orig = cv2.imread("./qr_frame.png"))
    w, h = 640, 360
    # w, h = 480, 270
    # w, h = 520, 558
    n_frames = 0
    # total_frames = 10
    # curr_sum = np.array((w, h))
    # min_x, max_x, min_y, max_y = float('inf'), -1, float('inf'), -1
    # mask = np.zeros((23, 23)) 
    resize_w, resize_h = 200, 200
    avg_array = np.zeros((resize_w, resize_h))

    while True:

        ret, frame = cap.read()
        # ret, frame = True, orig
        if not ret: 
            break
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        frame = cv2.resize(frame,dsize=(w, h))
        cv2.imshow('frame', frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        cv2.imshow('hsv', frame)

        # k = 3
        # itr = 200
        # blur = cv2.GaussianBlur(frame, (k,k), 0)
        # cv2.imshow('blur', blur)
        # thresh = cv2.adaptiveThreshold(blur,300,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)
        # cv2.imshow('thresh', thresh)
        # # Dilate to combine adjacent text contours
        # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (k,k))
        # frame = cv2.dilate(thresh, kernel, iterations=itr)
        # cv2.imshow('frame', frame)
        low_H, low_S, low_V = 0, 0, 250
        high_H, high_S, high_V = 255, 255, 255
        thresh = cv2.inRange(frame, (low_H, low_S, low_V), (high_H, high_S, high_V))
        # thresh = cv2.threshold(frame, 255, 90, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # thresh = cv2.threshold(frame, 120, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # thresh = cv2.adaptiveThreshold(frame,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
        #     cv2.THRESH_BINARY,11,2)

        # blur = cv2.GaussianBlur(frame, (k,k), 0)
        # thresh = cv2.adaptiveThreshold(frame,90,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,41,30)

        cv2.imshow('thresh', thresh)
        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.erode(thresh, kernel, iterations=1)
        cv2.imshow('eroded', thresh)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        points = []
        for cnt in contours:
            for x, y in cnt[0]:
                centerOfCircle = (x, y)
                points.append(centerOfCircle)
                frame = cv2.circle(frame, centerOfCircle, radius=1, color=(0, 0, 255), thickness=2)
        print(len(points))

        cv2.imshow('frame with contours', frame)
        full_rect = cv2.minAreaRect(np.array(points))
        box = cv2.boxPoints(full_rect)
        # This is to avoid taking into account small, broken rectangles
        # if not( full_rect[1][0] > 125 and full_rect[1][1] > 125):
        #     continue
        print(full_rect[1][0], full_rect[1][1])    
        n_frames += 1

        print(box)
        initial = np.float32([[0, 0], [23, 0], [23, 23], [0, 23]])
        matrix = cv2.getPerspectiveTransform(box, initial)

        cv2.drawContours(frame,[np.int0(box)],0,(0,0,255),2)
        array = np.zeros((23, 23))

        for x, y in points:
            i, j, _ = matrix @ np.array([x, y, 1])
            i, j = int(i), int(j)
            i, j = min(i, 22), min(j, 22) #i, j are sometimes 23
            # array[i][j] = 1
            array[22-i][22-j] = 1 #to change the orientation
            cv2.circle(frame, (x, y), radius=1, color=(0, 0, 255), thickness=2)


        cv2.imshow('frames', frame)
        array = np.array(255 * ( array ), dtype=np.uint8)
        array = cv2.resize(array, (resize_w, resize_h))
        avg_array = (avg_array * (n_frames - 1) + array) / n_frames
        show = np.array(avg_array, dtype=np.uint8)
        cv2.imshow('array', show)
        real = get_real()
        real = cv2.resize(real, (resize_w, resize_h))
        cv2.imshow('Ground truth', real)
        cv2.imshow('Not-averaged QR', cv2.resize(array, (resize_w, resize_h)))

    # cv2.imwrite('qr_code_test_not_avg.png', array)
    # corners = {(0, 0), (0, 14), (14, 0)}
    # for i, j in corners:
    #     for k in range(9):
    #         show[i][j+k] = 255
    #         show[i+8][j+k] = 255
    #         show[i+k][j] = 255
    #         show[i+k][j+8] = 255

    # To take care of gray-ish     
    show[show < 30] = 0
    show[show > 0 ] = 255
    # show[show > 20] = 255
    # show[show < 255] = 0

    # To see if manually fixing mistakes would fix QR code detection
    mistakes = {
        # (0, 0, 255), 
        # (0, 4, 255), 
        # (0, 15, 255), 
        # (1, 0, 255), 
        # (1, 8, 255), 
        # (3, 22, 255), 
        # (8, 15, 255), 
        # (20, 8, 255), 
        ## Above are erros on the side of square
        # (1, 11, 255),
        # (3, 10, 255), 
        # (9, 4, 0), 
        (10, 3, 0), 
        (10, 6, 0), 
        (10, 15, 255),
        (12, 1, 255), 
        (12, 2, 0), 


        (12, 5, 0), 
        (12, 7, 255), 
        (14, 9, 0), 
        (15, 7, 0), 
        (17, 1, 0), 
        (17, 5, 0), 
        (17, 13, 0), 
        (18, 1, 0), 
        (18, 7, 0), 
        (21, 15, 255), 
        (22, 15, 255)
    }
    # for i, j, expected in mistakes:
    #     show[i][j] = expected



    cv2.imwrite('qr_code_test.png', show)
if __name__ == '__main__':
    main()

    frame = cv2.imread("qr_code_test.png")
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    real = cv2.imread("qr_real.png")
    real = cv2.cvtColor(real, cv2.COLOR_BGR2GRAY)
    c = 0
    for i in range(23):
        for j in range(23):
            if frame[i][j] != real[i][j]:
                print(f"Position at {i}, {j} is {frame[i][j]} but should be {real[i][j]}")
                c+=1
    print(f"Found {c} inconsitencies")
    print("Trying to do the text detection")
    for wechat, clahe in {(True, True), (True, False), (False, True), (False, False)}: 
        type = "wechat" if wechat else "pyzbar"
        print(f"Using {type} and clahe = {clahe}")
        frame = cv2.imread("qr_code_test.png")
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame, (300, 300))
        if clahe:
            # cv2.imshow('gray', cv2.resize(frame, (200, 200)))
            frame = cv2.createCLAHE(5.0, (5, 5)).apply(frame)
            # cv2.imshow('clahe', cv2.resize(frame, (200, 200)))
            frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 29, 1)
            # cv2.imshow('adapting threshold', cv2.resize(frame, (200, 200)))
        if wechat:
            frame = detect_qr(frame, "wechat")
        else:
            frame = detect_qr(frame)
            # cv2.imshow('result', frame)