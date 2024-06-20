import io
import re
import cv2
import yaml
import torch
import base64
import imutils
import logging
import requests
import unidecode
import collections
import numpy as np
from PIL import Image
from io import BytesIO
from datetime import timedelta

def load_image(image_url):
    try:
        if "http://" not in image_url:
            pil_image = Image.open(image_url).convert('RGB')
        else:
            response = requests.get(image_url)
            if response.status_code != 200:
                return None
            pil_image = Image.open(BytesIO(response.content)).convert('RGB')

        img = np.array(pil_image)
        if len(img.shape) != 3:
            raise ValueError('Image Error')

        if img.shape[2] < 3:
            raise ValueError('img.shape = %d != 3' % img.shape[2])
        
        if img.shape[2] == 4:
            #convert the image from BGRA2RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img
    except Exception as ex:
        logging.info("exception error from load image: {}".format(ex))
        return None

def encode_image(image, cv=True):
    """
    input: cv2 image
    output: base64 encoded image
    """
    image = np.array(image)
    if cv:
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    _, im_arr = cv2.imencode('.jpg', image)
    im_bytes = im_arr.tobytes()
    b64_string = base64.b64encode(im_bytes)
    image_base64 = b64_string.decode("utf-8")
    return image_base64

def decode_img(img_base64):
    """
    input: base64 encoded image
    output: cv2 image
    """
    img = img_base64.encode()
    img = base64.b64decode(img)
    img = np.frombuffer(img, dtype=np.uint8)
    img = cv2.imdecode(img, flags=cv2.IMREAD_COLOR)
    return img

# define a function for horizontally concatenating images of different heights 
def hconcat_resize(img_list, interpolation=cv2.INTER_CUBIC):
    # take minimum hights
    h_min = min(img.shape[0] 
                for img in img_list)
      
    # image resizing 
    im_list_resize = [cv2.resize(img,
                       (int(img.shape[1] * h_min / img.shape[0]),
                        h_min), interpolation
                                 = interpolation) 
                      for img in img_list]
      
    # return final image
    return cv2.hconcat(im_list_resize)

def clip_boxes(boxes, shape):
    # Clip boxes (xyxy) to image shape (height, width)
    if isinstance(boxes, torch.Tensor):  # faster individually
        boxes[:, 0].clamp_(0, shape[1])  # x1
        boxes[:, 1].clamp_(0, shape[0])  # y1
        boxes[:, 2].clamp_(0, shape[1])  # x2
        boxes[:, 3].clamp_(0, shape[0])  # y2
    else:  # np.array (faster grouped)
        boxes[:, [0, 2]] = boxes[:, [0, 2]].clip(0, shape[1])  # x1, x2
        boxes[:, [1, 3]] = boxes[:, [1, 3]].clip(0, shape[0])  # y1, y2

def blur_detection(image, size=30, threshold=10):
    if max(image.shape[:2]) > 250:
        size = 20
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	# grab the dimensions of the image and use the dimensions to
	# derive the center (x, y)-coordinates
    (h, w) = gray.shape
    (cX, cY) = (int(w / 2.0), int(h / 2.0))

    fft = np.fft.fft2(gray)
    fftShift = np.fft.fftshift(fft)

    # zero-out the center of the FFT shift (i.e., remove low
	# frequencies), apply the inverse shift such that the DC
	# component once again becomes the top-left, and then apply
	# the inverse FFT
    fftShift[cY - size:cY + size, cX - size:cX + size] = 0
    fftShift = np.fft.ifftshift(fftShift)
    recon = np.fft.ifft2(fftShift)

    # compute the magnitude spectrum of the reconstructed image,
    # then compute the mean of the magnitude values
    magnitude = 20 * np.log(np.abs(recon))
    mean = np.mean(magnitude)

    # the image will be considered "blurry" if the mean value of the
    # magnitudes is less than the threshold value
    blur_result = mean <= threshold

    return blur_result

def check_valid_image(image):
    """"
    Check image is not blur and detectable
    input: image, blur_detection para: {size, threshold}
    output: status
    """
    status = "200"
    if image is None:
        status = "461"
        return status

    check_blur = blur_detection(image)
    if check_blur:
        status = "465"

    return status

