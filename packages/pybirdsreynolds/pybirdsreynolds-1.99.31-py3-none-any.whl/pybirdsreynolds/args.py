# args.py
import argparse
import textwrap
import importlib
import pybirdsreynolds.const as const

def get_description() -> str:
    return importlib.resources.files("pybirdsreynolds").joinpath("DESCRIPTION.txt").read_text(encoding="utf-8").strip()

def get_epilog() -> str:
    return importlib.resources.files("pybirdsreynolds").joinpath("EPILOG.txt").read_text(encoding="utf-8").strip()

def display_range(prefix):
    value_default = getattr(const, f"{prefix}_DEFAULT")
    if not isinstance(value_default, bool) and isinstance(value_default, bool):
        value_min      = getattr(const, f"{prefix}_MIN")
        value_max      = getattr(const, f"{prefix}_MAX")
        value_free_min = getattr(const, f"{prefix}_FREE_MIN")
        value_free_max = getattr(const, f"{prefix}_FREE_MAX")
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

def check_values(prefix, free, value, parser):
    value_default   = getattr(const, f"{prefix}_DEFAULT")
    value_min       = getattr(const, f"{prefix}_MIN")
    value_max       = getattr(const, f"{prefix}_MAX")
    value_free_min  = getattr(const, f"{prefix}_FREE_MIN")
    value_free_max  = getattr(const, f"{prefix}_FREE_MAX")

    if not free:
        if value_min is not None and value_max is not None and (value < value_min or value > value_max):
            parser.error(f"{prefix.lower()} must be between {value_min} and {value_max}")
        elif value_min is None and value_max is not None and value > value_max:
            parser.error(f"{prefix.lower()} must <= {value_max}")
        elif value_min is not None and value_max is None and value < value_min:
            parser.error(f"{prefix.lower()} must >= {value_min}")
    else:
        if value_free_min is not None and value_free_max is not None and (value < value_free_min or value > value_free_max):
            parser.error(f"{prefix.lower()} must be between {value_free_min} and {value_free_max}")
        elif value_free_min is None and value_free_max is not None and value > value_free_max:
            parser.error(f"{prefix.lower()} must <= {value_free_max}")
        elif value_free_min is not None and value_free_max is None and value < value_free_min:
            parser.error(f"{prefix.lower()} must >= {value_free_min}")

def create_parser():
    controls_text = "\n".join(
        f"  {getattr(const, name)} [{getattr(const, name.replace('_TEXT', '_COMMAND'))}]"
        for name in dir(const)
        if name.endswith("_TEXT") and getattr(const, f"{name[:-5]}_HIDEN") < 2
    )

    parser = argparse.ArgumentParser(
        description=get_description() + "\n\n" + f"controls:\n{controls_text}",
        epilog=get_epilog(),
        formatter_class=argparse.RawTextHelpFormatter
    )

    for name in dir(const):
        if not name.endswith("_DOC"):
            continue

        prefix = name[:-4]
        hide = getattr(const, f"{prefix}_HIDEN")
        if hide == 2:
            continue

        default_name = f"{prefix}_DEFAULT"
        if not hasattr(const, default_name):
            continue

        default_value = getattr(const, default_name)
        arg_name = "--" + prefix.lower()
        if isinstance(default_value, bool):
            parser.add_argument(
                arg_name,
                action="store_true",
                default=default_value,
                help=getattr(const, name) + " (" + display_range(prefix) + ")"
            )
        elif isinstance(default_value, int):
            parser.add_argument(
                arg_name,
                type=int,
                default=default_value,
                help=getattr(const, name) + " (" + display_range(prefix) + ")"
            )
        elif isinstance(default_value, str):
            parser.add_argument(arg_name, type=str, default=default_value,
                                help=g[name])
    return parser

def compute_args():
    parser = create_parser()
    args = parser.parse_args()

    import pybirdsreynolds.const as const

    for name in dir(const):
        if not name.endswith("_DOC"):
            continue

        prefix = name[:-4]
        hide = getattr(const, f"{prefix}_HIDEN")
        if hide == 2:
            continue

        default_name = f"{prefix}_DEFAULT"
        if not hasattr(const, default_name):
            continue

        default_value = getattr(const, default_name)
        if not isinstance(default_value, int) or isinstance(default_value, bool):
            continue
        
        arg_value = getattr(args, prefix.lower(), None)
        check_values(prefix, args.free, arg_value, parser )   

    
    return args

def get_help_text():
    parser = create_parser()
    return parser.format_help()
