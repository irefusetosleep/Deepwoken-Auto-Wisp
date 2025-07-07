threshold = 0.6 #mess with this if its failing to find the ritual cast box

#run this script if either:
# This is the first time you're using this program
# You get a new monitor/s

import keyboard
from PIL import Image
import cv2
import numpy as np
import pygetwindow as gw
from screeninfo import get_monitors
import mss
import time

template = cv2.imread("Wisp_Box_Lines.png")
template_grey = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
template_w, template_h = template_grey.shape[::-1]

def get_roblox_monitor(): #Returns the display roblox is open on
    while True: 
        for w in gw.getWindowsWithTitle("Roblox"):
            if w.isMaximized == False:
                w.maximize()
            center_y = w.left + w.width // 2
            center_x = w.top + w.height // 2

            monitor = None
            for m in get_monitors():
                if (m.x <= center_x < m.x + m.width and
                    m.y <= center_y < m.y + m.height):
                    monitor = m
            if monitor:
                print("Got monitor!")
                return monitor
            else:
                print("Couldnt get monitor")
        else:
            print("Open roblox in fullscreen buddy")
            time.sleep(.5)


def get_wisp_box():
    print("Getting wisp box")

    monitor = get_roblox_monitor()

    while True:
        with mss.mss() as sct:
            bbox = {"left": monitor.x,
                    "top": monitor.y,
                    "width": monitor.width,
                    "height": monitor.height,
                    }
            screenshot = sct.grab(bbox)

            # Save or process
            img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
            img.save("monitor_capture.png")
            
            # Convert to a format OpenCV understands (BGRA to BGR)
            img = np.array(screenshot)
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

            # Match template
            result = cv2.matchTemplate(img_gray, template_grey, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= threshold:
                top_left = max_loc
                bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
                print(f"Found at {top_left}, size: {template_w}x{template_h}")

                with open("box_location.txt", "w+") as f:
                    f.write(f"TopLeft={top_left}\nBottomRight={bottom_right}")

                # Optionally, move mouse or crop this region
                region = img_bgr[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]

                # Save or display for debug
                cv2.imwrite("matched_region.png", region)
                
                exit()
            else:
                print("Image not found.")

get_wisp_box()

keyboard.wait()