def vconcat_2_images(image1, image2):
    """"
    Desc: Concatenate 2 images with order from image1 to image2
    Input: image1, image2
    Output: Concatenated image
    """
    dw = image1.shape[1] / image2.shape[1]
    new_w = int(image2.shape[0]*dw)

    image2 = cv2.resize(image2, (image1.shape[1], new_w))
    result_img = cv2.vconcat([image1, image2])
    return result_img

def url_image(client, address_server, image, image_name, bucketName):
    """this function to upload image to cloud (MinIO) 
    Args:
        client (object) : instance of python client API
        address_server (str): address of cloud 
        image (np.array): store image infomation
        image_name (str): name of image
        bucketName (str): name of bucket 

    Returns:
        url (str): url of image after uploading
    """
    buf = io.BytesIO()
    
    img = Image.fromarray(image)
    img.save(buf, format="JPEG")
    length = len(buf.getbuffer())
    buf.seek(0)
    result = None
    objectName=f'{image_name}'
    # upload image 
    result = client.put_object(bucketName, 
                objectName,  
                data=buf,
                length=length, 
                content_type='image/jpeg')
    # Get presigned URL string to download 'my-object' in
    # 'my-bucket' with 12 hours expiry.
    url = client.get_presigned_url(
        "GET",
        bucketName,
        objectName,
        expires=timedelta(hours=12),
    )
    return url

def store_image(client, address_server, image, image_name, bucketName):
    """this function to upload image to cloud (MinIO) 
    Args:
        client (object) : instance of python client API
        address_server (str): address of cloud 
        image (np.array): store image infomation
        image_name (str): name of image
        bucketName (str): name of bucket 

    Returns:
        url (str): url of image after uploading
    """
    
    buf = io.BytesIO()
    if isinstance(image, np.ndarray):
        img = Image.fromarray(image)
    elif "http://" in image:
        response = requests.get(image)
        if response.status_code != 200:
            return None
        image = Image.open(BytesIO(response.content))
        img = Image.fromarray(image)
    else:
        img = decode_img(image)
        img = Image.fromarray(img)
    img.save(buf, format="JPEG")
    length = len(buf.getbuffer())
    buf.seek(0)
    result = None
    objectName=f'{image_name}'
    # upload image 
    result = client.put_object(bucketName, 
                objectName,  
                data=buf,
                length=length, 
                content_type='image/jpeg')
    url="http://"+address_server
    if result is not None:
        url +='/'+bucketName +'/'+ objectName
    else:
        url = ""
    return url

def is_float(str):
        """
        Check if string is float
        Input: Number string
        Output: Boolean"""
        try:
            float(str)
            return True
        except ValueError:
            return False

def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]

def config_form_name_list():
    with open('config/form_name_list.yaml') as yaml_file:
        form_name_list = yaml.safe_load(yaml_file)

    form_name_list = form_name_list['form_name']

    return form_name_list

def config_name_of_column():
    with open('config/name_of_column.yaml') as yaml_file:
        name_of_column = yaml.safe_load(yaml_file)

    return name_of_column

def padding_box(image, box, left_side = 0.0, right_side = 0.0, top_side = 0.0, bottom_side =0.0):
    """
    Extend 2 sides of a box with input values
    Input: box, left_ratio, right_ratio, top_ratio, bottom_ratio
    Output: padding box
    """
    x_max = image.shape[1]
    y_max = image.shape[0]

    p1, p2, p3, p4 = box[0], box[1], box[2], box[3]
    p1[0] = int(p1[0] - (p2[0] - p1[0])*left_side)
    p2[0] = int(p2[0] + (p2[0] - p1[0])*right_side)
    p3[0] = int(p3[0] + (p3[0] - p4[0])*right_side)
    p4[0] = int(p4[0] - (p3[0] - p4[0])*left_side)

    p1[1] = int(p1[1] - (p4[1] - p1[1])*top_side)
    p2[1] = int(p2[1] - (p3[1] - p2[1])*top_side)
    p3[1] = int(p3[1] + (p3[1] - p2[1])*bottom_side)
    p4[1] = int(p4[1] + (p4[1] - p1[1])*bottom_side)

    p1[0] = p4[0] = min(p1[0], p4[0])
    p2[0] = p3[0] = max(p2[0], p3[0])

    p1[1] = p2[1] = min(p1[1], p2[1])
    p3[1] = p4[1] = max(p3[1], p4[1])

    box = [p1, p2, p3, p4]

    for p in box:
        p[0] = max(min(p[0], x_max), 0)
        p[1] = max(min(p[1], y_max), 0)

    return box

