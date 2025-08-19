import pybirdsreynolds.const as const
import tkinter as tk
import math

root = None
tip_window = None
canvas=None
point_ids = []

def draw_paused(pcanvas):
    pcanvas.delete("paused")
    if const.PAUSED:
        if const.BLINK_STATE:
            pcanvas.create_text(
                const.WIDTH_CONTROLS,
                max(const.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT),
                anchor="sw",
                fill="red",
                font=(const.FONT_TYPE, const.FONT_SIZE, "bold"),
                tags="paused",
                text=" PAUSED "
            )
        const.BLINK_STATE = not const.BLINK_STATE
        pcanvas.after(500, lambda: draw_paused(pcanvas))

def draw_fps(pcanvas, fps_value):
    pcanvas.delete("fps")
    if const.FPS:
        if not const.PAUSED:
            if fps_value == 0:
                value="..."
            else:    
                value = f"{fps_value:.1f}"
        else:
            value = "NA"
        pcanvas.create_text(
            const.WIDTH_CONTROLS,
            0,            
            anchor="nw",  
            fill="yellow",
            font=(const.FONT_TYPE, const.FONT_SIZE, "bold"),
            tags="fps",
            text=f" FPS : {value}"
    ) 

def draw_hidden(pcanvas):
    pcanvas.delete("hidden")
    if const.HIDDEN:
        pcanvas.create_text(
            const.WIDTH_CONTROLS+const.WIDTH,
            max(const.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT),
            anchor="se",
            fill="gray",
            font=(const.FONT_TYPE, const.FONT_SIZE), 
            tags="hidden",
            text="h to restore panels "
        )           

def draw_rectangle(pcanvas, proot):
    if not is_maximized(proot):
        global width_before_maximized
        global heigth_before_maximized  
        width_before_maximized=const.WIDTH 
        heigth_before_maximized=const.HEIGHT         
    pcanvas.delete("boundary")
    pcanvas.create_rectangle(
        const.WIDTH_CONTROLS, 0, const.WIDTH_CONTROLS + const.WIDTH, const.HEIGHT,
        outline=const.FILL_COLOR, width=const.MARGIN,
        tags="boundary"
    )        

def draw_canvas_hiden(proot):
    proot.geometry(f"{const.WIDTH+2}x{max(const.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
    proot.minsize(const.WIDTH+2, const.HEIGHT)
    proot.maxsize(const.WIDTH+2, const.HEIGHT)
    width_tmp=const.WIDTH
    height_tmp=const.HEIGHT        
    proot.update()
    proot.minsize(const.WIDTH_MIN, const.HEIGHT_MIN)
    proot.maxsize(10000, 10000)
    proot.update()
    const.WIDTH=width_tmp
    const.HEIGHT=height_tmp       
    return

def draw_canvas(pcanvas, proot):
    proot.geometry(f"{const.WIDTH_PARAMS+const.WIDTH+const.WIDTH_CONTROLS+2}x{max(const.HEIGHT, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
    pcanvas.config(width=const.WIDTH_PARAMS+const.WIDTH+const.WIDTH_CONTROLS+2, height=max(const.HEIGHT,const.HEIGHT_PARAMS_CONTROLS_DEFAULT), bg=const.CANVAS_BG)


def is_maximized(proot):
    if proot.tk.call('tk', 'windowingsystem') == 'aqua':
        return bool(proot.attributes("-fullscreen"))
    if proot.state() == "zoomed":
        return True
    try:
        if proot.attributes('-zoomed'):
            return True
    except tk.TclError:
        pass
    return (
        proot.winfo_width() >= proot.winfo_screenwidth() and
        proot.winfo_height() >= proot.winfo_screenheight()
    )

def draw_points(pcanvas, pbirds, pvelocities):
    global point_ids
    for pid in point_ids:
        pcanvas.delete(pid)
    point_ids.clear()

    triangle_size = 6*const.SIZE
    triangle_width = 4*const.SIZE
    for (x, y), (vx, vy) in zip(pbirds, pvelocities):
        if not const.TRIANGLES: 
            pid = pcanvas.create_oval(
                x - const.SIZE, y - const.SIZE,
                x + const.SIZE, y + const.SIZE,
                fill=const.FILL_COLOR, outline=const.OUTLINE_COLOR)
        else:
            angle = math.atan2(vy, vx)
            tip_x = x + math.cos(angle) * triangle_size
            tip_y = y + math.sin(angle) * triangle_size
            left_angle = angle + math.radians(150)
            right_angle = angle - math.radians(150)

            left_x = x + math.cos(left_angle) * triangle_width
            left_y = y + math.sin(left_angle) * triangle_width

            right_x = x + math.cos(right_angle) * triangle_width
            right_y = y + math.sin(right_angle) * triangle_width

            pid = pcanvas.create_polygon(
                tip_x, tip_y,
                left_x, left_y,
                right_x, right_y,
                fill=const.FILL_COLOR, outline=const.OUTLINE_COLOR
            )
        point_ids.append(pid) 

def maximize_minimize(proot, force):
    global width_before_maximized
    global heigth_before_maximized
    if is_maximized(proot):
        proot.state("normal")
        try:
            proot.attributes('-zoomed', False)
        except tk.TclError:
            pass
        if not force:
            const.WIDTH=width_before_maximized
            const.HEIGHT=heigth_before_maximized
    else:
        width_before_maximized=const.WIDTH 
        heigth_before_maximized=const.HEIGHT          

        wm = proot.tk.call('tk', 'windowingsystem')
        if wm == 'aqua':  # macOS
            proot.attributes("-fullscreen", True)
        elif wm == 'win32':  # Windows
            proot.state("zoomed")
        else:  # Linux
            try:
                proot.attributes('-zoomed', True)
            except tk.TclError:
                proot.attributes("-fullscreen", True)
    proot.focus_force()
    proot.focus_set() 

def show_tip(widget, text, event=None, dx=10, dy=10, wraplength=200):
    global tip_window

    # Si un tooltip est déjà affiché → le détruire
    if tip_window is not None:
        try:
            tip_window.destroy()
        except:
            pass
        tip_window = None

    if not text:
        return

    # Position du tooltip
    if event:  # cas des événements <Enter> sur un Canvas
        x = widget.winfo_rootx() + event.x + dx
        y = widget.winfo_rooty() + event.y + dy
    else:  # cas d’un widget normal
        x = widget.winfo_rootx() + dx
        y = widget.winfo_rooty() + widget.winfo_height() + dy

    tip_window = tw = tk.Toplevel(widget)
    tw.wm_overrideredirect(True)
    tw.wm_geometry(f"+{x}+{y}")
    label = tk.Label(
        tw,
        text=text,
        background="yellow",
        relief="solid",
        borderwidth=1,
        font=(const.FONT_TYPE, const.FONT_SIZE),
        wraplength=wraplength
    )
    label.pack(ipadx=4, ipady=2)

def hide_tip(event=None):
    global tip_window
    if tip_window:
        tip_window.destroy()
        tip_window = None

def add_canvas_tooltip(pcanvas, item, text):
    pcanvas.tag_bind(item, "<Enter>", lambda e: show_tip(pcanvas, text, e))
    pcanvas.tag_bind(item, "<Leave>", hide_tip)

def add_widget_tooltip(widget, text):
    widget.bind("<Enter>", lambda e: show_tip(widget, text))
    widget.bind("<Leave>", hide_tip)             