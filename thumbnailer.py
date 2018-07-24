import json
import PIL.Image
import PIL.ImageFont
import PIL.ImageDraw
import PIL.ImageTk
import sys
import time
from easygui import fileopenbox, ynbox, msgbox
from tkinter import * 
from tkinter.colorchooser import *

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

        #Make the GUI
        self.root = Tk()

        self.window = Frame(self.root)
        self.window.grid(padx=5, pady=5)

        self.left_side = Frame(self.window)
        self.left_side.grid(row=0, column=0, padx=5)
        self.right_side = Frame(self.window)
        self.right_side.grid(row=0, column=5, padx=5)

        #LEFT SIDE
        self.but_select_image = Button(self.left_side, text="Select Image", command=self.select_image, width=20)
        self.but_select_image.grid(row=5, column=0, columnspan=10)
        #Text input
        Label(self.left_side, text="Text:").grid(row=10, column=0)
        self.ent_text = Text(self.left_side, width=30, height=6)
        self.ent_text.grid(row=10, column=5, columnspan=5)

        scrollb = Scrollbar(self.left_side, command=self.ent_text.yview)
        scrollb.grid(row=10, column=11, sticky='nsew')
        self.ent_text['yscrollcommand'] = scrollb.set

        #Text size slider
        Label(self.left_side, text="Size:").grid(row=15, column=0)
        self.sli_size = Scale(self.left_side, orient=HORIZONTAL, from_=10, to=100, resolution=2)
        self.sli_size.grid(row=15, column=5, columnspan=5)
        self.sli_size.set(self.text_size)
        #Colour picker buttons
        Label(self.left_side, text="Colour:").grid(row=20, column=0)
        self.but_fill_colour = Button(self.left_side, text="Text", command=self.set_text_fill)
        self.but_fill_colour.grid(row=20, column=5)
        self.but_border_colour = Button(self.left_side, text="Dropshadow", command=self.set_text_border)
        self.but_border_colour.grid(row=20, column=6)
        #Save image button
        self.but_save_image = Button(self.left_side, text="Save", command= lambda: self.save_image())
        self.but_save_image.grid(row=25, column=0, columnspan=10, pady=10, ipadx=5, ipady=5)

        #RIGHT SIDE
        photo = PIL.ImageTk.PhotoImage(file="./misc/default_image.jpg")
        self.lab_image_preview = Label(self.right_side, bg="#FFFFFF", image=photo)
        self.lab_image_preview.photo = photo
        self.lab_image_preview.grid(row=5,column=5)
        
        #Bindings
        def update_text_size():
            self.text_size = self.sli_size.get()
            print("size: {}".format(self.text_size))
            self.update_image_preview()
        
        def update_text_loc(loc):
            self.text_location = (loc.x, loc.y)
            self.update_image_preview()

        self.ent_text.bind("<KeyRelease>", lambda ignore: self.update_image_preview())
        self.sli_size.bind("<ButtonRelease-1>", lambda ignore: update_text_size())
        self.lab_image_preview.bind("<ButtonRelease-1>", lambda loc: update_text_loc(loc))

        self.root.protocol('WM_DELETE_WINDOW', self.close_program)  # self.root is your self.root window

        self.root.mainloop()

    def close_program(self):
            # check if saving
            # if not:
            self.root.destroy()
            quit()

    def set_text_fill(self):
        c = askcolor(color="red", parent=None, title=("Set text fill"))
        rgb_colour = tuple([int(i) for i in c[0]])
        if c:
            self.text_fill = rgb_colour
            self.but_fill_colour.config(fg=c[1])
            self.update_image_preview()
        else:
            pass
        
    def set_text_border(self):
        c = askcolor(color="red", parent=None, title=("Set text border"))
        rgb_colour = tuple([int(i) for i in c[0]])
        if c:
            self.text_border = rgb_colour
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
        self.image = self.image = PIL.Image.open(in_filename).convert('RGB')
        self.set_image_preview(self.image)


    def update_image_preview(self):
        """Update the preview image so it's in-sync with the current options"""
        self.set_image_preview(self.image)

    def set_image_preview(self, image):
        #Takes a standard PIL.Image and displays it in the image preview
        image = image.resize((640,360), PIL.Image.ANTIALIAS)
        #Add text
        text = str(self.ent_text.get(0.0, END))

        font = PIL.ImageFont.truetype(self.font_file, self.text_size)
        draw = PIL.ImageDraw.Draw(image)
        draw.text((self.text_location[0]+2, self.text_location[1]+2), text, self.text_border, font) #This is drop shadow
        draw.text(self.text_location, text, self.text_fill, font)
        #Add to the label
        image = PIL.ImageTk.PhotoImage(image)
        self.lab_image_preview.photo = image
        self.lab_image_preview.configure(image=image)

        self.lab_image_preview.update()

    def save_image(self):
        """
        Export the current image in 1280x720
        """
        image = self.image.resize((1280,720), PIL.Image.ANTIALIAS)
        #Add text
        text = str(self.ent_text.get(0.0, END))

        font = PIL.ImageFont.truetype(self.font_file, self.text_size*2)
        draw = PIL.ImageDraw.Draw(image)
        draw.text((self.text_location[0]*2+2, self.text_location[1]*2+2), text, self.text_border, font) #This is drop shadow
        draw.text((self.text_location[0]*2,self.text_location[1]*2), text, self.text_fill, font)
        
        out_filename = "{}.jpg".format(int(round(time.time() * 1000)))
        print("Saving to: '{}'".format(out_filename))
        image.save("{}/{}".format(self.output_folder, out_filename))
        msgbox("Your photo has been made into a thumbnail! You can find it at {}".format(self.output_folder))

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