def get_text_image(img, box):
    """
    Get text image from bounding box
    Input: Image, bounding box
    Output: Text image
    """
    if np.shape(box) == (4,):
        box = [[box[0],box[1]],[box[2],box[1]],
               [box[2],box[3]],[box[0],box[3]]]
    mask = np.zeros_like(img)
    box = np.int32([box])
    cv2.fillPoly(mask, box, (255, 255, 255))
    masked_image = cv2.bitwise_and(img, mask)
    x, y, w, h = cv2.boundingRect(box)
    text_img = masked_image[y:y+h, x:x+w]
    text_img = cv2.cvtColor(text_img, cv2.COLOR_BGR2RGB)
    return text_img

def draw_boxes(image, boxes):
    """
    Draw the boxes
    Input: the raw image and the list of boxes
    Output: the image
    """
    new_image = image.copy()
    if np.shape(boxes[0]) == (4,2):
        for i in range(len(boxes)):
            box = np.int32(boxes[i])
            cv2.polylines(new_image, [box], True, (255,0,0), 1)
    else:
        for i in range(len(boxes)):
            x1, y1, x2, y2 = boxes[i]
            cv2.rectangle(new_image, (x1, y1), (x2, y2), (255,0,0), 1)

    return new_image

def draw_lines(image, lines, color=(0, 255, 0)):
    """
    Draw the lines
    Input: the raw image and the list of lines
    Output: the image
    """
    for line in lines:
        start_point = (line[0], line[1])
        end_point = (line[2], line[3])
        cv2.line(image, start_point, end_point, color, 2)

    return image

def align_images(image, template, debug=False):
    # Convert both the input image and template to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Initiate SIFT detector
    sift = cv2.SIFT_create()
    # find the keypoints and descriptors with SIFT
    # Here img1 and img2 are grayscale images
    (kpsA, descsA) = sift.detectAndCompute(imageGray,None)
    (kpsB, descsB) = sift.detectAndCompute(templateGray,None)

    # FLANN parameters
    # I literally copy-pasted the defaults
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    search_params = dict(checks=25)   # or pass empty dictionary
    # do the matching
    flann = cv2.FlannBasedMatcher(index_params,search_params)
    raw_matches = flann.knnMatch(descsA,descsB,k=2)
    matchesMask = [[0,0] for i in range(len(raw_matches))]
    matches = []
    for i,(m,n) in enumerate(raw_matches):
        if m.distance < 0.4*n.distance:
            matches.append((m,n))
            matchesMask[i]=[1,0]

    # Check to see if we should visualize the matched keypoints
    if debug:
        draw_params = dict(matchColor = (0,255,0),
                   singlePointColor = (255,0,0),
                   matchesMask = matchesMask,
                   flags = cv2.DrawMatchesFlags_DEFAULT)
        matchedVis = cv2.drawMatchesKnn(image, kpsA, template, kpsB, matches, None, **draw_params)
        matchedVis = imutils.resize(matchedVis, width=1000)
        cv2.imshow("Matched Keypoints", matchedVis)
        cv2.waitKey(0)

    # Allocate memory for the keypoints (x,y-coordinates) from the top matches
    # -- These coordinates are going to be used to compute our homography matrix
    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")

    # Loop over the top matches
    for i,(m,n) in enumerate(matches):
        # Indicate that the two keypoints in the respective images map to each other
        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt

    # Compute the homography matrix between the two sets of matched points
    (H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)

    # Use the homography matrix to align the images
    (h, w) = template.shape[:2]
    aligned = cv2.warpPerspective(image, H, (w, h))

    return aligned

