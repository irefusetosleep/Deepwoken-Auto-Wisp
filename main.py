import tkinter as tk
import pydirectinput
import pytesseract
from PIL import ImageGrab
import time
import keyboard
import cv2
import numpy as np
from PIL import Image

wisp_keys = {"Z", "X", "C", "V"}
    
letters = {"Z.png", "X.png", "C.png", "V.png"}
letter_threshold = .8

def match_letter(source):
    source_g = cv2.cvtColor(source, cv2.COLOR_RGB2GRAY)
    
    for letter in letters:
        template = cv2.imread(letter, cv2.IMREAD_COLOR)
        template_g = cv2.cvtColor(template, cv2.COLOR_RGB2GRAY)
        w, h = template_g.shape[::-1]

        result = cv2.matchTemplate(source_g, template_g, cv2.TM_CCOEFF_NORMED)
        loc = np.where(result >= letter_threshold)

        if len(loc[0]) > 0:
            return letter.split(".png")[0]


def scan_screen(bbox):
    #chop image into 5
    img = ImageGrab.grab(bbox)
    img.save("Screen_Grab.png")

    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    height, width, channels = cv_img.shape
    piece_width = width // 5  # integer division to get width per piece

    pieces = []
    for i in range(5):
        start_x = i * piece_width
        # Make sure last piece takes the remaining pixels (in case width not divisible by 5)
        end_x = (i + 1) * piece_width if i < 4 else width
        piece = cv_img[:, start_x:end_x]
        pieces.append(piece)

    # Now pieces[0], pieces[1], ..., pieces[4] contain the 5 image slices

    # Example: Show each piece in a window (press any key to close each)
    for i, piece in enumerate(pieces):
        if i == 0: 
            continue
        filename = f"piece_{i+1}.png"
        cv2.imwrite(filename, piece)
        
        letter_match = match_letter(piece)
        if letter_match:
            print(letter_match)
            pydirectinput.press(letter_match.lower())
            time.sleep(.01)


def type_shit(shit_to_type):
    print("Typing shit")


#setup start/stop hotkey
TOGGLE_KEY = 'f5'

state = {"running":False}

def on_toggle():
    state["running"] = not state["running"] #fuck off python
    print("Running:", state["running"])

keyboard.add_hotkey(TOGGLE_KEY, on_toggle)

#main loop

LOOP_TIME = .2 #how long the machine waits between screen scans
KEYPRESS_SPEED = LOOP_TIME / 1.5 #computer scans every .2 seconds, presses the keys this much faster

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

print("TopLeft:", top_left)
print("BottomRight:", bottom_right)           

bound_box = (top_left[0], top_left[1], bottom_right[0], bottom_right[1]) #ok cool we know where to look
print(bound_box)

while True:
    if state["running"] == True:
        scan_screen(bound_box)

keyboard.wait() #keeps the program alive
