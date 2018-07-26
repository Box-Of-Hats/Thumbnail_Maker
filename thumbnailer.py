import json
import os
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw
import PIL.ImageTk
import sys
import time
from easygui import fileopenbox, ynbox, msgbox
from tkinter import * 
from tkinter.colorchooser import *
import tkinter.font

"""
TODO:
    -Add a font chooser
"""

class TextGraphic():
    def __init__(self, loc=None, text=None, size=None, font=None, f_colour=None, bg_colour=None):
        self.location = loc
        self.text = text
        self.font = font
        self.f_colour = f_colour
        self.bg_colour = bg_colour
        self.size = size
    
    def in_bounding_box(self, location, tolerance=0):
        #Check if a location is within the bounding box of the graphic
        right = self.midpoint[0] + self.width/2 + tolerance
        left = self.midpoint[0] - self.width/2 - tolerance
        top = self.midpoint[1] - self.height/2 - tolerance
        bottom = self.midpoint[1] + self.height/2 + tolerance

        return (left <= location[0]  and location[0] <= right and top <= location[1] and location[1] <= bottom)

    def get_midpoint(self):
        #Returns the midpoint location of the graphic
        return (self.location[0]+int(0.5*self.width), self.location[1]+int(0.5*self.height))

    def get_width(self):
        #Get width of the graphic in pixels
        font = PIL.ImageFont.truetype(self.font, self.size)
        text_lines = self.text.split("\n")
        longest_line = max(text_lines, key=lambda x: len(x)).strip()
        width = font.getsize(longest_line)[0]
        return width

    def get_height(self):
        #Get height of the graphic in pixels
        font = PIL.ImageFont.truetype(self.font, self.size)
        text_lines = self.text.split("\n")
        longest_line = max(text_lines, key=lambda x: len(x)).strip()
        height = font.getsize(longest_line)[1] * len(text_lines)
        return height
    
    width = property(get_width)
    height = property(get_height)
    midpoint = property(get_midpoint)