# def preprocess_image(image):
#     """
#     Preprocess image
#     Input: opencv image
#     Output: preprocessed image
#     """
#     # img = cv2.resize(image, None, fx = 5000/image.shape[0], fy = 5000/image.shape[0])
#     img = imutils.resize(image, width=5000)

#     kernel_erosion = np.ones((3,3),np.uint8) # 3,3
#     img = cv2.erode(img,kernel_erosion,iterations = 1)

#     # Increase contrast
#     lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
#     l_channel, a, b = cv2.split(lab_img)

#     # Applying CLAHE to L-channel
#     # feel free to try different values for the limit and grid size:
#     clahe = cv2.createCLAHE(clipLimit=8.0, tileGridSize=(4,4)) # clipLimit=8.0 4,4
#     cl = clahe.apply(l_channel)

#     # Merge the CLAHE enhanced L-channel with the a and b channel
#     limg = cv2.merge((cl,a,b))

#     # Converting image from LAB Color model to GRAY color space
#     brg_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
#     gray_img = cv2.cvtColor(brg_img, cv2.COLOR_BGR2GRAY)

#     # Remove noise
#     thresh = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
#     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
#     gray_img = 255 - cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

#     # Binarize image
#     gray_img = cv2.adaptiveThreshold(gray_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 155, 11)

#     # Erosion
#     kernel_dilation = np.ones((2,2),np.uint8) #2,2
#     erosion = cv2.dilate(gray_img,kernel_dilation,iterations = 1)

#     # Enhance the edges and details
#     kernel_enhancement = np.array([[0, -1, 0],[-1, 5,-1],[0, -1, 0]])
#     erosion = cv2.filter2D(src=erosion, ddepth=-1, kernel=kernel_enhancement)

#     # Resize image
#     # erosion = cv2.resize(erosion, None, fx = 2500/img.shape[0], fy = 2500/img.shape[0])
#     erosion = imutils.resize(erosion, width=2500)

#     erosion = cv2.cvtColor(erosion, cv2.COLOR_GRAY2BGR)

#     return erosion

def preprocess_image(image):
    """
    Preprocess image
    Input: opencv image
    Output: preprocessed image
    """
    img = imutils.resize(image, width=5000)

    # Increase contrast
    lab_img = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab_img)

    # Applying CLAHE to L-channel
    # feel free to try different values for the limit and grid size:
    clahe = cv2.createCLAHE(clipLimit=15.0, tileGridSize=(2,2)) # clipLimit=15 2,2
    cl = clahe.apply(l_channel)

    # Merge the CLAHE enhanced L-channel with the a and b channel
    limg = cv2.merge((cl,a,b))

    # Converting image from LAB Color model to GRAY color space
    brg_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    gray_img = cv2.cvtColor(brg_img, cv2.COLOR_BGR2GRAY)

    # Remove noise
    thresh = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    binary_img = 255 - cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

    # Resize image
    result_img = imutils.resize(binary_img, width=2000)
    result_img = cv2.cvtColor(result_img, cv2.COLOR_GRAY2BGR)

    return result_img

def draw_result_text(img, text,
                     font=cv2.FONT_HERSHEY_COMPLEX,
                     pos=(0, 0),
                     font_scale=3,
                     font_thickness=2,
                     text_color=(0, 0, 0),
                     text_color_bg=(0, 0, 0)):

    x, y = pos
    text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)
    text_w, text_h = text_size
    cv2.rectangle(img, pos, (x + text_w, y + text_h), text_color_bg, -1)
    cv2.putText(img, text, (x, y + text_h + font_scale - 1), font, font_scale, text_color, font_thickness)

    return text_size


