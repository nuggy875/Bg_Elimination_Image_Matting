import cv2
import numpy as np
import os
import os.path as osp
import sys

if len(sys.argv) == 1:
    print('please input env variable..')
    exit()

image = sys.argv[1]
src = cv2.imread('../public/image/'+sys.argv[1]+'.jpg')
bgr = src[:,:,:3]
gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
alpha = src[:,:,:3]
result = np.dstack([bgr, alpha])


det_path = osp.realpath('../public/result')
cv2.imwrite(osp.join(det_path, sys.argv[1]+'_rst.png'), result)           # Save