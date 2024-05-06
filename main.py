import pyautogui
import time
import os
import cv2 as cv
import numpy as np
import keyboard
from ahk import AHK

ahk = AHK()

def get_template(template_path):
    template = cv.imread(template_path)
    width = int(template.shape[1] * 1)
    height = int(template.shape[0] * 1)
    dim = (width, height)
    resized_template = cv.resize(template, dim, interpolation=cv.INTER_AREA)
    return resized_template

def find_template_in_image(image, template, threshold=0.8):
    res = cv.matchTemplate(image, template, cv.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    return loc

def click_at_location(x, y):
    pyautogui.moveTo(x, y, 0.25)
    time.sleep(0.25)
    pyautogui.click()
    time.sleep(0.25)

def click_if_pixel_diff(x, y):
    p = pyautogui.pixel(x, y)
    if p[0] != p[1] or p[0] != p[2]:
        click_at_location(x, y)

def click_img(template_path, confidence=0.8, action="Click"):
    im1 = np.array(pyautogui.screenshot())[:, :, ::-1]
    template = get_template(template_path)
    loc = find_template_in_image(im1, template, confidence)
    if loc[0].size != 0:
        x, y = int(loc[1][0] + template.shape[1] / 2), int(loc[0][0] + template.shape[0] / 2)
        click_if_pixel_diff(x, y)
        print(f"{action}: {template_path}")
        return 1
    return 0

def process_images(directory):
    for f in os.listdir(directory):
        if click_img(os.path.join(directory, f), action="Process Image") == 1:
            if click_img('imgs\\2_close.png', action="Close Image") == 1:
                continue
            return 1
    return 0

def get_action():
    return process_images('imgs\\action')

def get_collect():
    return process_images('imgs\\collect')

def get_refine():
    return process_images('imgs\\refine')

def click_mid():
    x, y = pyautogui.size()
    mid_x = int(x / 2) - 10
    mid_y = int(y / 1.975)
    pyautogui.moveTo(mid_x, mid_y, 0.75)
    time.sleep(5)
    ahk.click()
    time.sleep(0.2)
    ahk.click()
    time.sleep(0.3)
    ahk.click()
    time.sleep(0.5)
    print("Clicked Mid")

def click_event():
    x, y = pyautogui.size()
    mid_x = int(x / 2) - 10
    mid_y = int((y / 1.975) + 150)
    pyautogui.moveTo(mid_x, mid_y, 0.75)
    time.sleep(3)
    ahk.click()
    time.sleep(2)
    print("Clicked Event")

def finalize_actions():
    time.sleep(0.5)
    click_mid()
    for img in ['0_confirm.png', '1_confirm.png', '2_confirm.png', '3_confirm.png']:
        click_img(f'imgs\\{img}', confidence=0.7, action="Confirm Action")
    click_img(f'imgs\\repair.png', action="Repair")
    click_img(f'imgs\\2_close.png', action="Close 2")
    click_img(f'imgs\\no.png', action="No")
    time.sleep(1)
    print("Finalized Actions")

p = pyautogui.pixel(686, 701)
print(p)

c = 0
stop = True
refine = False
collect = True

print('PRESS [L] TO START')
print('PRESS [K] TO START AND REFINE WOOD/STONE')
print('PRESS [P] TO PAUSE')

while True:
    if keyboard.is_pressed('p'):
        stop = True
        print("PAUSED!")
    if keyboard.is_pressed('l'):
        stop = False
        collect = True
        refine = False
        print("Starting... 2 secs...")
        time.sleep(2)
    if keyboard.is_pressed('k'):
        stop = False
        collect = True
        refine = True
        print("Starting... 2 secs...")
        time.sleep(2)
    if stop:
        continue
    c += 1
    click_img(f'imgs\\3_close.png', confidence=0.7, action="Close 3")
    click_img(f'imgs\\2_close.png', confidence=0.7, action="Close 2")
    click_img(f'imgs\\mission.png', confidence=0.9, action="Mission")
    pyautogui.press('x')
    r = click_img(f'imgs\\event.png', confidence=0.9, action="Event")
    
    if r == 1:
        time.sleep(7)
        click_event()
        time.sleep(2)
        for img in ['0_confirm.png', '1_confirm.png', '2_confirm.png', '3_confirm.png']:
            click_img(f'imgs\\{img}', confidence=0.7, action="Confirm Event")
        
    if not click_img(f'imgs\\0_close.png', action="Check 0 Close", confidence=0.9) or not click_img(f'imgs\\1_close.png', action="Check 1 Close", confidence=0.9): 
        if refine and get_refine() == 1:
            finalize_actions()                  
        
        if collect and get_collect() == 1:
            finalize_actions()   
        
        if get_action() == 1:
            finalize_actions()   
    time.sleep(0.1)
