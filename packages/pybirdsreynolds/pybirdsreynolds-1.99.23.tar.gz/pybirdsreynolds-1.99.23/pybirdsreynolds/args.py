import argparse
import sys
import textwrap
from pybirdsreynolds.const import *
from pathlib import Path
import re
import importlib

def get_description() -> str:
    return importlib.resources.files("pybirdsreynolds").joinpath("DESCRIPTION.txt").read_text(encoding="utf-8").strip()

def get_epilog() -> str:
    return importlib.resources.files("pybirdsreynolds").joinpath("EPILOG.txt").read_text(encoding="utf-8").strip()


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
        description = get_description() + "\n\n" + textwrap.dedent(f"""\
controls:
{controls_text}
        """),
        epilog=get_epilog(),
        formatter_class=argparse.RawTextHelpFormatter
    )   


    g = globals()

    for name, doc in g.items():
        if not name.endswith("_DOC"):
            continue

        prefix = name[:-4]
        hide =g[f"{prefix}_HIDEN"]
        if hide == 2:
            continue 
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
        hide =g[f"{prefix}_HIDEN"]
        if hide == 2:
            continue         
        default_name = f"{prefix}_DEFAULT"
        if default_name not in g:
            continue

        default_value = g[default_name]
        if not isinstance(default_value, int) or isinstance(default_value, bool):
            continue
        
        arg_value = getattr(args, prefix.lower(), None)
        check_values(prefix, args.free, arg_value, my_parser )   

    
    return args


