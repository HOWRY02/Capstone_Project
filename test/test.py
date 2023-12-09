# from thefuzz import fuzz, process

# text = 'don xin mien thi'
# text_1 = 'don xin mien thi anh van dau ra'

# print(fuzz.ratio(text, text_1))
# print(fuzz.partial_ratio(text, text_1))
# print(fuzz.token_set_ratio(text, text_1))
# print(fuzz.token_sort_ratio(text, text_1))

import cv2 
import numpy as np 
  
  
# Read image 
image = cv2.imread("src/data_form/don_mien_thi.png")
image = cv2.resize(image, None, fx = 500/image.shape[0], fy = 500/image.shape[0])
  
# Select ROI 
r = cv2.selectROI("select the area", image) 
  
# Crop image 
cropped_image = image[int(r[1]):int(r[1]+r[3]),  
                      int(r[0]):int(r[0]+r[2])] 
  
# Display cropped image 
cv2.imshow("Cropped image", cropped_image) 
cv2.waitKey(0)
cv2.destroyAllWindows()