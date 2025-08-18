import tkinter as tk
import random
import math
from pybirdsreynolds.args import compute_args, display_range, get_description, get_epilog, get_help_text
import signal
import sys
import copy
from importlib.metadata import version
import time
from tkinter import font
from pybirdsreynolds.const import *
import types

# variables
version_prog = version("pybirdsreynolds")
options = compute_args()

for var_name, default_value in list(globals().items()):
    if var_name.endswith("_DEFAULT"):
        option_name = var_name[:-8]
        value = getattr(options, option_name.lower(), default_value)
        globals()[option_name] = value
        globals()[option_name+"_BUTTON_UP"] = None
        globals()[option_name+"_BUTTON_DOWN"] = None
    if var_name.endswith("_TEXT"):
        option_name = var_name[:-5]
        value = getattr(options, option_name.lower(), default_value)
        globals()[option_name] = value
        globals()[option_name+"_BUTTON"] = None

tip_window = None
hidden=False
root=None
canvas=None
trans_hiden=False
last_time = time.time()
paused = True
blink_state = True
frame_count = 0
fps_value = 0
fonts=[]
fps= False
count= not paused
resizing = False
margin=1
selected_index=0
shift_pressed = False
width_before_maximized=WIDTH
heigth_before_maximized=HEIGHT
if not COLOR:
    canvas_bg = "black"
    fill_color = "white"
    outline_color = "black"
else:
    canvas_bg = "#87CEEB"
    fill_color = "black"
    outline_color = "white" 

start_button = None
refresh_button = None
generation_button = None

# deep copy
max_speed_init = copy.deepcopy(MAX_SPEED)
neighbor_radius_init = copy.deepcopy(NEIGHBOR_RADIUS)
num_birds_init = copy.deepcopy(NUM_BIRDS)
width_init = copy.deepcopy(WIDTH)
height_init = copy.deepcopy(HEIGHT)
refresh_ms_init = copy.deepcopy(REFRESH_MS)
random_speed_init = copy.deepcopy(RANDOM_SPEED)
random_angle_init = copy.deepcopy(RANDOM_ANGLE)
sep_weight_init = copy.deepcopy(SEP_WEIGHT)
align_weight_init = copy.deepcopy(ALIGN_WEIGHT)
coh_weight_init = copy.deepcopy(COH_WEIGHT)
size_init = copy.deepcopy(SIZE)
font_size_init = copy.deepcopy(FONT_SIZE)
font_type_init = copy.deepcopy(FONT_TYPE)
triangles_init = copy.deepcopy(TRIANGLES)
free_init = copy.deepcopy(FREE)
color_init= copy.deepcopy(COLOR)
repeating = {"active": False, "job": None}


# doc dict
param_docs = {
    name.removesuffix("_DOC"): value
    for name, value in globals().items()
    if name.endswith("_DOC")
    and globals().get(f"{name[:-4]}_HIDEN") == 0
}
param_order = list(param_docs.keys())

