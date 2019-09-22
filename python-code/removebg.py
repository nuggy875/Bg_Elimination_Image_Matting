import cv2
import numpy as np
import os
import os.path as osp
import sys
from matplotlib import pyplot as plt

#== Parameters =======================================================================
#BLUR = 21
#CANNY_THRESH_1 = 10
#CANNY_THRESH_2 = 200
#MASK_DILATE_ITER = 10
#MASK_ERODE_ITER = 10
#MASK_COLOR = (0.0,0.0,1.0) # In BGR format


BLUR = 5
CANNY_THRESH_1 = 10
CANNY_THRESH_2 = 10
MASK_DILATE_ITER = 10
MASK_ERODE_ITER = 10
MASK_COLOR = (0.0,0.0,0.0) # In BGR format


def cannyAlg(input_img, output_img):
    #== Processing =======================================================================

    #-- Read image -----------------------------------------------------------------------
    img = cv2.imread(input_img)
    # gray scaling
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    #-- Edge detection -------------------------------------------------------------------
    edges = cv2.Canny(gray, CANNY_THRESH_1, CANNY_THRESH_2)
    edges = cv2.dilate(edges, None)
    edges = cv2.erode(edges, None)

    #-- Find contours in edges, sort by area ---------------------------------------------
    contour_info = []
    # Previously, for a previous version of cv2, this line was: 
    # _, contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    # Thanks to notes from commenters, I've updated the code but left this note
    for c in contours:
        contour_info.append((
            c,
            cv2.isContourConvex(c),
            cv2.contourArea(c),
        ))
    contour_info = sorted(contour_info, key=lambda c: c[2], reverse=True)
    max_contour = contour_info[0]

    #-- Create empty mask, draw filled polygon on it corresponding to largest contour ----
    # Mask is black, polygon is white
    mask = np.zeros(edges.shape)
    cv2.fillConvexPoly(mask, max_contour[0], (255))

    #-- Smooth mask, then blur it --------------------------------------------------------
    mask = cv2.dilate(mask, None, iterations=MASK_DILATE_ITER)
    mask = cv2.erode(mask, None, iterations=MASK_ERODE_ITER)
    mask = cv2.GaussianBlur(mask, (BLUR, BLUR), 0)
    mask_stack = np.dstack([mask]*3)    # Create 3-channel alpha mask

    #-- Blend masked img into MASK_COLOR background --------------------------------------
    mask_stack  = mask_stack.astype('float32') / 255.0          # Use float matrices, 
    img         = img.astype('float32') / 255.0                 #  for easy blending

    masked = (mask_stack * img) + ((1-mask_stack) * MASK_COLOR) # Blend
    masked = (masked * 255).astype('uint8')                     # Convert back to 8-bit 

    tmp = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    _,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
    b, g, r = cv2.split(masked)
    rgba = [b,g,r, alpha]
    dst = cv2.merge(rgba,4)

    cv2.imshow('img', dst)                                   # Display
    cv2.waitKey()
    cv2.imwrite(output_img, dst)           # Save


def grabCut(input_img, output_img):
    img = cv2.imread(input_img)
    mask = np.zeros(img.shape[:2], np.uint8)
    bgdModel = np.zeros((1,65), np.float64)
    fgdModel = np.zeros((1,65), np.float64)
    rect = (50,50,450,290)
    cv2.grabCut(img,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)
    mask2 = np.where((mask==2)|(mask==0), 0, 1).astype('uint8')
    img = img*mask2[:,:,np.newaxis]
    plt.imshow(img), plt.colorbar(), plt.show()



# python removebg.py 1 test5
# mode = 1
# imageFileName = test5

if __name__ == "__main__":
    if len(sys.argv) == 1 or len(sys.argv) == 2:
        print('ERROR:EnvVarialbleRequired')
        exit()
        
    input_img_path = osp.realpath('../public/image/'+sys.argv[2]+'.jpg')
    det_path = osp.realpath('../public/result')
    if not os.path.exists(det_path):
        os.makedirs(det_path)
    output_img_path = osp.join(det_path, sys.argv[2]+'_'+sys.argv[1]+'_rst.png')

    if not os.path.exists(input_img_path):
        print('ERROR:ImageNotExists')
        exit()
    
    if sys.argv[1] == '1':
        cannyAlg(input_img_path, output_img_path)
    elif sys.argv[1] == '2':
        grabCut(input_img_path, output_img_path)
    else:
        print('else')
        

    





    