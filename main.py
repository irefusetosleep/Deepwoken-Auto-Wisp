DELAY = 0 #if you're high ping ritual casts will be delayed, tweak this to work with your ping

letter_threshold = .7 #tweak this if the macro has trouble reading keys (lower = less strict, higher = stricter)

#dont edit anything below here these are the only settings

import tkinter as tk
import pydirectinput
import pytesseract
import time
import keyboard
import cv2
import numpy as np
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
import mss
import threading

pydirectinput.PAUSE = 0.05

executor = ThreadPoolExecutor(max_workers=4)

letters = {"Z.png", "X.png", "C.png", "V.png"}

#creates templates for tesseract to use

templates = {}
for name in letters:
    img = cv2.imread(name, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    templates[name.split(".png")[0]] = gray

def match_letter(source):
    source_g = cv2.cvtColor(source, cv2.COLOR_RGB2GRAY) # convert to greyscale for easier reading

    for name, template_g in templates.items():
        result = cv2.matchTemplate(source_g, template_g, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= letter_threshold)
        if len(loc[0]) > 0:
            return name

buffer = {}
buffer_lock = threading.Lock()

def read(piece, i):
    letter_match = match_letter(piece)
    with buffer_lock:
            buffer[i-1] = letter_match.lower() if letter_match else "N/A"

def grab_screen(bbox):
    with mss.mss() as sct:
        monitor = {"top": bbox[1], "left": bbox[0], "width": bbox[2]-bbox[0], "height": bbox[3]-bbox[1]}
        img = np.array(sct.grab(monitor))
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

def scan_screen(bbox):
    #chop image into 5

    cv_img = grab_screen(bbox)
    _, width, _ = cv_img.shape
    piece_width = width // 5  # integer division to get width per piece

    buffer.clear()
    futures = []

    for i in range(5):
        start_x = i * piece_width
        # Make sure last piece takes the remaining pixels (in case width not divisible by 5)
        end_x = (i + 1) * piece_width if i < 4 else width
        piece = cv_img[:, start_x:end_x]
        futures.append(executor.submit(read, piece, i))


    for future in futures:
        future.result() #waits for threads to complete

    if all(buffer.get(i, "N/A") == "N/A" for i in range(4)):
        return  # nothing to type
    type_shit()

def type_shit():
    for i in range(4):
        letter = buffer[i]
        if letter == "N/A":
            break #should work because we're going in order

        pydirectinput.press(letter)
        time.sleep(DELAY)
    buffer.clear()


#setup start/stop hotkey
state = {"running":True}

#main loop
top_left = (0,0)
bottom_right = (0,0)

with open('box_location.txt', 'r') as file:
    for line in file:
        key, value = line.strip().split('=')
        # Remove parentheses and spaces, then split by comma
        coords = value.strip().strip('()').replace(' ', '').split(',')
        x, y = int(coords[0]), int(coords[1])
        
        if key == "TopLeft":
            top_left = (x, y)
        elif key == "BottomRight":
            bottom_right = (x, y)

bound_box = (top_left[0], top_left[1], bottom_right[0], bottom_right[1]) #ok cool we know where to look

while True:
    time.sleep(.1)
    if state["running"] == True:
        scan_screen(bound_box)
