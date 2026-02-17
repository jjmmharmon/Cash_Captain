import tkinter as tk
from PIL import Image, ImageTk
from db_manager import DatabaseManager
from interface import FinanceManagerUI
import time


def show_splash():
    """Display splash screen before loading the main application."""
    splash = tk.Toplevel()
    splash.overrideredirect(True)    


    # Load splash image
    try:
        img = Image.open("pennypal_logo.png")  
        img = img.resize((300, 300))
        splash_img = ImageTk.PhotoImage(img)
    except:
        splash_img = None


    # Center window
   
    screen_w = splash.winfo_screenwidth()
    screen_h = splash.winfo_screenheight()
    width = 350
    height = 350
    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)
    splash.geometry(f"{width}x{height}+{x}+{y}")


    # Display logo


    if splash_img:
        tk.Label(splash, image=splash_img).pack(expand=True)
        splash.image = splash_img
    else:
        tk.Label(splash, text="PennyPal", font=("Arial", 24)).pack(expand=True)


    splash.after(2500, splash.destroy)  


    return splash




def main():
    root = tk.Tk()
    root.withdraw()  


    # Show splash screen


    splash = show_splash()


    # Wait until splash closes


    root.after(2600, lambda: (
        root.deiconify(),   # Show main window
        start_app(root)
    ))


    root.mainloop()




def start_app(root):
    """Start PennyPal after splash screen finishes."""
    db = DatabaseManager("finance.db")
    FinanceManagerUI(root, db)




if __name__ == "__main__":
    main()