def draw_layout_result(image, layout_result, box_width=5, box_alpha=0.2):

    new_image = image.copy()
    color_of_class = {'text':(0,0,255), 'title':(255,0,0),
                      'list':(0,255,255), 'table':(0,255,0),
                      'figure':(127,127,127), 'question':(0,255,255),
                      'answer':(0,0,255), 'date':(255,0,0)}

    for key_layout, value_layout in layout_result.items():
        color_of_box = color_of_class[key_layout]
        # color_of_box = np.random.randint(0, 255, size=3).tolist()
        for i, box in enumerate(value_layout['box']):
            overlay = new_image.copy()
            
            top_left = (box[0], box[1])
            bottom_right = (box[2], box[3])

            cv2.rectangle(new_image, top_left, bottom_right, color_of_box, box_width)

            cv2.rectangle(overlay, top_left, bottom_right, color_of_box, -1)
            new_image = cv2.addWeighted(overlay, box_alpha, new_image, 1 - box_alpha, 0)

            text = key_layout + ' ' + str(round(value_layout['confidence'][i], 2))
            draw_result_text(new_image, text, font_scale=1, pos=top_left, text_color_bg=(255, 255, 255))

    return new_image

def center_of_box(box):
    """
    Find center position of box
    """
    if np.shape(box) == (4, 2):
        center_x = (box[0][0] + box[2][0]) / 2
        center_y = (box[0][1] + box[2][1]) / 2
    else:
        center_x = (box[0] + box[2]) / 2
        center_y = (box[1] + box[3]) / 2

    return center_x, center_y

def find_relative_position(box_1, box_2):
    """
    Find the relative position between box_1 and box_2
    {'same position':0, 'same row':1, 'same column':2, 'different position':3}
    Input: box_1, box_2
    Output: the relative position
    """
    # same position, same row, same column, different position
    relative_position = 3
    center_x, center_y = center_of_box(box_2)
    if np.shape(box_1) == (4, 2):
        x1, y1, x2, y2 = box_1[0][0], box_1[0][1], box_1[3][0], box_1[3][1]
    else:
        x1, y1, x2, y2 = box_1[0], box_1[1], box_1[2], box_1[3]

    if (center_x > x1 and center_x < x2) and (center_y > y1 and center_y < y2):
        relative_position = 0
    elif center_y > y1 and center_y < y2:
        relative_position = 1
    elif center_x > x1 and center_x < x2:
        relative_position = 2
    else:
        relative_position = 3
    
    return relative_position

def find_class_of_box(box, layout_result):
    """
    Input: box, layout_result
    Output: dictionary contains box and text in right layout class
    """
    center_x, center_y = center_of_box(box)

    for key_layout, value_layout in layout_result.items():
        for class_box in value_layout['box']:
            x1, y1, x2, y2 = class_box[0], class_box[1], class_box[2], class_box[3]
            if (center_x > x1 and center_x < x2) and (center_y > y1 and center_y < y2):
                return key_layout
            
    return 'other'

def remove_special_characters(input_string):
    # Define a regular expression pattern to match non-alphanumeric characters
    pattern = re.compile(r'[^a-zA-Z0-9\s]')
    
    # Use the pattern to replace non-alphanumeric characters with an empty string
    result_string = re.sub(pattern, '', input_string)
    
    return result_string

def make_underscore_name(text_list):

    for i, text in enumerate(text_list):
        lower_text = text.lower()
        ascii_text = unidecode.unidecode(lower_text)
        ascii_text = remove_special_characters(ascii_text)
        # text_list[i] = ascii_text.replace(" ", "_")
        ascii_words_in_text = ascii_text.split()

        while '' in ascii_words_in_text:
            ascii_words_in_text.remove('')

        text_list[i] = '_'.join(ascii_words_in_text)

    return text_list


def find_text_in_big_box(detector, recognizer, image):
    # detect all boxes in image
    detection = detector.detect(image)
    if detection is not None:
        if len(detection) > 1:
            detection.sort(key = lambda x: x[0][1])
            for i, box in enumerate(detection):
                relative_position = find_relative_position(detection[i-1], box)
                if relative_position == 1:
                    detection[i][0][1] = min(detection[i-1][0][1], box[0][1])
                    detection[i-1][0][1] = min(detection[i-1][0][1], box[0][1])
            detection.sort(key = lambda x: (x[0][1], x[0][0]))

        # recognize all texts
        recognition = []
        for box in detection:
            cropped_image = get_text_image(image, box)
            cropped_image = Image.fromarray(cropped_image)
            rec_result = recognizer.recognize(cropped_image)
            recognition.append(rec_result)

        text = ' '.join(recognition)
    else:
        text = ''

    return text

