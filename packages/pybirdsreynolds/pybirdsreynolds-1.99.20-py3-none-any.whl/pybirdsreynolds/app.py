import tkinter as tk
import random
import math
from pybirdsreynolds.args import compute_args, display_range
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
        option_name = var_name[:-8].lower()
        value = getattr(options, option_name, default_value)
        globals()[option_name] = value
        globals()[option_name+"_button_up"] = None
        globals()[option_name+"_button_down"] = None
    if var_name.endswith("_TEXT"):
        option_name = var_name[:-5].lower()
        value = getattr(options, option_name, default_value)
        globals()[option_name] = value
        globals()[option_name+"_button"] = None

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
width_before_maximized=width
heigth_before_maximized=height
if not color:
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
max_speed_init = copy.deepcopy(max_speed)
neighbor_radius_init = copy.deepcopy(neighbor_radius)
num_birds_init = copy.deepcopy(num_birds)
width_init = copy.deepcopy(width)
height_init = copy.deepcopy(height)
refresh_ms_init = copy.deepcopy(refresh_ms)
random_speed_init = copy.deepcopy(random_speed)
random_angle_init = copy.deepcopy(random_angle)
sep_weight_init = copy.deepcopy(sep_weight)
align_weight_init = copy.deepcopy(align_weight)
coh_weight_init = copy.deepcopy(coh_weight)
size_init = copy.deepcopy(size)
font_size_init = copy.deepcopy(font_size)
font_type_init = copy.deepcopy(font_type)
triangles_init = copy.deepcopy(triangles)
free_init = copy.deepcopy(free)
color_init= copy.deepcopy(color)
repeating = {"active": False, "job": None}


# doc dict
param_docs = {
    name.lower().removesuffix("_doc"): value
    for name, value in globals().items()
    if name.endswith("_DOC")
}
param_order = list(param_docs.keys())

