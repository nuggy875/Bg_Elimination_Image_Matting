import cv2
import os
import numpy as np

if __name__ == '__main__':
    cv2.imread(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../public/input/input.jpg")))
    img_test = np.zeros((500, 500, 3), np.uint8)
    cv2.imwrite(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../public/input/input_a.jpg")), img_test)
    print('connected1')
