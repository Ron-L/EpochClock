import cv2      # pip install opencv-python
import datetime
import pyperclip
import roman    # pip install roman
import tkinter as tk
import tkinter.font
import tkinter.messagebox

# "constants"
# for colors see https://cs111.wellesley.edu/archive/cs111_fall14/public_html/labs/lab12/tkintercolor.html
BEVEL_COLOR = 'gray21'          # dark gray
CONTROL_COLOR = 'gray75'        # light gray
DISPLAY_COLOR='#000000'         # black
FONT = '14-segmented display'   # https://fontstruct.com/fontstructions/show/2341582/14-segmented-display
SCALE = .5                      # needs to be 1/INTEGER (e.g. not .38)
DEFAULT_BASE = 10
WIDTH = 750
HEIGHT = 275

# globals
base = DEFAULT_BASE
canvas = None
fourteenSegSmallFont = None
fourteenSegLargeFont = None
root = None
invScale = int(1/SCALE)

def main():
    global canvas
    global fourteenSegSmallFont
    global fourteenSegLargeFont
    global root

    # create window
    root = tk.Tk()
    root.resizable(False, False)
    root.geometry(f'{0+(WIDTH-25)//invScale}x{25+25//invScale+(HEIGHT-50)//invScale}')
    root.configure(bg=CONTROL_COLOR)
    root.title('Epoch Clock')
    root.eval('tk::PlaceWindow . center') # Placing the window in the center of the screen

    # check for proper font
    if '14-segmented display' not in tk.font.families():
        # copy the link to the missing font to the clipboard
        pyperclip.copy('https://fontstruct.com/fontstructions/show/2341582/14-segmented-display')
        spam = pyperclip.paste()

        # display notice in message box
        tk.messagebox.showinfo("Epoch Clock Font Notice", """You'll need to install "14-segmented display" to get the proper effect.\n"""
        "https://fontstruct.com/fontstructions/show/2341582/14-segmented-display\n"
        "(The URL has been copied to the clipboard)")

    # create a canvas to be the clock bevel and hold the clock display
    canvas = tk.Canvas(root, bg=BEVEL_COLOR, highlightthickness=0)

    # Button Area
    frame1 = tk.Frame(root, bg=CONTROL_COLOR)
    if 0:
        frame1.pack(pady=15)

        button1 = tk.Button(frame1, text='Roman Numeral', borderwidth=10, padx=5, bg=CONTROL_COLOR, command=lambda : buttonClick(0))
        button1.pack(side='left', padx=5)
        button2 = tk.Button(frame1, text='Hexadecimal', borderwidth=10, padx=5, bg=CONTROL_COLOR, command=lambda : buttonClick(16))
        button2.pack(side='left', padx=5)
        button3 = tk.Button(frame1, text='Decimal', borderwidth=10, padx=5, bg=CONTROL_COLOR, command=lambda : buttonClick(10))
        button3.pack(side='left', padx=5)
        button3 = tk.Button(frame1, text='Octal', borderwidth=10,padx=5, bg=CONTROL_COLOR, command=lambda : buttonClick(8))
        button3.pack(side='left', padx=5)
        button4 = tk.Button(frame1, text='Binary', borderwidth=10,padx=5, bg=CONTROL_COLOR, command=lambda : buttonClick(2))
        button4.pack(side='left', padx=5)
    else:
        frame1.pack(fill=tkinter.BOTH)

        statusOptions = [
            ("Roman Numeral", 0),
            ("Hexadecimal", 16),
            ("Decimal", 10),
            ("Octal", 8),
            ("Binary", 2),
        ]
        x = tkinter.IntVar()  # this var is still needed so correct button is selected
        for text, val in statusOptions:
            rb = tkinter.Radiobutton(frame1, text=text, bg=CONTROL_COLOR, variable=x, value=val, padx=5, command=lambda val=val : buttonClick(val)).pack(side=tkinter.LEFT)
        x.set(base)

    # create fonts
    fourteenSegSmallFont = tk.font.Font(family=FONT, size=-30//invScale)  # negative size is pixels rather than points
    fourteenSegLargeFont = tk.font.Font(family=FONT, size=-50//invScale)  # negative size is pixels rather than points

    # display
    updateClockDisplay(reschedule=True)

    # always on top
    root.attributes('-topmost', True)
    #root.update()

    # Main
    root.mainloop()


def updateClockDisplay(reschedule=True):
    canvas.delete('all')

    # add a rectangle to the canvas to be the clock bevel and hold the clock display
    canvas.pack(fill=tk.constants.BOTH, expand=1)
    round_rectangle(25//invScale, 25//invScale, 0+((WIDTH-50)//invScale), 0+((HEIGHT-50)//invScale), radius=40, color=DISPLAY_COLOR)

    # AM/PM
    displayText(canvas,  60//invScale,  50//invScale, 'PM' if datetime.datetime.now().hour >= 12 else 'AM')

    # mm-dd-yyyy
    displayText(canvas, 390/invScale,  50/invScale, datetime.datetime.now().strftime('%m-%d-%Y'))

    # H:M
    # get one consistant now to use to avoid race conditions
    now = datetime.datetime.now()

    # special rule for hour due to AM/PM. Modulo doesn't work because 12:00 becomes 00:00
    if now.hour > 12:
        modifiedHour = now.hour - 12
    else:
        modifiedHour = now.hour

    match base:
        case 0:  # Roman Numerals
            h = roman.toRoman(modifiedHour)
            m = roman.toRoman(now.minute)
        case 16:
            h = f'{modifiedHour:02X}'
            m = f'{now.minute:02X}'
        case 10:
            h = f'{modifiedHour:02}'
            m = f'{now.minute:02}'
            displayText(canvas,  (65+4*50)//invScale, 120//invScale, f'{h}:{m}', 'large')
        case 8:
            h = f'{modifiedHour:02o}'
            m = f'{now.minute:02o}'
        case 2:
            h = f'{modifiedHour:02b}'
            m = f'{now.minute:02b}'
    if h == '00':
        h = '12'
    digOffset = 6-len(h)
    displayText(canvas,  (65+digOffset*50)//invScale, 120//invScale, f'{h}:{m}', 'large')

    # epoch
    displayText(canvas,  60//invScale, 185//invScale, str(int(now.timestamp())))

    # schedule another run on the next 1 second rollover
    if reschedule:
        delay = 1000 - int(now.microsecond /1000)
        root.after(delay, updateClockDisplay)


def displayText(canvas, x, y, text, fontSize='small'):
    if fontSize == 'small':
        font = fourteenSegSmallFont
        spacing = 30//invScale
    else:
        font = fourteenSegLargeFont
        spacing = 50//invScale
    for i, l in enumerate(text):
        if l == '0':
            l = 'O'
        elif l == '1':
            l = 'l'
        canvas.create_text(x+i*spacing, y, fill='chartreuse2', font=font, text=l) # RCL


def round_rectangle(x1, y1, x2, y2, radius=25, color='#000000', **kwargs): # Creating a rounded rectangle

        points = [x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1]

        return canvas.create_polygon(points, **kwargs, smooth=True, fill=color)

def buttonClick(num):
    global base

    base = num
    updateClockDisplay(reschedule=False)


if __name__ == '__main__':
    main()