def app():

    def restore_options():

        global max_speed, neighbor_radius, num_birds, width, height
        global refresh_ms, random_speed, random_angle
        global sep_weight, align_weight, coh_weight
        global paused, size, triangles, color, canvas_bg, font_size, font_type, fonts
        global fill_color, outline_color, fps, free
 
        max_speed = copy.deepcopy(max_speed_init)
        neighbor_radius = copy.deepcopy(neighbor_radius_init)
        num_birds = copy.deepcopy(num_birds_init)
        width = copy.deepcopy(width_init)
        height = copy.deepcopy(height_init)
        refresh_ms = copy.deepcopy(refresh_ms_init)
        random_speed = copy.deepcopy(random_speed_init)
        random_angle = copy.deepcopy(random_angle_init)
        sep_weight = copy.deepcopy(sep_weight_init)
        align_weight = copy.deepcopy(align_weight_init)
        coh_weight = copy.deepcopy(coh_weight_init)
        size = copy.deepcopy(size_init)
        color = copy.deepcopy(color_init)
        free = copy.deepcopy(free_init)
        triangles = copy.deepcopy(triangles_init)
        font_type = copy.deepcopy(font_type)   

        if not color:
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
                repeating["job"] = canvas.after(100, repeat)  # répète toutes les 100ms
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

    def draw_fps():
        global font_type
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
                width_controls,
                0,            
                anchor="nw",  
                fill="yellow",
                font=(font_type, font_size, "bold"),
                tags="fps",
                text=f" FPS : {value}"
        )

    def draw_paused():
        global font_type
        global blink_state
        canvas.delete("paused")
        if paused:
            if blink_state:
                canvas.create_text(
                    width_controls,
                    max(height, HEIGHT_PARAMS_CONTROLS_DEFAULT),
                    anchor="sw",
                    fill="red",
                    font=(font_type, font_size, "bold"),
                    tags="paused",
                    text=" PAUSED "
                )
            blink_state = not blink_state
            canvas.after(500, draw_paused)

    def toggle_pause(event=None):
        global paused
        global blink_state
        blink_state = True
        paused = not paused
        draw_status(False, False)
        draw_paused()

    def change_value(type, val, free):
        value = globals().get(type)
        prefix = type.upper()
        default = globals().get(f"{prefix}_DEFAULT")
        min_value = globals().get(f"{prefix}_MIN")
        max_value = globals().get(f"{prefix}_MAX")
        min_free_value = globals().get(f"{prefix}_FREE_MIN")
        max_free_value = globals().get(f"{prefix}_FREE_MAX")                    
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
        global selected_index, num_birds, max_speed
        global neighbor_radius, sep_weight, align_weight
        global coh_weight, size, random_speed, random_angle
        global triangles, free , refresh_ms, width, height, fonts
        global color, canvas_bg, fill_color, outline_color, fps, font_type
        global shift_pressed
        shift = getattr(event, "state", None)        
        if shift is not None:
            shift = (shift & 0x1) != 0
        else:
            shift = shift_pressed
        mult = 10 if shift else 1
        val = mult if event.keysym == "Right" else 1*-mult
        param = param_order[selected_index]
        if (param == "width" or param == "height") and is_maximized():
            val=0
        if event.keysym == "Up":
            selected_index = (selected_index - 1) % len(param_order)
        elif event.keysym == "Down":
            selected_index = (selected_index + 1) % len(param_order)
        elif event.keysym == "Right"  or event.keysym == "Left":
            if param == "triangles":
                triangles = not triangles
                draw()
            elif param == "font_type":
                current_index = fonts.index(font_type)
                font_type = fonts[(current_index + val) % len(fonts)]
                draw()
                draw_status(True, True)               
            elif param == "color":
                color = not color 
                if not color:
                    canvas_bg = "black"
                    fill_color = "white"
                    outline_color = "black"
                else:
                    canvas_bg = "#87CEEB"
                    fill_color = "black"
                    outline_color = "white" 
                draw_canvas()
                draw()
            elif param == "free":
                free = not free
                for paramm in param_order:
                    if paramm not in ["free", "color" , "triangles", "font_type"]:
                        globals()[paramm] = change_value(paramm, 0, free)                                                      
            else:  
                globals()[param] = change_value(param, val, free)

            if param == "num_birds":
                generate_points_and_facultative_move(False, False)
                draw_points()                 
            elif param == "width":  
                generate_points_and_facultative_move(False, False)
                draw_status(False, True)
                draw_canvas()  
                draw()
            elif param == "height":  
                generate_points_and_facultative_move(False, False)
                draw_status(False, True)
                draw_canvas()
                draw()
            elif param == "free":
                generate_points_and_facultative_move(False, False)
                draw()                       
            elif param == "size":
                generate_points_and_facultative_move(False, False)
                draw()
            elif param =="font_size" or param =="font_type":
                draw_status(True, True)     
        elif getattr(event, "keysym", "").lower() == str(RESET_COMMAND):
            restore_options()
            generate_points_and_facultative_move(False, False)
            draw()
            draw_canvas()
            draw_status(False, True)
            root.state('normal')
            root.focus_force()
            root.focus_set()
        elif getattr(event, "keysym", "").lower() == str(REGENERATION_COMMAND):
            global velocities
            global birds
            global paused
            pause= True
            velocities = []
            birds= [] 
            generate_points_and_facultative_move(False, False)
            draw_points()
        elif getattr(event, "keysym", "").lower() == str(TOOGLE_FPS_COMMAND):
            fps = not fps
            draw_fps()
        elif getattr(event, "keysym", "").lower() == str(TOOGLE_START_PAUSE_COMMAND):
            toggle_pause()
        elif getattr(event, "keysym", "").lower() == str(NEXT_FRAME_COMMAND):
            frame()
        elif getattr(event, "keysym", "").lower() == str(TOOGLE_MAXIMIZE_COMMAND):
            maximize_minimize(False)
        elif getattr(event, "keysym", "").lower() == str(HIDE_COMMAND):
            global width_params, width_controls,width, hidden
            if not hidden:
                if is_maximized():
                    maximize_minimize(True)
                global trans_hiden
                trans_hiden=True
                width_params=0
                width_controls=0
                draw_status(True, True)
                generate_points_and_facultative_move(False, True)
                draw_canvas_hiden()
                draw()
                root.title(f"pybirdsreynolds - "+HIDE_COMMAND+" to display commands")
                hidden=True            
            else:
                width_params=WIDTH_PARAMS_DEFAULT
                width_controls=WIDTH_CONTROLS_DEFAULT
                if is_maximized():
                    width=root.winfo_width()-width_params-width_controls
                draw_status(True, True)
                generate_points_and_facultative_move(False, True)
                draw_canvas()
                draw()
                root.title(f"pybirdsreynolds - {version_prog}")
                hidden=False
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
        global width, height  
        if is_maximized():
            root.state("normal")
            try:
                root.attributes('-zoomed', False)
            except tk.TclError:
                pass
            if not force:
                width=width_before_maximized
                height=heigth_before_maximized
            #draw_canvas()
        else:
            width_before_maximized=width 
            heigth_before_maximized=height          

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
        global width, height,width_params, width_controls 
        if trans_hiden:
            width = max(event.width - width_params - width_controls,WIDTH_MIN)
            height = max(event.height,HEIGHT_PARAMS_CONTROLS_DEFAULT) 
            generate_points_and_facultative_move(False, False)
            draw_points()
            draw_rectangle()
            draw_fps()
            trans_hiden=False
            return
        width = max(event.width - width_params - width_controls -2,WIDTH_MIN)
        height = max(event.height -2,HEIGHT_PARAMS_CONTROLS_DEFAULT) 
        generate_points_and_facultative_move(False, False)
        draw_status(False, True)
        draw_points()
        draw_rectangle()
        draw_fps()

    def draw_canvas_hiden():
        global root, canvas_bg, canvas, height, width
        root.geometry(f"{width+2}x{max(height, HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
        root.minsize(width+2, height)
        root.maxsize(width+2, height)
        root.update()
        root.minsize(WIDTH_MIN, HEIGHT_MIN)
        root.maxsize(10000, 10000)
        root.update()
        return

    def draw_canvas():
        global canvas_bg, height, width
        
        root.geometry(f"{width_params+width+width_controls+2}x{max(height, HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
        canvas.config(width=width_params+width+width_controls+2, height=max(height,HEIGHT_PARAMS_CONTROLS_DEFAULT), bg=canvas_bg)

    def on_click(l, sens):
        global selected_index
        first_word = l.split()[0] if l.split() else None
        lines = [
            f"{name.lower().removesuffix('_doc'):15} :    {str(globals()[name.lower().removesuffix('_doc')]).split(maxsplit=1)[0]}"
            for name in globals()
            if name.endswith("_DOC")
        ] + [
            f"{name.lower().removesuffix('_text'):15} :    {globals()[name]} [{globals()[name.replace('_TEXT', '_COMMAND')]}]"
            for name in globals()
            if name.endswith("_TEXT")
        ]
        selected_index = next(
            (i for i, line in enumerate(lines) if line.split(":")[0].strip() == first_word),
            0
        )
        on_other_key(types.SimpleNamespace(keysym=sens))

    def draw_status(fullRefreshParams, fullRefreshControls):
        global font_type, start_button, refresh_button, generation_button, width_controls, width_params
        base_globals = [
            var_name[:-8].lower()
            for var_name in globals()
            if var_name.endswith("_DEFAULT")
        ]
        globals_button_down = "global " + ", ".join(name + "_button_down" for name in base_globals)
        exec(globals_button_down)
        globals_button_up = "global " + ", ".join(name + "_button_up" for name in base_globals)
        exec(globals_button_up) 

        normal_font = font.Font(family=font_type, size=font_size, weight="normal")
        bold_font   = font.Font(family=font_type, size=font_size, weight="bold")
        italic_font = font.Font(family=font_type, size=font_size, slant="italic")

        lines = [
            f"{name.lower().removesuffix('_doc'):15} :    {str(globals()[name.lower().removesuffix('_doc')]).split(maxsplit=1)[0]}"
            for name in globals()
            if name.endswith("_DOC")
        ] + [
            f"{name.lower().removesuffix('_text'):15} :    {globals()[name]} [{globals().get(name.replace('_TEXT', '_COMMAND'), '')}]"
            for name in globals()
            if name.endswith("_TEXT")
        ]
        x_text = 10
        y_text = 10
        canvas.delete("controls")
        canvas.delete("params")
        if width_params==0 and width_controls==0:
            canvas.delete("params_button")
            canvas.delete("controls_button")
            for name, value in globals().items():
                if name.endswith(("_button", "_button_up", "_button_down")):
                    globals()[name] = None
            return 

        i_param=-1
        i_control=-1 
        y_pos_control=0 
        for i, line in enumerate(lines):
            key = line.split()[0]
            font_to_use = normal_font
            fill = fill_color

            if i == selected_index:
                i_param=i_param+1
                fill = "red"
                item= canvas.create_text(
                    x_text +  width_controls + width,
                    y_text + i_param * 2.3 * font_size,
                    anchor="nw",
                    fill=fill,
                    font=font_to_use,
                    tags="params",
                    text=line,
                )
                create_canvas_tooltip(canvas, item, globals()[key.upper() + "_DOC"])
            elif "[" in line:
                i_control=i_control+1
                # fill = "yellow"
                # canvas.create_text(
                #     8 * x_text,
                #     2 * y_text + i_control * 2.1 * 2 * font_size,
                #     anchor="nw",
                #     fill=fill,
                #     font=font_to_use,
                #     tags="controls",
                #     text=line.split(":", 1)[1].strip(),
                # )
            elif not "[" in line:    
                i_param=i_param+1               
                item = canvas.create_text(
                    x_text  +  width_controls + width,
                    y_text + i_param * 2.3 * font_size,
                    anchor="nw",
                    fill=fill_color,
                    font=font_to_use,
                    tags="params",
                    text=line,
                )
                create_canvas_tooltip(canvas, item, globals()[key.upper() + "_DOC"])
            y_pos_control = y_text + i_control * 2.1 * 2 * font_size
            y_pos_param = y_text + i_param * 2.3 * font_size
            
            
            if fullRefreshControls:         
                first_colon_index = line.find(":") + 1 
                f = font.Font(font=font_to_use)
                x_offset = 0
                if "[" in line:
                    key = line.split()[0]
                    btn_font = (font_type, font_size*2)
                    btn_width = 2
                    btn_height = 1
                    highlight_color = "black"
                    highlight_thickness = 2

                    name_button = key + "_button"
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
                if "[" not in line:
                    highlight_color = "black"
                    highlight_thickness = 1                    
                    name_button_up=key+"_button_up"
                    name_button_down=key+"_button_down"
                    globals()[name_button_up]
                    globals()[name_button_down]
                    lbl_left = tk.Label(canvas, text="<", fg="black", bg="white", font=font_to_use , highlightbackground=highlight_color, highlightthickness=highlight_thickness)
                    lbl_left.bind("<Enter>", lambda e, w=lbl_left, t=f"{globals()[key.upper() + "_DOC"]}": show_tip(w, t, e))
                    lbl_left.bind("<Leave>", hide_tip)                                    
                    if globals()[name_button_down] is None: 
                        globals()[name_button_down] = canvas.create_window(x_text + x_offset + 1 + width_controls + width, y_pos_param, anchor="nw", window=lbl_left, tags=("params_button",))
                    else:
                        canvas.coords(globals()[name_button_down], x_text + x_offset + 1 + width_controls + width, y_pos_param)
                    lbl_right = tk.Label(canvas, text=">", fg="black", bg="white", font=font_to_use , highlightbackground=highlight_color, highlightthickness=highlight_thickness)
                    lbl_right.bind("<ButtonPress-1>", lambda e, l=line: start_repeat(l, "Right"))
                    lbl_right.bind("<ButtonRelease-1>", lambda e: stop_repeat()) 
                    if globals()[name_button_up] is None: 
                        globals()[name_button_up] = canvas.create_window(x_text + x_offset + 18 + width_controls + width, y_pos_param, anchor="nw", window=lbl_right, tags=("params_button",))
                    else:
                        canvas.coords(globals()[name_button_up], x_text + x_offset + 18 + width_controls + width, y_pos_param)
        param_name = param_order[selected_index]   
        doc_text = param_docs.get(param_name, "") + " ("+display_range(param_name.upper())+")"
        if doc_text:
            return
            canvas.create_text(
                x_text + width_controls + width,
                height,
                anchor="sw",
                fill=fill_color,
                font=italic_font,
                tags="params",
                text=param_name + " : " + doc_text,
                width=width_params - 2 * x_text
            )

    def draw_rectangle():
        global width_params, width_controls
        if not is_maximized():
            global width_before_maximized
            global heigth_before_maximized  
            width_before_maximized=width 
            heigth_before_maximized=height         
        canvas.delete("boundary")
        canvas.create_rectangle(
            width_controls, 0, width_controls + width, height,
            outline=fill_color, width=margin,
            tags="boundary"
        )

    def generate_points_and_facultative_move(with_move, translate):
        global velocities
        global new_velocities
        global hidden
        if not birds: 
            velocities = []
            for _ in range(num_birds):
                px = random.randint(margin + width_controls, width - margin + width_controls)
                py = random.randint(margin, height - margin)
                birds.append((px, py))
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(0, max_speed)
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
                if width_controls + margin <= x <= width_controls + width - margin and 0 + margin <= y <= height - margin:
                    inside_points.append((x, y))
                    inside_velocities.append((vx, vy))
            birds[:] = inside_points
            velocities[:] = inside_velocities
            new_velocities = []
            current_count = len(birds)
            
            # Add birds if not enough
            if num_birds > current_count:
                for _ in range(num_birds - current_count):
                    px = random.randint(margin + width_controls, width - margin + width_controls)
                    py = random.randint(margin, height - margin)
                    birds.append((px, py))

                    angle = random.uniform(0, 2 * math.pi)
                    speed = random.uniform(0, max_speed)
                    vx = speed * math.cos(angle)
                    vy = speed * math.sin(angle)
                    velocities.append((vx, vy))

            # Delete birds if not enough
            elif num_birds < current_count:
                for _ in range(current_count - num_birds):
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
            if neighbor_radius > 0 and not (sep_weight == 0 and align_weight == 0 and coh_weight == 0):
                for j, (x2, y2) in enumerate(birds):
                    if i == j:
                        continue
                    dist = math.sqrt((x2 - x)**2 + (y2 - y)**2)
                    if dist < neighbor_radius and dist > 0:
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

                vx += sep_weight * move_sep_x + align_weight * move_align_x + coh_weight * move_coh_x
                vy += sep_weight * move_sep_y + align_weight * move_align_y + coh_weight * move_coh_y
      
            #RANDOM
            speed = math.sqrt(vx**2 + vy**2)
            if random_speed!=0:
                target_speed = max_speed / 2
                sigma_percent = random_speed       # écart-type maximal en % de vmax
                adjust_strength = 0.05    # rappel vers target_speed
                sigma_base = (sigma_percent / 100) * max_speed
                weight = 4 * speed * (max_speed - speed) / (max_speed ** 2)
                sigma = sigma_base * weight
                delta_speed = random.gauss(0, sigma)
                new_speed = speed + delta_speed
                new_speed += (target_speed - new_speed) * adjust_strength
                new_speed = max(0.1, min(max_speed, new_speed))
                factor = new_speed / speed
                vx *= factor
                vy *= factor
            if random_angle!=0:
                angle = math.atan2(vy, vx)
                angle += math.radians(random.uniform(-1 * random_angle, random_angle))
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
            while nx < margin + width_controls or nx > width - margin + width_controls:
                if nx < margin + width_controls:
                    overshoot = (margin + width_controls) - nx
                    nx = (margin + width_controls) + overshoot
                    vx = abs(vx)
                elif nx > width - margin + width_controls:
                    overshoot = nx - (width - margin + width_controls)
                    nx = (width - margin + width_controls) - overshoot
                    vx = -abs(vx)
            while ny < margin or ny > height - margin:
                if ny < margin:
                    overshoot = margin - ny
                    ny = margin + overshoot
                    vy = abs(vy)
                elif ny > height - margin:
                    overshoot = ny - (height - margin)
                    ny = (height - margin) - overshoot
                    vy = -abs(vy)
            idx = birds.index((x, y))
            velocities[idx] = (vx, vy)
            new_points.append((nx, ny))
        birds[:] = new_points


    def draw_points():
        for pid in point_ids:
            canvas.delete(pid)
        point_ids.clear()

        triangle_size = 6*size
        triangle_width = 4*size

        for (x, y), (vx, vy) in zip(birds, velocities):
            if not triangles: 
                pid = canvas.create_oval(
                    x - size, y - size,
                    x + size, y + size,
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
        if speed > max_speed:
            vx = (vx / speed) * max_speed
            vy = (vy / speed) * max_speed
        return vx, vy

    def frame():
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

        root.after(refresh_ms, update)

    def signal_handler(sig, frame):
        print("Interrupted! Closing application...")
        root.destroy() 
        sys.exit(0)

    def create_canvas_tooltip(canvas, item, text):
        tip_window = None

        def show_tip(event):
            global tip_window

            # 1. Détruire l'ancien tooltip s'il existe
            if tip_window is not None:
                try:
                    tip_window.destroy()
                except:
                    pass
                tip_window = None

            # 2. Si pas de texte, on arrête ici
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
                font=(font_type, font_size)
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

        # 1. Détruire l'ancien tooltip s'il existe
        if tip_window is not None:
            try:
                tip_window.destroy()
            except:
                pass
            tip_window = None

        # 2. Si pas de texte, on arrête ici
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
            font=(font_type, font_size) 
        )
        label.pack()

    def hide_tip(event=None):
        global tip_window
        if tip_window:
            tip_window.destroy()
            tip_window = None

            
    def rustine_1():
        root.geometry(f"{width_params + width +1+ width_controls}x{max(height, HEIGHT_PARAMS_CONTROLS_DEFAULT)}")
    def rustine_2():
        root.geometry(f"{width_params + width +3+ width_controls}x{max(height, HEIGHT_PARAMS_CONTROLS_DEFAULT)}")

    global root, canvas


    root = tk.Tk()
    root.title(f"pybirdsreynolds - {version_prog}")
    root.minsize(width_params+ WIDTH_MIN+width_controls, max(height,HEIGHT_PARAMS_CONTROLS_DEFAULT))
    canvas = tk.Canvas(root, width=width_params+width+width_controls, height=height, bg=canvas_bg)
    canvas.pack(fill="both", expand=True)

    global font_type, font_type, fonts
    default_fonts = [f for f in FONT_TYPE_LIST if f in font.families()] 
    available_fonts = font.families()
    mono_fonts = [f for f in available_fonts if "mono" in f.lower()]

    fonts = []
    for f in default_fonts + mono_fonts:
        if f not in fonts:
            fonts.append(f)

    if font_type not in fonts:
        font_type = fonts[0]  
        
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


