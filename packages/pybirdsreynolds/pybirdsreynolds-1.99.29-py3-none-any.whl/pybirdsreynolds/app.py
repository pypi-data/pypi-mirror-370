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
import types
import pybirdsreynolds.const as const
from pybirdsreynolds.draw import draw_paused, draw_fps, draw_hidden, draw_rectangle, draw_canvas, draw_canvas_hiden, draw_points, maximize_minimize, add_canvas_tooltip, add_widget_tooltip, is_maximized
import pybirdsreynolds.draw as draw
import pybirdsreynolds.reynolds as reynolds
from pybirdsreynolds.reynolds import generate_points_and_facultative_move

# variables
version_prog = version("pybirdsreynolds")
options = compute_args()
for var_name in dir(const):
    if var_name.endswith("_DEFAULT"):
        option_name = var_name[:-8]
        default_value = getattr(const, var_name)
        value = getattr(options, option_name.lower(), default_value)
        setattr(const, option_name, value)



trans_hiden=False
last_time = time.time()

frame_count = 0
fps_value = 0
fonts=[]
count= not const.PAUSED
resizing = False

selected_index=0
shift_pressed = False
width_before_maximized=const.WIDTH
heigth_before_maximized=const.HEIGHT
if not const.COLOR:
    const.CANVAS_BG = "black"
    const.FILL_COLOR = "white"
    const.OUTLINE_COLOR = "black"
else:
    const.CANVAS_BG = "#87CEEB"
    const.FILL_COLOR = "black"
    const.OUTLINE_COLOR = "white" 

start_button = None
refresh_button = None
generation_button = None

# deep copy
max_speed_init = copy.deepcopy(const.MAX_SPEED)
neighbor_radius_init = copy.deepcopy(const.NEIGHBOR_RADIUS)
num_birds_init = copy.deepcopy(const.NUM_BIRDS)
width_init = copy.deepcopy(const.WIDTH)
height_init = copy.deepcopy(const.HEIGHT)
refresh_ms_init = copy.deepcopy(const.REFRESH_MS)
random_speed_init = copy.deepcopy(const.RANDOM_SPEED)
random_angle_init = copy.deepcopy(const.RANDOM_ANGLE)
sep_weight_init = copy.deepcopy(const.SEP_WEIGHT)
align_weight_init = copy.deepcopy(const.ALIGN_WEIGHT)
coh_weight_init = copy.deepcopy(const.COH_WEIGHT)
size_init = copy.deepcopy(const.SIZE)
font_size_init = copy.deepcopy(const.FONT_SIZE)
font_type_init = copy.deepcopy(const.FONT_TYPE)
triangles_init = copy.deepcopy(const.TRIANGLES)
free_init = copy.deepcopy(const.FREE)
color_init= copy.deepcopy(const.COLOR)
repeating = {"active": False, "job": None}