def app():

    def restore_options():

        global MAX_SPEED, NEIGHBOR_RADIUS, NUM_BIRDS, WIDTH, HEIGHT
        global REFRESH_MS, RANDOM_SPEED, RANDOM_ANGLE
        global SEP_WEIGHT, ALIGN_WEIGHT, COH_WEIGHT
        global paused, SIZE, TRIANGLES, COLOR, canvas_bg, FONT_SIZE, FONT_TYPE, fonts
        global fill_color, outline_color, fps, FREE
 
        MAX_SPEED = copy.deepcopy(max_speed_init)
        NEIGHBOR_RADIUS = copy.deepcopy(neighbor_radius_init)
        NUM_BIRDS = copy.deepcopy(num_birds_init)
        WIDTH = copy.deepcopy(width_init)
        HEIGHT = copy.deepcopy(height_init)
        REFRESH_MS = copy.deepcopy(refresh_ms_init)
        RANDOM_SPEED = copy.deepcopy(random_speed_init)
        RANDOM_ANGLE = copy.deepcopy(random_angle_init)
        SEP_WEIGHT = copy.deepcopy(sep_weight_init)
        ALIGN_WEIGHT = copy.deepcopy(align_weight_init)
        COH_WEIGHT = copy.deepcopy(coh_weight_init)
        SIZE = copy.deepcopy(size_init)
        COLOR = copy.deepcopy(color_init)
        FREE = copy.deepcopy(free_init)
        TRIANGLES = copy.deepcopy(triangles_init)
        FONT_TYPE = copy.deepcopy(FONT_TYPE)   

        if not COLOR:
            canvas_bg = "black"
            fill_color = "white"
            outline_color = "black"
        else:
            canvas_bg = "#87CEEB"
            fill_color = "black"
            outline_color = "white" 

    def start_repeat(ligne, direction):
        def repeat():
            on_click(ligne, direction)
            if repeating["active"]:
                repeating["job"] = canvas.after(100, repeat)
        repeating["active"] = True
        repeat()

    def stop_repeat():
        repeating["active"] = False
        if repeating["job"]:
            canvas.after_cancel(repeating["job"])
            repeating["job"] = None

    def on_shift_press(event):
        global shift_pressed
        shift_pressed = True

    def on_shift_release(event):
        global shift_pressed
        shift_pressed = False

    def draw():
        draw_status(False, False)
        draw_points()
        draw_rectangle()
        draw_fps()
        draw_hidden()

    def draw_fps():
        global FONT_TYPE
        canvas.delete("fps")
        if fps:
            if not paused:
                if fps_value == 0:
                    value="..."
                else:    
                    value = f"{fps_value:.1f}"
            else:
                value = "NA"
            canvas.create_text(
                WIDTH_CONTROLS,
                0,            
                anchor="nw",  
                fill="yellow",
                font=(FONT_TYPE, FONT_SIZE, "bold"),
                tags="fps",
                text=f" FPS : {value}"
        )

    def draw_paused():
        global FONT_TYPE
        global blink_state
        canvas.delete("paused")
        if paused:
            if blink_state:
                canvas.create_text(
                    WIDTH_CONTROLS,
                    max(HEIGHT, HEIGHT_PARAMS_CONTROLS_DEFAULT),
                    anchor="sw",
                    fill="red",
                    font=(FONT_TYPE, FONT_SIZE, "bold"),
                    tags="paused",
                    text=" PAUSED "
                )
            blink_state = not blink_state
            canvas.after(500, draw_paused)

    def draw_hidden():
        global FONT_TYPE
        global hidden
        canvas.delete("hidden")
        if hidden:
            canvas.create_text(
                WIDTH_CONTROLS+WIDTH,
                max(HEIGHT, HEIGHT_PARAMS_CONTROLS_DEFAULT),
                anchor="se",
                fill="gray",
                font=(FONT_TYPE, FONT_SIZE), 
                tags="hidden",
                text="h to restore panels "
            )

    def toggle_pause(event=None):
        global paused
        global blink_state
        blink_state = True
        paused = not paused
        draw_status(False, False)
        draw_paused()

    def change_value(type, val, FREE):
        value = globals().get(type)
        prefix = type.upper()
        default = globals().get(f"{prefix}_DEFAULT")
        min_value = globals().get(f"{prefix}_MIN")
        max_value = globals().get(f"{prefix}_MAX")
        min_free_value = globals().get(f"{prefix}_FREE_MIN")
        max_free_value = globals().get(f"{prefix}_FREE_MAX")                    
        value += val
        if not FREE:
            if max_value is not None:
                value = min(value, max_value)
            if min_value is not None:
                value = max(value, min_value)
        else:
            if max_free_value is not None:
                value = min(value, max_free_value)
            if min_free_value is not None:
                value = max(value, min_free_value)
        return value

    def on_other_key(event):
        global selected_index, NUM_BIRDS, MAX_SPEED
        global NEIGHBOR_RADIUS, SEP_WEIGHT, ALIGN_WEIGHT
        global COH_WEIGHT, SIZE, RANDOM_SPEED, RANDOM_ANGLE
        global TRIANGLES, FREE , REFRESH_MS, WIDTH, HEIGHT, fonts
        global COLOR, canvas_bg, fill_color, outline_color, fps, FONT_TYPE
        global shift_pressed
        shift = getattr(event, "state", None)        
        if shift is not None:
            shift = (shift & 0x1) != 0
        else:
            shift = shift_pressed
        if SHIFT_HIDEN==0:
            shift =False    
        mult = 10 if shift else 1
        val = mult if event.keysym == "Right" else 1*-mult
        param = param_order[selected_index]
        if (param == "WIDTH" or param == "HEIGHT") and is_maximized():
            val=0
        if event.keysym == "Up" and ARROWS_HIDE<2:
            selected_index = (selected_index - 1) % len(param_order)
        elif event.keysym == "Down" and ARROWS_HIDE<2:
            selected_index = (selected_index + 1) % len(param_order)
        elif (event.keysym == "Right"  or event.keysym == "Left") and ARROWS_HIDE<=1:
            if param == "TRIANGLES":
                TRIANGLES = not TRIANGLES
                draw()
            elif param == "FONT_TYPE":
                current_index = fonts.index(FONT_TYPE)
                FONT_TYPE = fonts[(current_index + val) % len(fonts)]
                draw()
                draw_status(True, True)               
            elif param == "COLOR":
                COLOR = not COLOR 
                if not COLOR:
                    canvas_bg = "black"
                    fill_color = "white"
                    outline_color = "black"
                else:
                    canvas_bg = "#87CEEB"
                    fill_color = "black"
                    outline_color = "white" 
                draw_canvas()
                draw()
            elif param == "FREE":
                FREE = not FREE
                for paramm in param_order:
                    if paramm not in ["FREE", "COLOR" , "TRIANGLES", "FONT_TYPE"]:
                        globals()[paramm] = change_value(paramm, 0, FREE)                                                      
            else:  
                globals()[param] = change_value(param, val, FREE)

            if param == "NUM_BIRDS":
                generate_points_and_facultative_move(False, False)
                draw_points()                 
            elif param == "WIDTH":  
                generate_points_and_facultative_move(False, False)
                draw_status(False, True)
                draw_canvas()  
                draw()
            elif param == "HEIGHT":  
                generate_points_and_facultative_move(False, False)
                draw_status(False, True)
                draw_canvas()
                draw()
            elif param == "FREE":
                generate_points_and_facultative_move(False, False)
                draw()                       
            elif param == "SIZE":
                generate_points_and_facultative_move(False, False)
                draw()
            elif param =="FONT_SIZE" or param =="FONT_TYPE":
                draw_status(True, True)     
        elif getattr(event, "keysym", "").lower() == str(RESET_COMMAND) and RESET_HIDEN<=1:
            restore_options()
            generate_points_and_facultative_move(False, False)
            draw()
            draw_canvas()
            draw_status(False, True)
            root.state('normal')
            root.focus_force()
            root.focus_set()
        elif getattr(event, "keysym", "").lower() == str(REGENERATION_COMMAND) and REGENERATION_HIDEN<=1:
            global velocities
            global birds
            global paused
            pause= True
            velocities = []
            birds= [] 
            generate_points_and_facultative_move(False, False)
            draw_points()
        elif getattr(event, "keysym", "").lower() == str(TOOGLE_FPS_COMMAND) and TOOGLE_FPS_HIDEN<=1:
            fps = not fps
            draw_fps()
        elif getattr(event, "keysym", "").lower() == str(TOOGLE_START_PAUSE_COMMAND) and TOOGLE_START_PAUSE_HIDEN<=1:
            toggle_pause()
        elif getattr(event, "keysym", "").lower() == str(NEXT_FRAME_COMMAND) and NEXT_FRAME_HIDEN<=1:
            next_frame()
        elif getattr(event, "keysym", "").lower() == str(TOOGLE_MAXIMIZE_COMMAND) and TOOGLE_MAXIMIZE_HIDEN<=1:
            maximize_minimize(False)
        elif getattr(event, "keysym", "").lower() == str(DOC_COMMAND) and DOC_HIDEN<=1:
            help = f"pybirdsreynolds {version_prog}\n\n"+get_help_text()
            popin = tk.Toplevel(canvas)
            popin.title("Documentation - pybirdreynolds")
            popin.transient(canvas.winfo_toplevel())  
            popin.geometry("+200+200")  
            popin.configure(bg="gray") 

            frame = tk.Frame(popin, bg="gray")
            frame.pack(padx=10, pady=10)

            text_widget = tk.Text(
                frame,
                wrap="word",
                width=80,
                height=20,
                bg="gray",
                fg="black",
                insertbackground="black",
                highlightthickness=0,
                bd=0
            )
            text_widget.insert("1.0", help)
            text_widget.config(state="disabled")  
            text_widget.pack(side="left", fill="both", expand=True)

            scrollbar = tk.Scrollbar(frame, command=text_widget.yview)
            scrollbar.pack(side="right", fill="y")
            text_widget.config(yscrollcommand=scrollbar.set)
            popin.wait_visibility()
            popin.grab_set() 


        elif getattr(event, "keysym", "").lower() == str(HIDE_COMMAND) and HIDE_HIDEN<=1:
            global WIDTH_PARAMS, WIDTH_CONTROLS,WIDTH, hidden
            if not hidden:
                if is_maximized():
                    maximize_minimize(True)
                global trans_hiden
                trans_hiden=True
                WIDTH_PARAMS=0
                WIDTH_CONTROLS=0
                draw_status(True, True)
                generate_points_and_facultative_move(False, True)
                draw_canvas_hiden()
                hidden=True
                draw()
            else:
                WIDTH_PARAMS=WIDTH_PARAMS_DEFAULT
                WIDTH_CONTROLS=WIDTH_CONTROLS_DEFAULT
                if is_maximized():
                    WIDTH=root.winfo_width()-WIDTH_PARAMS-WIDTH_CONTROLS
                draw_status(True, True)
                generate_points_and_facultative_move(False, True)
                draw_canvas()
                hidden=False
                draw()
        draw_status(False, False)
    def is_maximized():
        if root.tk.call('tk', 'windowingsystem') == 'aqua':
            return bool(root.attributes("-fullscreen"))
        if root.state() == "zoomed":
            return True
        try:
            if root.attributes('-zoomed'):
                return True
        except tk.TclError:
            pass
        return (
            root.winfo_width() >= root.winfo_screenwidth() and
            root.winfo_height() >= root.winfo_screenheight()
        )

    def maximize_minimize(force):
        global width_before_maximized
        global heigth_before_maximized
        global WIDTH, HEIGHT  
        if is_maximized():
            root.state("normal")
            try:
                root.attributes('-zoomed', False)
            except tk.TclError:
                pass
            if not force:
                WIDTH=width_before_maximized
                HEIGHT=heigth_before_maximized
        else:
            width_before_maximized=WIDTH 
            heigth_before_maximized=HEIGHT          

            wm = root.tk.call('tk', 'windowingsystem')
            if wm == 'aqua':  # macOS
                root.attributes("-fullscreen", True)
            elif wm == 'win32':  # Windows
                root.state("zoomed")
            else:  # Linux
                try:
                    root.attributes('-zoomed', True)
                except tk.TclError:
                    root.attributes("-fullscreen", True)
        root.focus_force()
        root.focus_set()


    def on_resize(event):
        global trans_hiden
        global WIDTH, HEIGHT,WIDTH_PARAMS, WIDTH_CONTROLS 
        if trans_hiden:
            WIDTH = max(event.width - WIDTH_PARAMS - WIDTH_CONTROLS,WIDTH_MIN)
            HEIGHT = max(event.height,HEIGHT_PARAMS_CONTROLS_DEFAULT) 
            generate_points_and_facultative_move(False, False)
            draw_points()
            draw_rectangle()
            draw_fps()
            trans_hiden=False
            return
        WIDTH = max(event.width - WIDTH_PARAMS - WIDTH_CONTROLS -2,WIDTH_MIN)
        HEIGHT = max(event.height -2,HEIGHT_PARAMS_CONTROLS_DEFAULT) 
        generate_points_and_facultative_move(False, False)
        draw_status(False, True)
        draw_points()
        draw_rectangle()
        draw_fps()

    def draw_canvas_hiden():
        global root, canvas_bg, canvas, HEIGHT, WIDTH
        root.geometry(f"{WIDTH+2}x{max(HEIGHT, HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
        root.minsize(WIDTH+2, HEIGHT)
        root.maxsize(WIDTH+2, HEIGHT)
        width_tmp=WIDTH
        height_tmp=HEIGHT        
        root.update()
        root.minsize(WIDTH_MIN, HEIGHT_MIN)
        root.maxsize(10000, 10000)
        root.update()
        WIDTH=width_tmp
        HEIGHT=height_tmp       
        return

    def draw_canvas():
        global canvas_bg, HEIGHT, WIDTH
        
        root.geometry(f"{WIDTH_PARAMS+WIDTH+WIDTH_CONTROLS+2}x{max(HEIGHT, HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
        canvas.config(width=WIDTH_PARAMS+WIDTH+WIDTH_CONTROLS+2, height=max(HEIGHT,HEIGHT_PARAMS_CONTROLS_DEFAULT), bg=canvas_bg)

    def on_click(l, sens):
        global selected_index
        first_word = l.split()[0] if l.split() else None
        lines = [
            f"{name.removesuffix('_DOC'):15} :    {str(globals()[name.removesuffix('_DOC')]).split(maxsplit=1)[0]}"
            for name in globals()
            if name.endswith("_DOC")
            and globals().get(f"{name[:-4]}_HIDEN") == 0
        ] + [
            f"{name.removesuffix('_TEXT'):15} :    {globals()[name]} [{globals()[name.replace('_TEXT', '_COMMAND')]}]"
            for name in globals()
            if name.endswith("_TEXT")
            and globals().get(f"{name[:-5]}_HIDEN") == 0
        ]
        selected_index = next(
            (i for i, line in enumerate(lines) if line.split(":")[0].strip() == first_word),
            0
        )
        on_other_key(types.SimpleNamespace(keysym=sens))

    def draw_status(fullRefreshParams, fullRefreshControls):
        global FONT_TYPE, start_button, refresh_button, generation_button, WIDTH_CONTROLS, WIDTH_PARAMS
        base_globals = [
            var_name[:-8]
            for var_name in globals()
            if var_name.endswith("_DEFAULT")
        ]
        globals_button_down = "global " + ", ".join(name + "_BUTTON_DOWN" for name in base_globals)
        exec(globals_button_down)
        globals_button_up = "global " + ", ".join(name + "_BUTTON_UP" for name in base_globals)
        exec(globals_button_up) 

        normal_font = font.Font(family=FONT_TYPE, size=FONT_SIZE, weight="normal")
        bold_font   = font.Font(family=FONT_TYPE, size=FONT_SIZE, weight="bold")
        italic_font = font.Font(family=FONT_TYPE, size=FONT_SIZE, slant="italic")

        lines = [
            f"{name.removesuffix('_DOC'):15} :    {str(globals()[name.removesuffix('_DOC')]).split(maxsplit=1)[0]}"
            for name in globals()
            if name.endswith("_DOC")
            and globals().get(f"{name[:-4]}_HIDEN") == 0
        ] + [
            f"{name.removesuffix('_TEXT'):15} :    {globals()[name]} [{globals().get(name.replace('_TEXT', '_COMMAND'), '')}]"
            for name in globals()
            if name.endswith("_TEXT")
            and globals().get(f"{name[:-5]}_HIDEN") == 0
        ]
        x_text = 10
        y_text = 10
        canvas.delete("controls")
        canvas.delete("params")
        if WIDTH_PARAMS==0 and WIDTH_CONTROLS==0:
            canvas.delete("params_button")
            canvas.delete("controls_button")
            for name, value in globals().items():
                if name.endswith(("_BUTTON", "_BUTTON_UP", "_BUTTON_DOWN")):
                    globals()[name] = None
            return 

        i_param=-1
        i_control=-1 
        y_pos_control=0 
        for i, line in enumerate(lines):
            key = line.split()[0]
            font_to_use = normal_font
            fill = fill_color

            if i == selected_index and ARROWS_HIDE<2:
                i_param=i_param+1
                fill = "red"
                item= canvas.create_text(
                    x_text +  WIDTH_CONTROLS + WIDTH,
                    y_text + i_param * 2.3 * FONT_SIZE,
                    anchor="nw",
                    fill=fill,
                    font=font_to_use,
                    tags="params",
                    text=line.lower(),
                )
                create_canvas_tooltip(canvas, item, globals()[key.upper() + "_DOC"])
            elif "[" in line:
                i_control=i_control+1
                # fill = "yellow"
                # canvas.create_text(
                #     8 * x_text,
                #     2 * y_text + i_control * 2.1 * 2 * FONT_SIZE,
                #     anchor="nw",
                #     fill=fill,
                #     font=font_to_use,
                #     tags="controls",
                #     text=line.split(":", 1)[1].strip().lower(),
                # )
            elif not "[" in line:    
                i_param=i_param+1               
                item = canvas.create_text(
                    x_text  +  WIDTH_CONTROLS + WIDTH,
                    y_text + i_param * 2.3 * FONT_SIZE,
                    anchor="nw",
                    fill=fill_color,
                    font=font_to_use,
                    tags="params",
                    text=line.lower(),
                )
                create_canvas_tooltip(canvas, item, globals()[key.upper() + "_DOC"]+ " (" + display_range(key.upper()))
            y_pos_control = y_text + i_control * 2.1 * 2 * FONT_SIZE
            y_pos_param = y_text + i_param * 2.3 * FONT_SIZE
            
            
            if fullRefreshControls:         
                first_colon_index = line.find(":") + 1 
                f = font.Font(font=font_to_use)
                x_offset = 0
                if "[" in line:
                    key = line.split()[0]
                    btn_font = (FONT_TYPE, FONT_SIZE*2)
                    btn_width = 2
                    btn_height = 1
                    highlight_color = "black"
                    highlight_thickness = 2

                    name_button = key + "_BUTTON"
                    globals()[name_button]
                    key = line.split()[0]
                    icon = globals()[key.upper() + "_ICON"]
                    cmd = globals()[key.upper() + "_COMMAND"]

                    lbl_btn_tmp = tk.Label(
                        canvas, text=icon, fg="black", bg="white",
                        font=btn_font, width=btn_width, height=btn_height, anchor="center",
                        highlightbackground=highlight_color, highlightthickness=highlight_thickness
                    )

                    lbl_btn_tmp.bind("<Enter>", lambda e, w=lbl_btn_tmp, t=f"{globals()[key.upper() + "_TEXT"]}" + " [" + f"{globals()[key.upper() + "_COMMAND"]}" +"]": show_tip(w, t, e))
                    lbl_btn_tmp.bind("<Leave>", hide_tip)

                    lbl_btn_tmp.bind("<Button-1>", lambda e, c=cmd: on_other_key(types.SimpleNamespace(keysym=c)))

                    if globals()[name_button] is None:
                        globals()[name_button] = canvas.create_window(
                            x_text + x_offset + 2 ,
                            y_pos_control, anchor="nw", window=lbl_btn_tmp, tags=("controls_button",)
                        )
                    else:
                        canvas.coords(
                            globals()[name_button],
                            x_text + x_offset + 2 ,
                            y_pos_control
                        )

                first_colon_index = line.find(":") + 1 
                f = font.Font(font=font_to_use)
                x_offset = f.measure(line[:first_colon_index])
                if "[" not in line and ARROWS_HIDE<2:
                    highlight_color = "black"
                    highlight_thickness = 1                    
                    name_button_up=key+"_BUTTON_UP"
                    name_button_down=key+"_BUTTON_DOWN"
                    globals()[name_button_up]
                    globals()[name_button_down]
                    lbl_left = tk.Label(canvas, text="<", fg="black", bg="white", font=font_to_use , highlightbackground=highlight_color, highlightthickness=highlight_thickness)
                    lbl_left.bind("<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Left"))
                    lbl_left.bind("<ButtonRelease-1>", lambda e: stop_repeat())                                  
                    if globals()[name_button_down] is None: 
                        globals()[name_button_down] = canvas.create_window(x_text + x_offset + 1 + WIDTH_CONTROLS + WIDTH, y_pos_param, anchor="nw", window=lbl_left, tags=("params_button",))
                    else:
                        canvas.coords(globals()[name_button_down], x_text + x_offset + 1 + WIDTH_CONTROLS + WIDTH, y_pos_param)
                    lbl_right = tk.Label(canvas, text=">", fg="black", bg="white", font=font_to_use , highlightbackground=highlight_color, highlightthickness=highlight_thickness)
                    lbl_right.bind("<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Right"))
                    lbl_right.bind("<ButtonRelease-1>", lambda e: stop_repeat()) 
                    if globals()[name_button_up] is None: 
                        globals()[name_button_up] = canvas.create_window(x_text + x_offset + 18 + WIDTH_CONTROLS + WIDTH, y_pos_param, anchor="nw", window=lbl_right, tags=("params_button",))
                    else:
                        canvas.coords(globals()[name_button_up], x_text + x_offset + 18 + WIDTH_CONTROLS + WIDTH, y_pos_param)
        param_name = param_order[selected_index]   
        doc_text = param_docs.get(param_name, "") + " ("+display_range(param_name.upper())+")"
        if doc_text:
            return
            canvas.create_text(
                x_text + WIDTH_CONTROLS + WIDTH,
                HEIGHT,
                anchor="sw",
                fill=fill_color,
                font=italic_font,
                tags="params",
                text=param_name + " : " + doc_text,
                width=WIDTH_PARAMS - 2 * x_text
            )

    def draw_rectangle():
        global WIDTH_PARAMS, WIDTH_CONTROLS
        if not is_maximized():
            global width_before_maximized
            global heigth_before_maximized  
            width_before_maximized=WIDTH 
            heigth_before_maximized=HEIGHT         
        canvas.delete("boundary")
        canvas.create_rectangle(
            WIDTH_CONTROLS, 0, WIDTH_CONTROLS + WIDTH, HEIGHT,
            outline=fill_color, width=margin,
            tags="boundary"
        )

    def generate_points_and_facultative_move(with_move, translate):
        global velocities
        global new_velocities
        global hidden
        if not birds: 
            velocities = []
            for _ in range(NUM_BIRDS):
                px = random.randint(margin + WIDTH_CONTROLS, WIDTH - margin + WIDTH_CONTROLS)
                py = random.randint(margin, HEIGHT - margin)
                birds.append((px, py))
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, MAX_SPEED)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
                velocities.append((vx, vy))

        else:
            if translate:
                for i in range(len(birds)):
                    x, y = birds[i]
                    if hidden:
                        birds[i] = (x + WIDTH_CONTROLS_DEFAULT, y)
                    else:
                        birds[i] = (x - WIDTH_CONTROLS_DEFAULT, y)                               
            # Keep birds only if inside
            inside_points = []
            inside_velocities = []
            for (x, y), (vx, vy) in zip(birds, velocities):
                if WIDTH_CONTROLS + margin <= x <= WIDTH_CONTROLS + WIDTH - margin and 0 + margin <= y <= HEIGHT - margin:
                    inside_points.append((x, y))
                    inside_velocities.append((vx, vy))
            birds[:] = inside_points
            velocities[:] = inside_velocities
            new_velocities = []
            current_count = len(birds)
            
            # Add birds if not enough
            if NUM_BIRDS > current_count:
                for _ in range(NUM_BIRDS - current_count):
                    px = random.randint(margin + WIDTH_CONTROLS, WIDTH - margin + WIDTH_CONTROLS)
                    py = random.randint(margin, HEIGHT - margin)
                    birds.append((px, py))

                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0, MAX_SPEED)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    velocities.append((vx, vy))

            # Delete birds if not enough
            elif NUM_BIRDS < current_count:
                for _ in range(current_count - NUM_BIRDS):
                    idx = random.randint(0, len(birds) - 1)
                    birds.pop(idx)
                    velocities.pop(idx)

            if with_move:                    
                move()
    def move():
        global velocities
        global new_velocities
        #TODO n2 use Grid / Uniform Cell List 
        for i, (x, y) in enumerate(birds):
            move_sep_x, move_sep_y = 0, 0
            move_align_x, move_align_y, move_align_x_tmp, move_align_y_tmp = 0, 0, 0, 0
            move_coh_x, move_coh_y, move_coh_x_tmp, move_coh_y_tmp = 0, 0, 0, 0
            neighbors = 0
            vx, vy = velocities[i]
            if NEIGHBOR_RADIUS > 0 and not (SEP_WEIGHT == 0 and ALIGN_WEIGHT == 0 and COH_WEIGHT == 0):
                for j, (x2, y2) in enumerate(birds):
                    if i == j:
                        continue
                    dist = math.sqrt((x2 - x)**2 + (y2 - y)**2)
                    if dist < NEIGHBOR_RADIUS and dist > 0:
                        # SEPARATION
                        # If a neighbor is too close, add a vector to move away from it (opposite direction of the neighbor).
                        move_sep_x += (x - x2) / dist
                        move_sep_y += (y - y2) / dist
                        # ALIGNMENT
                        # Add the neighbor's velocity so the bird tends to align with it.
                        # Division is done later
                        vx2, vy2 = velocities[j]
                        move_align_x_tmp += vx2
                        move_align_y_tmp += vy2
                        # COHESION
                        # Add the neighbor's position to later calculate an average point, 
                        # so the bird moves toward the group's center.
                        # Division is done later
                        move_coh_x_tmp += x2
                        move_coh_y_tmp += y2
                        neighbors += 1
                
                if neighbors > 0:
                    move_align_x = move_align_x_tmp/neighbors
                    move_align_y = move_align_y_tmp/neighbors
                    move_coh_x = move_coh_x_tmp/neighbors
                    move_coh_y = move_coh_y_tmp/neighbors
                    move_coh_x = move_coh_x - x
                    move_coh_y = move_coh_y - y

                vx += SEP_WEIGHT * move_sep_x + ALIGN_WEIGHT * move_align_x + COH_WEIGHT * move_coh_x
                vy += SEP_WEIGHT * move_sep_y + ALIGN_WEIGHT * move_align_y + COH_WEIGHT * move_coh_y
      
            #RANDOM
            speed = math.sqrt(vx**2 + vy**2)
            if RANDOM_SPEED!=0:
                target_speed = MAX_SPEED / 2
                sigma_percent = RANDOM_SPEED   
                adjust_strength = 0.05 
                sigma_base = (sigma_percent / 100) * MAX_SPEED
                weight = 4 * speed * (MAX_SPEED - speed) / (MAX_SPEED ** 2)
                sigma = sigma_base * weight
                delta_speed = random.gauss(0, sigma)
                new_speed = speed + delta_speed
                new_speed += (target_speed - new_speed) * adjust_strength
                new_speed = max(0.1, min(MAX_SPEED, new_speed))
                factor = new_speed / speed
                vx *= factor
                vy *= factor
            if RANDOM_ANGLE!=0:
                angle = math.atan2(vy, vx)
                angle += math.radians(random.uniform(-1 * RANDOM_ANGLE, RANDOM_ANGLE))
                speed = math.sqrt(vx**2 + vy**2)
                vx = speed * math.cos(angle)
                vy = speed * math.sin(angle)
            vx, vy = limit_speed(vx, vy)
                
            new_velocities.append((vx, vy))

        velocities = new_velocities

        # Update positions
        new_points = []
        for (x, y), (vx, vy) in zip(birds, velocities):
            nx = x + vx
            ny = y + vy
            # Bounces
            while nx < margin + WIDTH_CONTROLS or nx > WIDTH - margin + WIDTH_CONTROLS:
                if nx < margin + WIDTH_CONTROLS:
                    overshoot = (margin + WIDTH_CONTROLS) - nx
                    nx = (margin + WIDTH_CONTROLS) + overshoot
                    vx = abs(vx)
                elif nx > WIDTH - margin + WIDTH_CONTROLS:
                    overshoot = nx - (WIDTH - margin + WIDTH_CONTROLS)
                    nx = (WIDTH - margin + WIDTH_CONTROLS) - overshoot
                    vx = -abs(vx)
            while ny < margin or ny > HEIGHT - margin:
                if ny < margin:
                    overshoot = margin - ny
                    ny = margin + overshoot
                    vy = abs(vy)
                elif ny > HEIGHT - margin:
                    overshoot = ny - (HEIGHT - margin)
                    ny = (HEIGHT - margin) - overshoot
                    vy = -abs(vy)
            idx = birds.index((x, y))
            velocities[idx] = (vx, vy)
            new_points.append((nx, ny))
        birds[:] = new_points


    def draw_points():
        for pid in point_ids:
            canvas.delete(pid)
        point_ids.clear()

        triangle_size = 6*SIZE
        triangle_width = 4*SIZE

        for (x, y), (vx, vy) in zip(birds, velocities):
            if not TRIANGLES: 
                pid = canvas.create_oval(
                    x - SIZE, y - SIZE,
                    x + SIZE, y + SIZE,
                    fill=fill_color, outline=outline_color)
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

                pid = canvas.create_polygon(
                    tip_x, tip_y,
                    left_x, left_y,
                    right_x, right_y,
                    fill=fill_color, outline=outline_color
                )
            point_ids.append(pid)


    def limit_speed(vx, vy):
        speed = math.sqrt(vx*vx + vy*vy)
        if speed > MAX_SPEED:
            vx = (vx / speed) * MAX_SPEED
            vy = (vy / speed) * MAX_SPEED
        return vx, vy

    def next_frame():
        if paused:
            generate_points_and_facultative_move(True, False)
            draw_points()

    def update():
        global frame_count, last_time, fps_value, count
        if not paused:
            generate_points_and_facultative_move(True, False)
            draw_points()
            draw_fps()
            frame_count += 1
            now = time.time()
            if not count:
                last_time = now
                count = True
            #add delay to stabilize fps    
            if now - last_time >= 1.0: 
                fps_value = frame_count / (now - last_time)
                frame_count = 0
                last_time = now 
        #reset fps        
        else:
            frame_count = 0
            count = False
            fps_value = 0          

        root.after(REFRESH_MS, update)

    def signal_handler(sig, frame):
        print("Interrupted! Closing application...")
        root.destroy() 
        sys.exit(0)

    def create_canvas_tooltip(canvas, item, text):
        tip_window = None

        def show_tip(event):
            global tip_window
            if tip_window is not None:
                try:
                    tip_window.destroy()
                except:
                    pass
                tip_window = None
            if not text:
                return
            x = canvas.winfo_rootx() + event.x + 10
            y = canvas.winfo_rooty() + event.y + 10
            tip_window = tw = tk.Toplevel(canvas)
            tw.wm_overrideredirect(True)
            tw.wm_geometry(f"+{x}+{y}")
            label = tk.Label(
                tw, text=text,
                background="yellow",
                relief="solid",
                borderwidth=1,
                font=(FONT_TYPE, FONT_SIZE),
                wraplength=200
            )
            label.pack(ipadx=4, ipady=2)

        def hide_tip(event):
            global tip_window
            if tip_window:
                tip_window.destroy()
                tip_window = None

        canvas.tag_bind(item, "<Enter>", show_tip)
        canvas.tag_bind(item, "<Leave>", hide_tip)

    def show_tip(widget, text, event=None):
        global tip_window

        if tip_window is not None:
            try:
                tip_window.destroy()
            except:
                pass
            tip_window = None

        if not text:
            return
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + widget.winfo_height() + 10
        tip_window = tw = tk.Toplevel(widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=text,
            background="yellow",
            relief="solid",
            borderwidth=1,
            font=(FONT_TYPE, FONT_SIZE) 
        )
        label.pack()

    def hide_tip(event=None):
        global tip_window
        if tip_window:
            tip_window.destroy()
            tip_window = None

            
    def rustine_1():
        root.geometry(f"{WIDTH_PARAMS + WIDTH +1+ WIDTH_CONTROLS}x{max(HEIGHT +1, HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
    def rustine_2():
        root.geometry(f"{WIDTH_PARAMS + WIDTH +3+ WIDTH_CONTROLS}x{max(HEIGHT +3, HEIGHT_PARAMS_CONTROLS_DEFAULT)}")

    global root, canvas


    root = tk.Tk()
    root.title(f"pybirdsreynolds")
    root.minsize(WIDTH_PARAMS+ WIDTH_MIN+WIDTH_CONTROLS, max(HEIGHT,HEIGHT_PARAMS_CONTROLS_DEFAULT))
    canvas = tk.Canvas(root, width=WIDTH_PARAMS+WIDTH+WIDTH_CONTROLS, height=HEIGHT, bg=canvas_bg)
    canvas.pack(fill="both", expand=True)

    global FONT_TYPE, FONT_TYPE, fonts
    default_fonts = [f for f in FONT_TYPE_LIST if f in font.families()] 
    available_fonts = font.families()
    mono_fonts = [f for f in available_fonts if "mono" in f.lower()]

    fonts = []
    for f in default_fonts + mono_fonts:
        if f not in fonts:
            fonts.append(f)

    if FONT_TYPE not in fonts:
        FONT_TYPE = fonts[0]  
        
    birds = [] 
    point_ids = []

    generate_points_and_facultative_move(True, False)
    draw()
    draw_status(True, True)
    draw_paused()
    root.bind('p', toggle_pause)
    root.bind("<Key>", on_other_key)
    root.bind_all("<Shift_L>", on_shift_press)
    root.bind_all("<Shift_R>", on_shift_press)
    root.bind_all("<KeyRelease-Shift_L>", on_shift_release)
    root.bind_all("<KeyRelease-Shift_R>", on_shift_release)

    canvas.bind("<Configure>", on_resize)
    
    signal.signal(signal.SIGINT, signal_handler)
    update()
    global last_x, last_y
    last_x = root.winfo_x()
    last_y = root.winfo_y()

    root.after(100, rustine_1)
    root.after(200, rustine_2)
    root.update()
    root.mainloop()           


