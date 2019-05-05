# -*- coding: utf-8 -*-
import tkinter as tk
from PIL import ImageTk, Image


class Application(tk.Frame):
    def __init__(self, master=None, imagen=None, text_ocr=None):
        super().__init__(master)

        if not imagen or not text_ocr:
            raise ValueError('No se ha especificado una imagen o texto extraido mediante OCR.')
        
        self.imagen = imagen
        self.text_ocr = text_ocr

        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.image_panel = tk.Label(self, text='Codigo de Seguridad extraido mediante OCR:')
        self.image_panel.pack(side="top") #, fill="both", expand="yes")

        self.img = ImageTk.PhotoImage(Image.open(self.imagen))
        self.image_panel = tk.Label(self, image=self.img)
        self.image_panel.pack(side="top")#, fill="both", expand="yes")
    
        self.text = tk.Text(self, width=10, height=1, pady=5)
        self.text.pack(side="top")
        self.text.insert(tk.INSERT, self.text_ocr)

        self.hi_there = tk.Button(self, text="OK", command=self.say_hi)
        self.hi_there.pack(side="bottom")

    def say_hi(self):
        self.text_ocr = self.text.get('1.0', '1.8')
        self.master.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = Application(master=root,imagen='pdf/images/page0-7.png', text_ocr='IOguhsm3')
    app.mainloop()
    print(app.text_ocr)
