import tkinter as tk
import cv2
from PIL import Image, ImageTk
from threading import Thread


def display_roi(event):
    global tkimg

    if image:
        tkimg = ImageTk.PhotoImage(image)
        cropped_lbl.config(image=tkimg)

def select_roi():
    global image

    img = cv2.imread("src/data_form/don_mien_thi.png")
    roi  = cv2.selectROI(img)

    imCrop = img[int(roi[1]):int(roi[1]+roi[3]), int(roi[0]):int(roi[0]+roi[2])]
    
    if len(imCrop)>0:
        image = Image.fromarray(cv2.cvtColor(imCrop, cv2.COLOR_BGR2RGB))

    # cv2.destroyAllWindows()
    root.event_generate("<<ROISELECTED>>")

def start_thread():

    thread = Thread(target=select_roi, daemon=True)
    thread.start()


root = tk.Tk()

cropped_lbl = tk.Label(root)
cropped_lbl.pack(expand=True, fill="both")

tk.Button(root, text="select ROI", command=start_thread).pack()

root.bind("<<ROISELECTED>>", display_roi)
root.mainloop()