def app():

    param_docs = {
        name.removesuffix("_DOC"): value
        for name, value in vars(const).items()
        if name.endswith("_DOC")
        and getattr(const, f"{name[:-4]}_HIDEN", 1) == 0 
    }
    param_order = list(param_docs.keys())

    def restore_options():

        global fonts
 
        const.MAX_SPEED = copy.deepcopy(max_speed_init)
        const.NEIGHBOR_RADIUS = copy.deepcopy(neighbor_radius_init)
        const.NUM_BIRDS = copy.deepcopy(num_birds_init)
        const.WIDTH = copy.deepcopy(width_init)
        const.HEIGHT = copy.deepcopy(height_init)
        const.REFRESH_MS = copy.deepcopy(refresh_ms_init)
        const.RANDOM_SPEED = copy.deepcopy(random_speed_init)
        const.ANDOM_ANGLE = copy.deepcopy(random_angle_init)
        const.SEP_WEIGHT = copy.deepcopy(sep_weight_init)
        const.ALIGN_WEIGHT = copy.deepcopy(align_weight_init)
        const.COH_WEIGHT = copy.deepcopy(coh_weight_init)
        const.SIZE = copy.deepcopy(size_init)
        const.COLOR = copy.deepcopy(color_init)
        const.FREE = copy.deepcopy(free_init)
        const.TRIANGLES = copy.deepcopy(triangles_init)
        #TODO mieux gérer le font_type
        #const.FONT_TYPE = copy.deepcopy(font_type_init)   

        if not const.COLOR:
            const.CANVAS_BG = "black"
            const.FILL_COLOR = "white"
            const.OUTLINE_COLOR = "black"
        else:
            const.CANVAS_BG = "#87CEEB"
            const.FILL_COLOR = "black"
            const.OUTLINE_COLOR = "white" 

    def start_repeat(ligne, direction):
        def repeat():
            on_click(ligne, direction)
            if repeating["active"]:
                repeating["job"] = draw.canvas.after(100, repeat)
        repeating["active"] = True
        repeat()

    def stop_repeat():
        repeating["active"] = False
        if repeating["job"]:
            draw.canvas.after_cancel(repeating["job"])
            repeating["job"] = None

    def on_shift_press(event):
        global shift_pressed
        shift_pressed = True

    def on_shift_release(event):
        global shift_pressed
        shift_pressed = False

    def draw():
        draw_status(False, False)
        draw_points(draw.canvas, reynolds.birds, reynolds.velocities)
        draw_rectangle(draw.canvas, draw.root)
        draw_fps(draw.canvas, fps_value)
        draw_hidden(draw.canvas)

    def toggle_pause(event=None):
        const.BLINK_STATE = True
        const.PAUSED = not const.PAUSED
        draw_status(False, False)
        draw_paused(draw.canvas)

    def change_value(type, val, free):
        value = getattr(const, type, None)
        prefix = type.upper()
        default       = getattr(const, f"{prefix}_DEFAULT", None)
        min_value     = getattr(const, f"{prefix}_MIN", None)
        max_value     = getattr(const, f"{prefix}_MAX", None)
        min_free_value = getattr(const, f"{prefix}_FREE_MIN", None)
        max_free_value = getattr(const, f"{prefix}_FREE_MAX", None)                
        value += val
        if not free:
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
        global selected_index
        global fonts
        global shift_pressed
        shift = getattr(event, "state", None)        
        if shift is not None:
            shift = (shift & 0x1) != 0
        else:
            shift = shift_pressed
        if const.SHIFT_HIDEN==0:
            shift =False    
        mult = 10 if shift else 1
        val = mult if event.keysym == "Right" else 1*-mult
        param = param_order[selected_index]
        if (param == "WIDTH" or param == "HEIGHT") and is_maximized(draw.root):
            val=0
        if event.keysym == "Up" and const.ARROWS_HIDE<2:
            selected_index = (selected_index - 1) % len(param_order)
        elif event.keysym == "Down" and const.ARROWS_HIDE<2:
            selected_index = (selected_index + 1) % len(param_order)
        elif (event.keysym == "Right"  or event.keysym == "Left") and const.ARROWS_HIDE<=1:
            if param == "TRIANGLES":
                const.TRIANGLES = not const.TRIANGLES
                draw()
            elif param == "FONT_TYPE":
                current_index = fonts.index(const.FONT_TYPE)
                const.FONT_TYPE = fonts[(current_index + val) % len(fonts)]
                draw()
                draw_status(True, True)               
            elif param == "COLOR":
                COLOR = not COLOR 
                if not COLOR:
                    const.CANVAS_BG = "black"
                    const.FILL_COLOR = "white"
                    const.OUTLINE_COLOR = "black"
                else:
                    const.CANVAS_BG = "#87CEEB"
                    const.FILL_COLOR = "black"
                    const.OUTLINE_COLOR = "white" 
                draw_canvas(draw.canvas,draw.root)
                draw()
            elif param == "FREE":
                const.FREE = not const.FREE
                for paramm in param_order:
                    if paramm not in ["FREE", "COLOR" , "TRIANGLES", "FONT_TYPE"]:
                        setattr(const, paramm, change_value(paramm, 0, const.FREE))                                                   
            else:  
                setattr(const, param, change_value(param, val, const.FREE))

            if param == "NUM_BIRDS":
                generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
                draw_points(draw.canvas, reynolds.birds, reynolds.velocities)                 
            elif param == "WIDTH":  
                generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
                draw_status(False, True)
                draw_canvas(draw.canvas,draw.root)  
                draw()
            elif param == "HEIGHT":  
                generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
                draw_status(False, True)
                draw_canvas(draw.canvas,draw.root)
                draw()
            elif param == "FREE":
                generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
                draw()                       
            elif param == "SIZE":
                generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
                draw()
            elif param =="FONT_SIZE" or param =="FONT_TYPE":
                draw_status(True, True)     
        elif getattr(event, "keysym", "").lower() == str(const.RESET_COMMAND) and const.RESET_HIDEN<=1:
            restore_options()
            generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
            draw()
            draw_canvas(draw.canvas,draw.root)
            draw_status(False, True)
            draw.root.state('normal')
            draw.root.focus_force()
            draw.root.focus_set()
        elif getattr(event, "keysym", "").lower() == str(const.REGENERATION_COMMAND) and const.REGENERATION_HIDEN<=1:
            reynolds.velocities = []
            reynolds.birds= [] 
            generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
            draw_points(draw.canvas, reynolds.birds, reynolds.velocities)
        elif getattr(event, "keysym", "").lower() == str(const.TOOGLE_FPS_COMMAND) and const.TOOGLE_FPS_HIDEN<=1:
            const.FPS = not const.FPS
            draw_fps(draw.canvas, fps_value)
        elif getattr(event, "keysym", "").lower() == str(const.TOOGLE_START_PAUSE_COMMAND) and const.TOOGLE_START_PAUSE_HIDEN<=1:
            toggle_pause()
        elif getattr(event, "keysym", "").lower() == str(const.NEXT_FRAME_COMMAND) and const.NEXT_FRAME_HIDEN<=1:
            next_frame()
        elif getattr(event, "keysym", "").lower() == str(const.TOOGLE_MAXIMIZE_COMMAND) and const.TOOGLE_MAXIMIZE_HIDEN<=1:
            maximize_minimize(draw.root, False)
        elif getattr(event, "keysym", "").lower() == str(const.DOC_COMMAND) and const.DOC_HIDEN<=1:
            help = f"pybirdsreynolds {version_prog}\n\n"+get_help_text()
            popin = tk.Toplevel(draw.canvas)
            popin.title("Documentation - pybirdreynolds")
            popin.transient(draw.canvas.winfo_toplevel())  
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


        elif getattr(event, "keysym", "").lower() == str(const.HIDE_COMMAND) and const.HIDE_HIDEN<=1:
            if not const.HIDDEN:
                if is_maximized(draw.root):
                    maximize_minimize(draw.root, True)
                global trans_hiden
                trans_hiden=True
                const.WIDTH_PARAMS=0
                const.WIDTH_CONTROLS=0
                draw_status(True, True)
                generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, True)
                draw_canvas_hiden(draw.root)
                const.HIDDEN=True
                draw()
            else:
                const.WIDTH_PARAMS=const.WIDTH_PARAMS_DEFAULT
                const.WIDTH_CONTROLS=const.WIDTH_CONTROLS_DEFAULT
                if is_maximized(draw.root):
                    const.WIDTH=draw.root.winfo_width()-const.WIDTH_PARAMS-const.WIDTH_CONTROLS
                draw_status(True, True)
                generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, True)
                draw_canvas(draw.canvas,draw.root)
                const.HIDDEN=False
                draw()
        draw_status(False, False)

    def on_resize(event):
        global trans_hiden
        if trans_hiden:
            const.WIDTH = max(event.width - const.WIDTH_PARAMS - const.WIDTH_CONTROLS,const.WIDTH_MIN)
            const.HEIGHT = max(event.height,const.HEIGHT_PARAMS_CONTROLS_DEFAULT) 
            generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
            draw_points(draw.canvas, reynolds.birds, reynolds.velocities)
            draw_rectangle(draw.canvas, draw.root)
            draw_fps(draw.canvas, fps_value)
            trans_hiden=False
            return
        const.WIDTH = max(event.width - const.WIDTH_PARAMS - const.WIDTH_CONTROLS -2,const.WIDTH_MIN)
        const.HEIGHT = max(event.height -2,const.HEIGHT_PARAMS_CONTROLS_DEFAULT) 
        generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,False, False)
        draw_status(False, True)
        draw_points(draw.canvas, reynolds.birds, reynolds.velocities)
        draw_rectangle(draw.canvas, draw.root)
        draw_fps(draw.canvas, fps_value)

    def on_click(l, sens):
        global selected_index
        first_word = l.split()[0] if l.split() else None
        lines = [
            f"{name.removesuffix('_DOC'):15} :    {str(getattr(const, name.removesuffix('_DOC'))).split(maxsplit=1)[0]}"
            for name in vars(const)
            if name.endswith("_DOC")
            and getattr(const, f"{name[:-4]}_HIDEN", 1) == 0
        ] + [
            f"{name.removesuffix('_TEXT'):15} :    {getattr(const, name)} [{getattr(const, name.replace('_TEXT', '_COMMAND'), '')}]"
            for name in vars(const)
            if name.endswith("_TEXT")
            and getattr(const, f"{name[:-5]}_HIDEN", 1) == 0
        ]
        selected_index = next(
            (i for i, line in enumerate(lines) if line.split(":")[0].strip() == first_word),
            0
        )
        on_other_key(types.SimpleNamespace(keysym=sens))

    def draw_status(fullRefreshParams, fullRefreshControls):
        global start_button, refresh_button, generation_button
        # récupérer toutes les variables _DEFAULT dans const
        base_globals = [
            var_name[:-8]  # enlever le "_DEFAULT"
            for var_name in vars(const)
            if var_name.endswith("_DEFAULT")
        ]


        normal_font = font.Font(family=const.FONT_TYPE, size=const.FONT_SIZE, weight="normal")
        bold_font   = font.Font(family=const.FONT_TYPE, size=const.FONT_SIZE, weight="bold")
        italic_font = font.Font(family=const.FONT_TYPE, size=const.FONT_SIZE, slant="italic")

        lines = [
            f"{name.removesuffix('_DOC'):15} :    {str(getattr(const, name.removesuffix('_DOC'))).split(maxsplit=1)[0]}"
            for name in vars(const)
            if name.endswith("_DOC")
            and getattr(const, f"{name[:-4]}_HIDEN", 1) == 0
        ] + [
            f"{name.removesuffix('_TEXT'):15} :    {getattr(const, name)} [{getattr(const, name.replace('_TEXT', '_COMMAND'), '')}]"
            for name in vars(const)
            if name.endswith("_TEXT")
            and getattr(const, f"{name[:-5]}_HIDEN", 1) == 0
        ]
        x_text = 10
        y_text = 10
        draw.canvas.delete("controls")
        draw.canvas.delete("params")
        if const.WIDTH_PARAMS==0 and const.WIDTH_CONTROLS==0:
            draw.canvas.delete("params_button")
            draw.canvas.delete("controls_button")
            for name in dir(const):
                if name.endswith(("_BUTTON", "_BUTTON_UP", "_BUTTON_DOWN")):
                    setattr(const, name, None)
            return 

        i_param=-1
        i_control=-1 
        y_pos_control=0 
        for i, line in enumerate(lines):
            key = line.split()[0]
            font_to_use = normal_font
            fill = const.FILL_COLOR

            if i == selected_index and const.ARROWS_HIDE<2:
                i_param=i_param+1
                fill = "red"
                item= draw.canvas.create_text(
                    x_text +  const.WIDTH_CONTROLS + const.WIDTH,
                    y_text + i_param * 2.3 * const.FONT_SIZE,
                    anchor="nw",
                    fill=fill,
                    font=font_to_use,
                    tags="params",
                    text=line.lower(),
                )
                add_canvas_tooltip(draw.canvas, item, getattr(const, key.upper() + "_DOC"))
            elif "[" in line:
                i_control=i_control+1
            elif not "[" in line:    
                i_param=i_param+1               
                item = draw.canvas.create_text(
                    x_text  +  const.WIDTH_CONTROLS + const.WIDTH,
                    y_text + i_param * 2.3 * const.FONT_SIZE,
                    anchor="nw",
                    fill=const.FILL_COLOR,
                    font=font_to_use,
                    tags="params",
                    text=line.lower(),
                )
                add_canvas_tooltip(
                    draw.canvas,
                    item,
                    getattr(const, key.upper() + "_DOC") + " (" + display_range(key.upper()) + ")"
)

            y_pos_control = y_text + i_control * 2.1 * 2 * const.FONT_SIZE
            y_pos_param = y_text + i_param * 2.3 * const.FONT_SIZE
            
            
            if fullRefreshControls:         
                first_colon_index = line.find(":") + 1 
                f = font.Font(font=font_to_use)
                x_offset = 0
                if "[" in line:
                    key = line.split()[0]
                    btn_font = (const.FONT_TYPE, const.FONT_SIZE*2)
                    btn_width = 2
                    btn_height = 1
                    highlight_color = "black"
                    highlight_thickness = 2

                    name_button = key + "_BUTTON"
                    key = line.split()[0]
                    icon = getattr(const, key.upper() + "_ICON")
                    cmd  = getattr(const, key.upper() + "_COMMAND")

                    lbl_btn_tmp = tk.Label(
                        draw.canvas, text=icon, fg="black", bg="white",
                        font=btn_font, width=btn_width, height=btn_height, anchor="center",
                        highlightbackground=highlight_color, highlightthickness=highlight_thickness
                    )

                    tooltip_text = f"{getattr(const, key.upper() + '_TEXT')} [{getattr(const, key.upper() + '_COMMAND')}]"
                    add_widget_tooltip(lbl_btn_tmp, tooltip_text)

                    lbl_btn_tmp.bind("<Button-1>", lambda e, c=cmd: on_other_key(types.SimpleNamespace(keysym=c)))

                    # Création du bouton
                    if getattr(const, name_button, None) is None:
                        setattr(
                            const,
                            name_button,
                            draw.canvas.create_window(
                                x_text + x_offset + 2,
                                y_pos_control,
                                anchor="nw",
                                window=lbl_btn_tmp,
                                tags=("controls_button",)
                            )
                        )
                    else:
                        draw.canvas.coords(
                            getattr(const, name_button),
                            x_text + x_offset + 2,
                            y_pos_control
                        )

                first_colon_index = line.find(":") + 1 
                f = font.Font(font=font_to_use)
                x_offset = f.measure(line[:first_colon_index])
                if "[" not in line and const.ARROWS_HIDE<2:
                    highlight_color = "black"
                    highlight_thickness = 1                    
                    name_button_up=key+"_BUTTON_UP"
                    name_button_down=key+"_BUTTON_DOWN"
                    lbl_left = tk.Label(draw.canvas, text="<", fg="black", bg="white", font=font_to_use , highlightbackground=highlight_color, highlightthickness=highlight_thickness)
                    lbl_left.bind("<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Left"))
                    lbl_left.bind("<ButtonRelease-1>", lambda e: stop_repeat())                                  
                    if not hasattr(const, name_button_down) or getattr(const, name_button_down) is None: 
                        setattr(
                            const,
                            name_button_down,
                            draw.canvas.create_window(
                                x_text + x_offset + 1 + const.WIDTH_CONTROLS + const.WIDTH,
                                y_pos_param,
                                anchor="nw",
                                window=lbl_left,
                                tags=("params_button",)
                            )
                        )

                    else:
                        draw.canvas.coords(getattr(const, name_button_down), x_text + x_offset + 1 + const.WIDTH_CONTROLS + const.WIDTH, y_pos_param)
                    lbl_right = tk.Label(draw.canvas, text=">", fg="black", bg="white", font=font_to_use , highlightbackground=highlight_color, highlightthickness=highlight_thickness)
                    lbl_right.bind("<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Right"))
                    lbl_right.bind("<ButtonRelease-1>", lambda e: stop_repeat()) 
                    if not hasattr(const, name_button_up) or getattr(const, name_button_up) is None: 
                        setattr(
                            const,
                            name_button_up,
                            draw.canvas.create_window(
                                x_text + x_offset + 18 + const.WIDTH_CONTROLS + const.WIDTH,
                                y_pos_param,
                                anchor="nw",
                                window=lbl_right,
                                tags=("params_button",)
                            )
                        )
                    else:
                        draw.canvas.coords(getattr(const, name_button_up), x_text + x_offset + 18 + const.WIDTH_CONTROLS + const.WIDTH, y_pos_param)

    def next_frame():
        if const.PAUSED:
            generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,True, False)
            draw_points(draw.canvas, reynolds.birds, reynolds.velocities)

    def update():
        global frame_count, last_time, fps_value, count
        if not const.PAUSED:
            generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,True, False)
            draw_points(draw.canvas, reynolds.birds, reynolds.velocities)
            draw_fps(draw.canvas, fps_value)
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

        draw.root.after(const.REFRESH_MS, update)

    def signal_handler(sig, frame):
        print("Interrupted! Closing application...")
        draw.root.destroy() 
        sys.exit(0)
            
    def rustine_1():
        draw.root.geometry(f"{const.WIDTH_PARAMS + const.WIDTH +1+ const.WIDTH_CONTROLS}x{max(const.HEIGHT +1, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
    def rustine_2():
        draw.root.geometry(f"{const.WIDTH_PARAMS + const.WIDTH +3+ const.WIDTH_CONTROLS}x{max(const.HEIGHT +3, const.HEIGHT_PARAMS_CONTROLS_DEFAULT)}")

    draw.root = tk.Tk()
    draw.root.title(f"pybirdsreynolds")
    draw.root.minsize(const.WIDTH_PARAMS+ const.WIDTH_MIN+const.WIDTH_CONTROLS, max(const.HEIGHT,const.HEIGHT_PARAMS_CONTROLS_DEFAULT))
    draw.canvas = tk.Canvas(draw.root, width=const.WIDTH_PARAMS+const.WIDTH+const.WIDTH_CONTROLS, height=const.HEIGHT, bg=const.CANVAS_BG)
    draw.canvas.pack(fill="both", expand=True)

    
    default_fonts = [f for f in const.FONT_TYPE_LIST if f in font.families()] 
    available_fonts = font.families()
    mono_fonts = [f for f in available_fonts if "mono" in f.lower()]

    fonts = []
    for f in default_fonts + mono_fonts:
        if f not in fonts:
            fonts.append(f)

    if const.FONT_TYPE not in fonts:
        const.FONT_TYPE = fonts[0]  
        
    generate_points_and_facultative_move(reynolds.birds, reynolds.velocities,True, False)
    draw()
    draw_status(True, True)
    draw_paused(draw.canvas)
    draw.root.bind('p', toggle_pause)
    draw.root.bind("<Key>", on_other_key)
    draw.root.bind_all("<Shift_L>", on_shift_press)
    draw.root.bind_all("<Shift_R>", on_shift_press)
    draw.root.bind_all("<KeyRelease-Shift_L>", on_shift_release)
    draw.root.bind_all("<KeyRelease-Shift_R>", on_shift_release)

    draw.canvas.bind("<Configure>", on_resize)
    
    signal.signal(signal.SIGINT, signal_handler)
    update()
    global last_x, last_y
    last_x = draw.root.winfo_x()
    last_y = draw.root.winfo_y()

    draw.root.after(100, rustine_1)
    draw.root.after(200, rustine_2)
    draw.root.update()
    draw.root.mainloop()           


