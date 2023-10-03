import io
import re
import cv2
import json
import yaml
import torch
import base64
import logging
import requests
import numpy as np
from PIL import Image
from io import BytesIO
from datetime import timedelta

def load_image(image_url):
    try:
        if "http://" not in image_url:
            pil_image = Image.open(image_url)
        else:
            response = requests.get(image_url)
            if response.status_code != 200:
                return None
            pil_image = Image.open(BytesIO(response.content))
        exif1 = pil_image._getexif()

        if exif1 is not None and 274 in exif1:
            if exif1[274] == 3:
                pil_image=pil_image.rotate(180, expand=True)
            elif exif1[274] == 6:
                pil_image=pil_image.rotate(270, expand=True)
            elif exif1[274] == 8:
                pil_image=pil_image.rotate(90, expand=True)

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

# define a function for horizontally 
# concatenating images of different
# heights 
def hconcat_resize(img_list, 
                   interpolation 
                   = cv2.INTER_CUBIC):
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

def calculate_list_distance(list_combination):
    # Calculate distance in list pair
    all_dist = []
    for cluster in list_combination:
        pts_dist = []
        for idx_pt1 in range(len(cluster) - 1):
            for idx_pt2 in range(idx_pt1 + 1, len(cluster)):
                pt1 = np.array(cluster[idx_pt1])
                pt2 = np.array(cluster[idx_pt2])
                dist = np.linalg.norm(pt1 - pt2)
                pts_dist.append(dist)
        all_dist.append(pts_dist)
    all_dist = np.array(all_dist)
    return all_dist

def calculate_merging_threshold(det):
    length_array = []
    for box in det:
        bbx = box[:4]
        length = np.sqrt(pow(bbx[0] - bbx[2], 2) + pow(bbx[1] - bbx[3], 2))
        length_array.append(length)
    chosen_idx = np.argmax(np.array(length_array))
    chosen_box = det[chosen_idx][:4]
    length = chosen_box[2] - chosen_box[0]
    margin_threshold = int(length/10) + 1
    return margin_threshold

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

def image_alignment(img, temp_img):
        """Image aligment using feature-based matching
        Input: Image
        Output: Wrapped image """
        # Convert to gray image
        cv2.setRNGSeed(0)
        height = temp_img.shape[0]
        ratio = round(height/img.shape[0], 3)
        width = int(img.shape[1]*ratio)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA) 

        input_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        temp_gray = cv2.cvtColor(temp_img.copy(), cv2.COLOR_BGR2GRAY)
        
        # Detect feature in both images
        sift = cv2.SIFT_create()
        (keypoints1, descriptors1) = sift.detectAndCompute(temp_gray, None)
        (keypoints2, descriptors2) = sift.detectAndCompute(input_gray, None)

        # Find nearest neighbor between the feature descriptors of the images
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=40) # or pass empty dictionary
        flann = cv2.FlannBasedMatcher(index_params,search_params)
        matches = flann.knnMatch(descriptors2, descriptors1, k=2)
        # Filter out matches based on distance ratio test
        good_matches = []
        for i,(m,n) in enumerate(matches):
            if m.distance < 0.7*n.distance:
                good_matches.append(m)

        # Draw matches   
        matching_result = cv2.drawMatches(img,keypoints2,temp_img,keypoints1,good_matches,None)
        
        # Estimate affine transformation using RANSAC
        input_matches = np.float32([ keypoints2[m.queryIdx].pt for m in good_matches ]).reshape(-1,1,2)
        template_matches = np.float32([ keypoints1[m.trainIdx].pt for m in good_matches ]).reshape(-1,1,2)
        M, _ = cv2.estimateAffine2D(input_matches, template_matches, ransacReprojThreshold=10.0)

        # Warp input image to template image
        inputReg = cv2.warpAffine(img, M, (temp_img.shape[1], temp_img.shape[0]))
        cv2.imwrite('src/OCR/template_matching/matches.jpg', matching_result)  
        cv2.imwrite('src/OCR/template_matching/inputReg.jpg', inputReg)
        return inputReg

def digit_correction(key, text):
        """
        Check and correct digit
        Input: key, text
        Output: corrected text
        """
        # just keep number and dot digit in ID and Age part
        if key in ['ID', 'Age']:
            text = re.sub(r"[^0-9]", "", text)
        # check gender value
        elif key == 'Gender':
            if 'Fe' in text or 'em' in text:
                text = 'Female'
            else:
                text= "Male"
        # remove alphabet digit in "Body Composition Analysis" part
        elif key == 'Body Composition Analysis':
            text = re.sub(r"[a-zA-Z]", "", text)
            text = re.sub(r" ", "" , text)
            last_index = text.rfind('.')
            count_digit = len(text) - last_index - 1
            first_index = text.find('.')
            text = text[:first_index + count_digit + 1] + ' ' + text[first_index + count_digit:]
            text = text.split(' ')[0]
        # just keep number, "+", "-", ".", "/", ":" and " " in the remaining fields.
        else:
            text = re.sub(r"[^0-9\+\-./: ]", "", text) 
            if is_float(text):
                if 'Control' in key:
                    if '-' in text or '+' in text:
                        text = text[0] + str(float(text[1:]))
                else:
                    text = str((float(text)))
        return text

