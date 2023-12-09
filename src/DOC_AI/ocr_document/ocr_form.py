# -----------------------------
#   USAGE
# -----------------------------
# python ocr_form.py --image scans/scan_01.jpg --template form_w4.png

# -----------------------------
#   IMPORTS
# -----------------------------
# Import the necessary packages
from pyimagesearch.alignment.align_images import align_images
from collections import namedtuple
import pytesseract
import argparse
import imutils
import cv2


# -----------------------------
#   FUNCTIONS
# -----------------------------
def cleanup_text(text):
    # Strip out non-ASCII text so we can draw the text on the image using OpenCV
    return "".join([c if ord(c) < 128 else "" for c in text]).strip()


# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True, help="Path to input image that we'll align to template")
ap.add_argument("-t", "--template", required=True, help="Path to input template image")
args = vars(ap.parse_args())

# Create a named tuple which we can use to create locations of the input document which is going to be OCR
OCRLocation = namedtuple("OCRLocation", ["id", "bbox", "filter_keywords"])

# Define the locations of each area of the document which are going to be OCR
OCR_LOCATIONS = [
    OCRLocation("step1_first_name", (265, 237, 751, 106), ["middle", "initial", "first", "name"]),
    OCRLocation("step1_last_name", (1020, 237, 835, 106), ["last", "name"]),
    OCRLocation("step1_address", (265, 336, 1588, 106), ["address"]),
    OCRLocation("step1_city_state_zip", (265, 436, 1588, 106), ["city", "zip", "town", "state"]),
    OCRLocation("step5_employee_signature", (319, 2516, 1487, 156),
                ["employee", "signature", "form", "valid", "unless", "you", "sign"]),
    OCRLocation("step5_date", (1804, 2516, 504, 156), ["date"]),
    OCRLocation("employee_name_address", (265, 2706, 1224, 180), ["employer", "name", "address"]),
    OCRLocation("employee_ein", (1831, 2706, 448, 180), ["employer", "identification", "number", "ein"]),
]

# Load the input image and template from disk
print("[INFO] Loading images...")
image = cv2.imread(args["image"])
template = cv2.imread(args["template"])

# Align the images
print("[INFO] Aligning images...")
aligned = align_images(image, template)

# Initialize a results list to store the document OCR parsing results
print("[INFO] OCR'ing document...")
parsingResults = []

# Loop over the locations of the document we are going to OCR
for loc in OCR_LOCATIONS:
    # Extract the OCR ROI from the aligned image
    (x, y, w, h) = loc.bbox
    roi = aligned[y:y + h, x:x + w]
    # OCR the ROI using Tesseract
    rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(rgb)
    # Break the text into lines and loop over them
    for line in text.split("\n"):
        # If the line is empty, ignore it
        if len(line) == 0:
            continue
        # Convert the line to lowercase and then check to see if the line contains any of the filter keywords
        # (These keywords are part of the *form itself* and should be ignored)
        lower = line.lower()
        count = sum([lower.count(x) for x in loc.filter_keywords])
        # If the count is zero than we know we are *not* examining a text field that is part of the document itself
        # (ex., info, on the field, an example, help text, etc.)
        if count == 0:
            # Update the parsing results dictionary with the OCR'd text if the line is *not* empty
            parsingResults.append((loc, line))

# Initialize a dictionary to store our final OCR results
results = {}

# Loop over the results of parsing the document
for (loc, line) in parsingResults:
    # Grab any existing OCR result for the current ID of the document
    r = results.get(loc.id, None)
    # If the result is None, initialize it using the text and location namedtuple
    # (Converting it to a dictionary as namedtuples are not hashable)
    if r is None:
        results[loc.id] = (line, loc._asdict())
    # Otherwise, there exists a OCR result for the current area of the document, in order to append to the existing line
    else:
        # Unpack the existing OCR result and append the line to the existing text
        (existingText, loc) = r
        text = "{}\n{}".format(existingText, line)
        # Update the results dictionary
        results[loc["id"]] = (text, loc)


# Loop over the results
for (locID, result) in results.items():
    # Unpack the result tuple
    (text, loc) = result
    # Display the OCR result to our terminal
    print(loc["id"])
    print("=" * len(loc["id"]))
    print("{}\n\n".format(text))
    # Extract the bounding box coordinates of the OCR location and
    # then strip out non-ASCII text in order to draw the text on the output image using OpenCV
    (x, y, w, h) = loc["bbox"]
    clean = cleanup_text(text)
    # Draw a bounding box around the text
    cv2.rectangle(aligned, (x, y), (x + w, y + h), (0, 255, 0), 2)
    # Loop over all lines in the text
    for (i, line) in enumerate(text.split("\n")):
        # Draw the line on the output image
        startY = y + (i * 70) + 40
        cv2.putText(aligned, line, (x, startY), cv2.FONT_HERSHEY_SIMPLEX, 1.8, (0, 0, 255), 5)
# Show the input and output images, resizing it such that they fit on the screen
cv2.imshow("Input", imutils.resize(image, width=700))
cv2.imshow("Output", imutils.resize(aligned, width=700))
cv2.waitKey(0)