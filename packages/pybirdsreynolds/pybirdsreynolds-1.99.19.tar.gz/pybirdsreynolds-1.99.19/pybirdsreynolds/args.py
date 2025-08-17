import argparse
import sys
import textwrap
from pybirdsreynolds.const import *

def display_range(prefix):
    g = globals()
    value_default   = g[f"{prefix}_DEFAULT"]
    if type(value_default) is int:
        value_min       = g[f"{prefix}_MIN"]
        value_max       = g[f"{prefix}_MAX"]
        value_free_min  = g[f"{prefix}_FREE_MIN"]
        value_free_max  = g[f"{prefix}_FREE_MAX"]
        parts = []
        
        if value_min is not None and value_max is not None:
            parts.append(f"between {value_min} and {value_max}")
        elif value_min is not None:
            parts.append(f">= {value_min}")
        elif value_max is not None:
            parts.append(f"<= {value_max}")
        else:   
            parts.append(f"with no limit")

        if value_free_min is not None and value_free_max is not None:
            parts.append(f"if --free between {value_free_min} and {value_free_max}")
        elif value_free_min is not None:
            parts.append(f"if --free >= {value_free_min}")
        elif value_free_max is not None:
            parts.append(f"if --free <= {value_free_max}")
        else:   
            parts.append(f"if --free with no limit")

        if value_default is not None:
            parts.append(f"default: {value_default}")
        
        return f"{' , '.join(parts)}" if parts else ""
    elif isinstance(value_default, bool):
        return "boolean value"
    else:
        return "string value"


def check_values(prefix , free , value , my_parser):
    g = globals()
    value_default   = g[f"{prefix}_DEFAULT"]
    value_min       = g[f"{prefix}_MIN"]
    value_max       = g[f"{prefix}_MAX"]
    value_free_min  = g[f"{prefix}_FREE_MIN"]
    value_free_max  = g[f"{prefix}_FREE_MAX"]  
    if not free:  
        if (value_min is not None and value_max is not None) and (value < value_min or value > value_max):
            my_parser.error(f"{prefix.lower()} must be between {value_min} and {value_max}")
        elif (value_min is None and value_max is not None) and (value > value_max):
            my_parser.error(f"{prefix.lower()} must <= {value_max}")
        elif (value_min is not None and value_max is None) and (value < value_min):
            my_parser.error(f"{prefix.lower()} must >= {value_min}") 
    else:
        if (value_free_min is not None and value_free_max is not None) and (value < value_free_min or value > value_free_max):
            my_parser.error(f"{prefix.lower()} must be between {value_free_min} and {value_free_max}")
        elif (value_free_min is None and value_free_max is not None) and (value > value_free_max):
            my_parser.error(f"{prefix.lower()} must <= {value_free_max}")
        elif (value_free_min is not None and value_free_max is None) and (value < value_free_min):
            my_parser.error(f"{prefix.lower()} must >= {value_free_min}")

def compute_args():
    controls_text = "\n".join(
        f"  {globals()[name]} [{globals()[name.replace('_TEXT', '_COMMAND')]}]"
        for name in globals()
        if name.endswith("_TEXT")
    )

    my_parser = argparse.ArgumentParser(
        description=textwrap.dedent(f"""\
This project is an interactive simulation of the Reynolds Boids model, implemented in Python with Tkinter. It allows you to visualize and experiment with the collective behavior of a flock of virtual birds by adjusting parameters such as cohesion, alignment, separation, speed, and neighborhood radius in real time. The interface also provides several controls (pause, reset, new generation, FPS display, etc.) to easily explore the dynamics of the system.

Controls:
{controls_text}

Thanks to Mehdi Moussaïd - http://www.mehdimoussaid.com/a-propos/ - https://youtu.be/xuKrkOh_mzk
        """),
        epilog=textwrap.dedent("""\
            Full documentation:  https://github.com/thib1984/pybirdsreynolds
            Report bugs:         https://github.com/thib1984/pybirdsreynolds/issues

            License: MIT
            Copyright (c) 2025 thib1984

            This is free software: you can modify and redistribute it.
            There is NO WARRANTY, to the extent permitted by law.
            Written by thib1984.
        """),
        formatter_class=argparse.RawTextHelpFormatter
    )   


    g = globals()

    for name, doc in g.items():
        if not name.endswith("_DOC"):
            continue

        prefix = name[:-4]
        default_name = f"{prefix}_DEFAULT"
        if default_name not in g:
            continue 

        default_value = g[default_name]
        arg_name = "--" + prefix.lower()
        if isinstance(default_value, bool):
            my_parser.add_argument(
                arg_name,
                action="store_true",
                default=default_value,
                help=g[name] + " (" +display_range(prefix) + ")"
            )
        elif isinstance(default_value, int):
            my_parser.add_argument(
                arg_name,
                type=int,
                default=default_value,
                help=g[name] + " (" +display_range(prefix) + ")"
            )
        elif isinstance(default_value, str):
            my_parser.add_argument(
                arg_name,
                type=str,
                default=default_value,
                help=g[name]
            )
    args = my_parser.parse_args()

    for name, doc in g.items():
        if not name.endswith("_DOC"):
            continue

        prefix = name[:-4]
        default_name = f"{prefix}_DEFAULT"
        if default_name not in g:
            continue

        default_value = g[default_name]
        if not isinstance(default_value, int) or isinstance(default_value, bool):
            continue  # on saute les booléens
        
        # Ici on suppose que les noms d'arguments sont en minuscules
        arg_value = getattr(args, prefix.lower(), None)
        check_values(prefix, args.free, arg_value, my_parser )   

    
    return args


