import cv2 as cv
import numpy as np
import tkinter
from tkinter import filedialog
from pathlib import Path

# select images' folder
tkinter.Tk().withdraw() # prevent an empty window from appearing
folder_path = filedialog.askdirectory()
p = Path(folder_path)
# out_dir = p / 'out'
image_files = list(p.glob('*.jpg'))
n_images = len(image_files)
# out_dir.mkdir(parents=True, exist_ok=True) # create new folder if not existed

def detect_corners(image_path):
    # Load the image
    image = cv.imread(image_path, cv.IMREAD_REDUCED_COLOR_4)
    width = image.shape[1]
    height = image.shape[0]
    img_area = width*height
    # print('width=', width, ', height = ', height)
    # Convert the image to grayscale
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # Apply Gaussian blur to remove noise
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    
    # Canny edge detection
    edges = cv.Canny(blurred, 50, 150)
    
    # Find contours
    contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    detected_squares = []
    # Iterate through contours
    for contour in contours:
        perimeter = cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, 0.02 * perimeter, True)
        area = cv.contourArea(contour)
        
        # If the contour has 4 corners (a square) and area is big enough
        if len(approx) == 4 and area>(img_area/2000):
            cv.drawContours(image, [approx], -1, (0, 255, 0), 2)
            # Calculate center point of the square
            M = cv.moments(approx)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                # remove QR code corners
                if cy < (height/15) or cy > (height*0.9): 
                    detected_squares.append((cx, cy))
                    cv.circle(image, (cx,cy),3, (0, 0, 255), 1 )
    # # Show the image with detected squares
    # print(detected_squares)
    # cv.imshow('Square Detection', image)
    # cv.waitKey(0)
    # cv.destroyAllWindows()
    return detected_squares

def sort_corners(corners):
    # Find the centroid of the corners
    centroid = np.mean(corners, axis=0)
    
    # Sort the corners based on their angle relative to the centroid
    sorted_corners = sorted(corners, key=lambda x: np.arctan2(x[1] - centroid[1], x[0] - centroid[0]))
    
    # Now the sorted corners should be in the correct order
    return sorted_corners


def get_cell_location(square_corners, tile_size):
    # Extract the corner coordinates
    top_left, top_right, bottom_right, bottom_left  = square_corners
    top_left= (int(top_left[0]*0.6), int(top_left[1]*1.7))
    top_right = (int(top_right[0]*1.03), int(top_right[1]*1.7))
    bottom_left = (int(bottom_left[0]*0.6), int(bottom_left[1]*0.96))
    bottom_right = (int(bottom_right[0]*1.03), int(bottom_right[1]*0.96))
    # Calculate the number of tiles in each dimension
    num_rows = tile_size[1]
    num_cols = tile_size[0]
    
    # Calculate the width and height of each tile
    tile_width = (top_right[0] - top_left[0]) // num_cols
    tile_height = (bottom_left[1] - top_left[1]) // num_rows
    
    # List to store tile coordinates
    tile_coordinates = []
    
    # Iterate through rows
    for row in range(num_rows):
        # Iterate through columns
        for col in range(num_cols):
            # Calculate starting and ending coordinates for the tile
            start_x = top_left[0] + col * tile_width
            end_x = start_x + tile_width
            start_y = top_left[1] + row * tile_height
            end_y = start_y + tile_height
            
            # Append the coordinates of the tile (top_left and bottom right)
            tile_coordinates.append(((start_x, start_y), (end_x, end_y)))
    
    return tile_coordinates


for count, image in enumerate(image_files):
    roi = detect_corners(str(image))  # centers of squares
    roi = sort_corners(roi)           # sort the coordinates
    # print(roi)
    number_of_cell = (8, 8)           
    cell_coordinates = get_cell_location(roi,number_of_cell)  
    img = cv.imread(str(image), cv.IMREAD_REDUCED_COLOR_4)
    for cell in cell_coordinates:
        cv.rectangle(img, cell[0], cell[1], (0, 0, 255), 1)
    cv.imshow('Square Detection', img)
    cv.waitKey(0)
    cv.destroyAllWindows()
  
   
    
    