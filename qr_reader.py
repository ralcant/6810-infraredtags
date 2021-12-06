import cv2
import numpy as np
from pyzbar.pyzbar import decode

def detect_qr(frame, type="pyzbar"):
    """Detect qr codes in a given frame and updates it"""
    if type == "wechat":
        # print("Using wechat")
        # detector = cv2.wechat_qrcode_WeChatQRCode("./wechat_model/detect.prototxt.txt", "./wechat_model/detect.caffemodel", "./wechat_model/sr.prototxt.txt", "./wechat_model/sr.caffemodel")
        detector = cv2.wechat_qrcode_WeChatQRCode()
        res, points = detector.detectAndDecode(frame)
        if len(res) > 0 or len(points) > 0:
            print(res, points)
        # print(res)
        return frame
        # for t in res:
            # if t != prevstr:
                # print(t)
    # print("Using pyzbar")
    barcodes = decode(frame)
    for barcode in barcodes:
        # extract the bounding box location of the barcode and draw the
        # bounding box surrounding the barcode on the image
        (x, y, w, h) = barcode.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        # the barcode data is a bytes object so if we want to draw it on
        # our output image we need to convert it to a string first
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type
        # draw the barcode data and barcode type on the image
        text = "{} ({})".format(barcodeData, barcodeType)
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 0, 255), 2)
        # print the barcode type and data to the terminal
        print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
    return frame

def main():
    """Access camera and detects QR codes there"""
    cap = cv2.VideoCapture(1)
    while True:
        ret, frame = cap.read()
        # print(frame.shape)
        if not ret:
            break
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame = detect_qr(frame)
        cv2.imshow("image", frame)
    # After the loop release the cap object
    cap.release()
    # Destroy all the windows
    cv2.destroyAllWindows()


if __name__ == '__main__':
    # print(list_ports())
    # main()
    # frame = cv2.imread("qr_frame.png")
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # print(frame.shape)
    # frame = cv2.createCLAHE(5.0, (5, 5)).apply(frame)
    # cv2.imwrite("a.jpg", frame)
    # # frame = detect_qr(frame)
    # frame = cv2.GaussianBlur(frame, (3, 3), 0)
    # cv2.imwrite("b.jpg", frame)

    # frame = cv2.adaptiveThreshold(frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 29, 1)
    # cv2.imwrite("c.jpg", frame)

    # # frame = detect_qr(frame, type="wechat")
    # cv2.imwrite("qr_code_test_detected.png", frame)
    # while True:
    #     if cv2.waitKey(25) & 0xFF == ord('q'):
    #         break
    for wechat, clahe in {(True, True), (True, False), (False, True), (False, False)}: 
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
    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("qr_code_test_detected_real.png", frame)

    # print(frame.shape)
    # min_x, max_x, min_y, max_y = 40, 520, 20, 500
    
    # cv2.rectangle(frame, (min_x, min_y), (max_x, max_y), (0, 255, 0), 1, cv2.LINE_AA)
    # cv2.imwrite("d.jpg", frame)