def flatten_comprehension(matrix):
    return [item for row in matrix for item in row]

def config_common_words_list(lang="vi"):
    with open('config/common_words_list.yaml') as yaml_file:
        common_words_list = yaml.safe_load(yaml_file)

    common_words_list = common_words_list[lang]

    return common_words_list

def config_collection_medicine(lang="vi"):
    with open('config/collection_medicine.yaml') as yaml_file:
        collection_medicine = yaml.safe_load(yaml_file)

    collection_dosage = collection_medicine[lang]["collection_dosage"]
    collection_timing = collection_medicine[lang]["collection_timing"]
    dosage_cases = collection_medicine[lang]["dosage_cases"]
    collection_duration = collection_medicine[lang]["collection_duration"]

    return collection_dosage, dosage_cases, collection_timing, collection_duration

def config_collection_user_info(lang="vi"):
    with open('config/collection_user_info.yaml') as yaml_file:
        collection_user_info = yaml.safe_load(yaml_file)

    collection_name = collection_user_info[lang]["collection_name"]
    collection_age = collection_user_info[lang]["collection_age"]
    collection_gender = collection_user_info[lang]["collection_gender"]
    collection_follow_up = collection_user_info[lang]["collection_follow_up"]

    return collection_name, collection_age, collection_gender, collection_follow_up

def process_number(num_string):

    if num_string is not None:
        return num_string.replace(',', '.')
    else:
        return num_string

def preprocess_text(text):
    """
    Add a space between consecutive words
    Input: the raw text
    Output: the right format text
    """
    pos = []
    for i in range(1, len(text)):
        if text[i].isalpha() and text[i-1].isnumeric():
            pos.append(i)
        elif (text[i].isnumeric() or text[i].isspace()) and text[i-1].isalpha():
            pos.append(i)

        if text[i].isalnum() == False:
            if i != len(text)-1:
                if text[i+1].isnumeric() and text[i-1].isnumeric():
                    continue
            pos.append(i)
            pos.append(i+1)
        else:
            if text[i].islower() and text[i-1].isupper():
                pos.append(i-1)
            elif text[i].isupper() and text[i-1].islower():
                pos.append(i)

    pos.sort(reverse=True)
    textlist = list(text)
    for i in pos:
        textlist.insert(i, ' ')
    text = ''.join(textlist)
    text_split = text.split()
    for i, val in enumerate(text_split):
        if val == 'I':
            text_split[i] = '1'
    text = ' '.join(text_split)

    return text

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
    mask = np.zeros_like(img)
    box = np.int32([box])
    cv2.fillPoly(mask, box, (255, 255, 255))
    masked_image = cv2.bitwise_and(img, mask)
    x, y, w, h = cv2.boundingRect(box)
    text_img = masked_image[y:y+h, x:x+w]
    text_img = cv2.cvtColor(text_img, cv2.COLOR_BGR2RGB)
    return text_img


def draw_result_image(image, solutions):
    """
    Draw the result image with the boxes to locate the solutions
    Input: the raw image and solutions
    Output: the result image
    """
    for solution in solutions:
        color = tuple(np.random.choice(range(256), size=3).tolist())
        for key in list(solution.keys()):
            boxes = solution[key]
            for i in range(len(boxes)):
                box = np.int32(boxes[i])
                cv2.polylines(image, [box], True, color, 1)

        for key in list(solution.keys()):
            boxes = solution[key]
            for i in range(len(boxes)):
                box = boxes[i]
                cv2.putText(
                    img = image,
                    text = key,
                    org = box[0],
                    fontFace = cv2.FONT_HERSHEY_TRIPLEX,
                    fontScale = 0.4,
                    color = (0, 0, 255),
                    thickness = 1
                    )

    return image


def draw_boxes_ocr(image, boxes):
    """
    Draw the boxes
    Input: the raw image and the list of boxes
    Output: the image
    """
    for i in range(len(boxes)):
        box = np.int32(boxes[i])
        cv2.polylines(image, [box], True, (255,0,0), 1)

    return image


def draw_lines_ocr(image, lines, color=(0, 255, 0)):
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