class Application():
    def __init__(self, config):
        self.config = config
        self.text_border = (255,255,255)
        self.text_fill = (1, 1, 1)
        self.text_size = 20
        self.text_location = (0,0)
        self.font_file = self.config["font_file"]
        self.input_folder = self.config["input_folder"]
        self.output_folder = self.config["output_folder"]
        self.font_folder = self.config["font_folder"]
        self.graphics = []
        self.selected_graphic = None
        self.midpoint = (320, 180)

        #Load the font list
        self.font_list = [i for i in os.listdir(self.font_folder) if i.endswith(".ttf")]

        #Make the GUI
        self.root = Tk()
        self.root.title("Thumbnail Maker V1.6")

        self.window = Frame(self.root)
        self.window.grid(padx=5, pady=5)

        self.left_side = Frame(self.window)
        self.left_side.grid(row=0, column=0, padx=5)
        self.right_side = Frame(self.window)
        self.right_side.grid(row=0, column=5, padx=5)

        #LEFT SIDE
        #Select Image
        self.but_select_image = Button(self.left_side, text="Select Image", command=self.select_image)
        self.but_select_image.grid(row=5, column=5, columnspan=20, pady=10, sticky="we")
        #Add new text
        self.but_select_image = Button(self.left_side, text="Add Text", command= lambda: self.add_new_text_element(self.midpoint))
        self.but_select_image.grid(row=7, column=5, columnspan=20, pady=10, sticky="we")
        #Change font
        self.font_var = StringVar(self.root)
        self.font_var.set(self.font_file.split("/")[-1])
        self.opt_font_selection = OptionMenu(self.left_side, self.font_var, *self.font_list)
        self.opt_font_selection.grid(row=9, column=5, columnspan=10, sticky="we")

        #Text input
        Label(self.left_side, text="Text:").grid(row=10, column=0)
        self.ent_text = Text(self.left_side, width=30, height=6)
        self.ent_text.grid(row=10, column=5, columnspan=5)
        scrollbar = Scrollbar(self.left_side, command=self.ent_text.yview)
        scrollbar.grid(row=10, column=11, sticky='nsew')
        self.ent_text['yscrollcommand'] = scrollbar.set

        #Text size slider
        self.lab_size = Label(self.left_side, text="Size: {}".format(self.text_size), width=10)
        self.lab_size.grid(row=15, column=0)
        self.sli_size = Scale(self.left_side, orient=HORIZONTAL, from_=10, to=160, resolution=2, showvalue=0)
        self.sli_size.grid(row=15, column=5, columnspan=5, sticky="we")
        self.sli_size.set(self.text_size)
        #Colour picker buttons
        Label(self.left_side, text="Colour:").grid(row=20, column=0)
        self.but_fill_colour = Button(self.left_side, text="Text", command=self.set_text_fill, width=10)
        self.but_fill_colour.grid(row=20, column=5)
        self.but_border_colour = Button(self.left_side, text="Dropshadow", command=self.set_text_border, width=10)
        self.but_border_colour.grid(row=20, column=6)
        #Save image button
        self.but_save_image = Button(self.left_side, text="Save", command= lambda: self.save_image())
        self.but_save_image.grid(row=25, column=5, columnspan=20, pady=10, sticky="we")

        #RIGHT SIDE
        photo = PIL.ImageTk.PhotoImage(file="./misc/default_image.jpg")
        self.image = PIL.Image.open("./misc/default_image.jpg").convert('RGB')
        self.lab_image_preview = Label(self.right_side, bg="#FFFFFF", image=photo)
        self.lab_image_preview.photo = photo
        self.lab_image_preview.grid(row=5,column=5)
        
        #Bindings
        def update_text_size():
            #Change the size of the selected graphic to that of the slider
            self.selected_graphic.size = self.sli_size.get()
            self.lab_size.config(text="Size: {}".format(self.selected_graphic.size))
            self.update_image_preview()
        
        def update_text_text():
            #Change the text of the selected graphic to that of the text entry
            self.selected_graphic.text = self.ent_text.get(0.0, END).strip()
            self.update_image_preview()

        def update_text_loc(mouse_event):
            #Change the location of the selected graphic to the mouse location
            font = PIL.ImageFont.truetype(self.selected_graphic.font, self.selected_graphic.size)

            #Calculate the size and midpoint of the text:
            text_lines = self.selected_graphic.text.split("\n")
            longest_line = max(text_lines, key=lambda x: len(x)).strip()
            width, height = font.getsize(longest_line)
            height = height * len(text_lines)
            #Move the graphic's centre to the mouse curser
            self.selected_graphic.location = (mouse_event.x-int(0.5*width), mouse_event.y-int(0.5*height))
            self.update_image_preview() #my_max(nested_list, key_func=lambda x: x[1])
        
        def create_text_if_empty():
            if len(self.graphics) == 0:
                self.add_new_text_element(self.midpoint)

        def font_option_changed(*args):
            #When the font option is changed:
            font_path = "{}{}".format(self.font_folder, self.font_var.get())
            if not self.selected_graphic:
                self.add_new_text_element(self.midpoint)
            self.selected_graphic.font = font_path
            self.update_image_preview()

        self.ent_text.bind("<KeyRelease>", lambda ignore: update_text_text())
        self.sli_size.bind("<ButtonRelease-1>", lambda ignore: update_text_size())
        self.lab_image_preview.bind("<ButtonPress-1>", lambda loc: self.select_graphic(self.get_closest_graphic(loc, tolerance=50)))
        self.ent_text.bind("<ButtonPress-1>", lambda ignore: create_text_if_empty())
        self.lab_image_preview.bind("<B1-Motion>", lambda loc: update_text_loc(loc))
        self.font_var.trace('w', font_option_changed)

        self.root.protocol('WM_DELETE_WINDOW', self.close_program)

        self.root.mainloop()

    def select_graphic(self, graphic):
        if not graphic:
            graphic = self.add_new_text_element(self.midpoint)
        self.selected_graphic = graphic
        self.ent_text.delete(0.0, END)
        self.ent_text.insert(END, self.selected_graphic.text)
        self.sli_size.set(self.selected_graphic.size)
        self.lab_size.config(text="Size: {}".format(self.selected_graphic.size))
        self.but_border_colour.config(fg="#{0:02x}{1:02x}{2:02x}".format(*self.selected_graphic.bg_colour))
        self.but_fill_colour.config(fg="#{0:02x}{1:02x}{2:02x}".format(*self.selected_graphic.f_colour))
        self.font_var.set(self.selected_graphic.font.split("/")[-1])

    def get_closest_graphic(self, mouse_event, tolerance=0):
        #Return the graphic which is the closest to the mouse event
        click_loc = mouse_event.x, mouse_event.y
        if len(self.graphics) == 0:
            return False
        else:
            distances = {g:None for g in self.graphics}
            for graphic in self.graphics:
                graphic_midpoint = graphic.midpoint
                distance = abs(click_loc[0] - graphic_midpoint[0]) + abs(click_loc[1] - graphic_midpoint[1])
                distances[graphic] = distance

            min_dist = min([distances[g] for g in distances])
            for graphic in distances:
                if (distances[graphic] == min_dist and graphic.in_bounding_box(click_loc, tolerance=tolerance)):
                    return graphic
            else:
                return False

    def add_new_text_element(self, location=(0,0)):
        new_text_element = TextGraphic(loc=location, text="Text {}".format(len(self.graphics)), size=20, font=self.font_file, f_colour=(255,255,255), bg_colour=(0,0,0))
        self.graphics.append(new_text_element)
        self.select_graphic(self.graphics[-1])
        self.update_image_preview()
        return new_text_element


    def close_program(self):
        self.root.destroy()
        quit()

    def set_text_fill(self):
        c = askcolor(color="red", parent=None, title=("Set text fill"))
        if c:
            rgb_colour = tuple([int(i) for i in c[0]])
            self.selected_graphic.f_colour = rgb_colour
            self.but_fill_colour.config(fg=c[1])
            self.update_image_preview()
        else:
            pass
        
    def set_text_border(self):
        c = askcolor(color="red", parent=None, title=("Set text border"))
        if c:
            rgb_colour = tuple([int(i) for i in c[0]])
            self.selected_graphic.bg_colour = rgb_colour
            self.but_border_colour.config(fg=c[1])
            self.update_image_preview()
        else:
            pass

    def select_image(self):
        #Attempt to load image from passed in args, else prompt the user with a gui
        in_filename = fileopenbox("Choose an image", "Thumbnail Maker", self.input_folder)
        if not in_filename:
            return None
        #Image was selected:
        self.image = PIL.Image.open(in_filename).convert('RGB')
        self.update_image_preview()

    def update_image_preview(self):
        #Takes a standard PIL.Image and displays it in the image preview
        image = self.render_image(size=(640, 360))

        #Add image to the label
        image = PIL.ImageTk.PhotoImage(image)
        self.lab_image_preview.photo = image
        self.lab_image_preview.configure(image=image)

        self.lab_image_preview.update()

    def save_image(self):
        """
        Export the current image in 1280x720
        """
        image = self.render_image((1280, 720))

        out_filename = "{}.jpg".format(int(round(time.time() * 1000)))
        print("Saving to: '{}'".format(out_filename))
        image.save("{}/{}".format(self.output_folder, out_filename))
        msgbox("Your photo has been made into a thumbnail! You can find it at {}".format(self.output_folder))

    def render_image(self, size=(1280, 720)):
        #returns an Image object that has been rendered with the current settings
        image = self.image.resize(size, PIL.Image.ANTIALIAS)
        """
        Loop through graphics and draw them to the image
        Janky multiplication/division on location to ensure that the text
        is in the correct location for both 1280x720 and 640x360 images.
        Other resolutions may not work!
        """
        draw = PIL.ImageDraw.Draw(image)
        for graphic in self.graphics:
            font = PIL.ImageFont.truetype(graphic.font, int(graphic.size/360*size[1]))
            draw.text((graphic.location[0]*size[0]/640+2, graphic.location[1]/360*size[1]+2), graphic.text, graphic.bg_colour, font) #This is drop shadow
            draw.text((graphic.location[0]*size[0]/640, graphic.location[1]*size[1]/360), graphic.text, graphic.f_colour, font)
        return image

def main():
    #Load config file
    try:
        with open("config.txt", "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: 'config.txt' file could not be found.")
        print("Please include this file in the same directory as thumbnailer.py.")
        print("""E.g:
        parent/
                thumbnailer/
                            thumbnailer.py
                            config.txt
        """)
        input("Press Return to exit...")
        quit()

    Application(config)

if __name__ == "__main__":
    main()
