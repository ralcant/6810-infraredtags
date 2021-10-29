import qrcode
import cv2
import numpy as np

def convert_to_qr(link, output=None):
    img = qrcode.make(data= link, version = 1, box_size=1, border=0)
    img = np.array(img, dtype=np.uint8) * 255
    print(img.shape)
    print(img)
    # img = cv2.resize(img, (100, 100))
    if output is not None:
        cv2.imwrite(output, img)

    # while True:
    #     cv2.imshow("qr code", img)
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

if __name__ == '__main__':
    link = "www.google.com"
    output = "./test.png"
    convert_to_qr(link)