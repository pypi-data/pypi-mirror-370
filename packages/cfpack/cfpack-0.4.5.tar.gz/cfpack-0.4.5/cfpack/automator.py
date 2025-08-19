#!/usr/bin/env python
# -*- coding: utf-8 -*-
# written by Christoph Federrath, 2023

import numpy as np
import time
import tempfile
from cfpack import print, stop

# first install pyautogui and opencv-python
import pyautogui as pag
import PIL

# class that uses pyautogui to automate mouse and keyboard interactions with the screen
class automator:

    # init
    def __init__(self, time_between_actions=0.05, verbose=1):
        pag.FAILSAFE = True # move to any screen corner to end automation
        pag.PAUSE = time_between_actions # wait time between pyautogui calls (in seconds)
        self.verbose = verbose # more verbose output (default is 1)
        self.screen_resolution = np.array(pag.size()) # screen width and height
        if verbose: print("Screen resolution =", self.screen_resolution)
        with tempfile.NamedTemporaryFile() as tmpf:
            tmp_file = tmpf.name+".png" # mame of temporary file
            test_screenshot = pag.screenshot() # take screenshot
            test_screenshot.save(tmp_file) # save screenshot
            tmp_img = PIL.Image.open(tmp_file) # open screenshot
            self.screenshot_resolution = np.array(tmp_img.size) # determine resolution of screenshot
            if verbose: print("Screenshot resolution = ", self.screenshot_resolution)
        # compute screenshot-to-screen resolution factor
        self.resolution_factor = self.screenshot_resolution / self.screen_resolution
        if verbose > 1: print("Current position of mouse =", pag.position()) # current position of the mouse

    # return the pyautogui object
    def get_pyautogui(self):
        return pag

    # write str on keyboard
    def keyboard_input(self, str):
        pag.typewrite(str)

    # open Apple spotlight
    def open_spotlight(self):
        pag.keyDown('command')
        pag.press('space')
        time.sleep(0.1)
        pag.keyUp('command')

    # function to get mouse position based on matching an input image
    def get_mouse_position(self, image_file, grayscale=True, confidence=0.8, ntries=10, delay_between_tries=0.5):
        if self.verbose > 1: print("Looking for ", image_file)
        position = None # initialisation
        # try a few times with short delays in between
        for itry in range(ntries):
            # loop over temporary rescaled and resized image files to allow for slight variations in screen resolution
            with tempfile.NamedTemporaryFile() as tmpf:
                tmp_file = tmpf.name+".png" # name of temporary file
                if self.verbose > 1: print("name of temporary image file: ", tmp_file)
                scale = self.resolution_factor / 2.0 # image scale factor
                if self.verbose > 1: print("scale = ", scale)
                delta_pixels = (np.array([[-i,i] for i in range(2)]).flatten())[1:] # try 0, -/+1 in pixel size
                for delta_pixel_y in delta_pixels: # try slight variation of image size in y
                    if position is not None: break # condition when image was found
                    for delta_pixel_x in delta_pixels: # try slight variation of image size in x
                        if position is not None: break # condition when image was found
                        delta_pixel = [delta_pixel_x, delta_pixel_y]
                        if self.verbose > 1: print("delta_pixel = ", delta_pixel)
                        self.resize_image(image_file, out_image_file=tmp_file, scale=scale, delta_pixel=delta_pixel) # resize image
                        try:
                            position = pag.locateCenterOnScreen(tmp_file, confidence=confidence, grayscale=grayscale) # find location on screen
                        except pag.ImageNotFoundException:
                            position = None
            if position is not None: break # condition when image was found
            time.sleep(delay_between_tries)
        if position is None:
            if self.verbose: print(f'{image_file} not found on screen...')
            return None
        else:
            ret_position = np.array(position) / self.resolution_factor # division by 2 can happen on retina displays
            if self.verbose > 1: print("Found position of ", image_file, " at ", ret_position)
            return ret_position

    # read image from file, resize by scale (can be 2D array or scalar),
    # add delta_pixel (can be 2D array or scalar) to scaled image, and write final image to out_image_file
    def resize_image(self, in_image_file, scale=1.0, delta_pixel=0, out_image_file=None):
        def check_and_convert_input(input):
            if not isinstance(input, list) and not isinstance(input, tuple) and not isinstance(input, np.ndarray):
                output = np.array([input, input])
            else:
                if len(np.array(input)) != 2: print("input must be 2-dimensional.", error=True)
                output = np.array(input)
            return output
        img = PIL.Image.open(in_image_file)
        # check args type
        scale_xy = check_and_convert_input(scale)
        delta_pixel_xy = check_and_convert_input(delta_pixel)
        new_size = np.array([img.size[0]*scale_xy[0], img.size[1]*scale_xy[1]]).astype('int') + delta_pixel_xy
        if self.verbose > 1: print("new image size = ", new_size)
        img = img.resize(tuple(new_size), PIL.Image.Resampling.LANCZOS)
        if out_image_file is None:
            out_image_file = "".join(in_image_file.split('.')[:-1])+"_resized."+in_image_file.split('.')[-1]
        img.save(out_image_file)
        if self.verbose > 1: print(out_image_file+" written.", color='magenta')

    # drag/move mouse to position of image (optional: click; pixel offset from centre of image)
    def move_mouse(self, image_file, offset=[0,0]):
        pos = self.get_mouse_position(image_file) # get position of image
        if pos is not None:
            pag.moveTo(pos[0]+offset[0], pos[1]+offset[1]) # move to position
            return pos
        else:
            return None

    # do a mouse click on image
    def click(self, image_file, nclicks=1, offset=[0,0]):
        pos = self.move_mouse(image_file, offset=offset)
        if pos is not None:
            if nclicks == 1: pag.click()
            if nclicks == 2: pag.doubleClick()
            if nclicks == 3: pag.tripleClick()
            return pos
        else:
            return None

# ===== the following applies in case we are running this in script mode =====
if __name__ == "__main__":
    ag = automator(verbose=2)