def format_data_dict(data_dict):
    # find class table
    table_area = {'table': {'box':[]}}
    for value_template in data_dict:
        if value_template['class'] == 'table':
            table_area['table']['box'] = [value_template['box']]
            data_dict.remove(value_template)
            break

    result = []
    table_question = []
    table_answer = []
    for i, value_template in enumerate(data_dict):
        if len(table_area['table']['box']) > 0:
            class_of_box = find_class_of_box(value_template['box'], table_area)
        else:
            class_of_box = 'other'

        if class_of_box == 'table':
            if value_template['class'] == 'question':
                table_question.append(value_template)
            else:
                table_answer.append(value_template)  
        else:
            if value_template['class'] != 'answer':
                element = value_template
                if value_template['class'] == 'question':
                    element['answer_text'] = [data_dict[i+1]]
                elif value_template['class'] == 'date':
                    date_answer = {'box': value_template['box'],
                                   'text': '',
                                   'class': 'answer'}
                    element['answer_text'] = [date_answer]
                else:
                    element['answer_text'] = []
                result.append(element)

    for question in table_question:
        element = question
        element['answer_text'] = []
        for answer in table_answer:
            relative_position = find_relative_position(question['box'], answer['box'])
            if relative_position == 2:
                element['answer_text'].append(answer)
        result.append(element)
    
    return result

def intersection(line1, line2):
    """
    Finds the intersection of two lines given in Hesse normal form.
    Returns closest integer pixel locations.
    """
    rho1, theta1 = line1[0]
    rho2, theta2 = line2[0]
    A = np.array([
        [np.cos(theta1), np.sin(theta1)],
        [np.cos(theta2), np.sin(theta2)]
    ])
    b = np.array([[rho1], [rho2]])

    x0, y0 = np.linalg.solve(A, b)
    x0, y0 = int(np.round(x0)), int(np.round(y0))
    return [x0, y0]

    

def segmented_intersections(horizontal_lines, vertical_lines):
    """Finds the intersections between groups of lines."""
    intersections = []
    for h_line in horizontal_lines:
        intersections_in_line = []
        for v_line in vertical_lines:
            if intersection(h_line, v_line):
                intersections_in_line.append(intersection(h_line, v_line))
        intersections.append(intersections_in_line)
    return intersections

def create_answer_boxes_in_table(image, table_box):

    # new_image = image.copy()
    # image = imutils.resize(new_image, width=700)

    xt1, yt1, xt2, yt2 = table_box[0], table_box[1], table_box[2], table_box[3]

    w, h = xt2-xt1, yt2-yt1

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Perform HoughLines tranform
    lines = cv2.HoughLines(thresh,1,np.pi/180,500)
    horizontal_lines = []
    vertical_lines = []
    for line in lines:
        # for rho,theta in line:
        rho, theta = line[0]
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a*rho
        y0 = b*rho
        x1 = int(x0 + 3000*(-b))
        y1 = int(y0 + 3000*(a))
        x2 = int(x0 - 3000*(-b))
        y2 = int(y0 - 3000*(a))

        if y1 <= (yt2 - h*0.04) and y1 > (yt1 + h*0.04):
            horizontal_lines.append(line)

        if x1 <= (xt2 - w*0.04) and x1 > (xt1 + w*0.04):
            vertical_lines.append(line)

    horizontal_lines.append(np.array([[yt2, 1.5708]], dtype=float))
    vertical_lines.append(np.array([[xt2, 0]], dtype=float))

    intersections = segmented_intersections(horizontal_lines, vertical_lines)
    for point_in_line in intersections:
        point_in_line.sort(key = lambda x: x[0])
    print(intersections)
    intersections.sort(key = lambda x: (x[0][1], x[0][0]))
    print(intersections)
    answer_boxes = []
    for i in range(len(intersections)-1):
        for j in range(len(intersections[i])-1):
            answer_boxes.append(intersections[i][j]+intersections[i+1][j+1])

    return answer_boxes
