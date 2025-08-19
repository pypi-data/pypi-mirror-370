import sys
import os
def current_dir_sys_path():
    sys.path.append(os.getcwd())  #current_dir_sys_path()

import importlib
def instantiate_config(config):
    if not "target" in config:
        if config == '__is_first_stage__':
            return None
        elif config == "__is_unconditional__":
            return None
        raise KeyError("Expected key `target` to instantiate.")
    return get_obj_from_str(config["target"])(**config.get("params", dict()))
def get_obj_from_str(string, reload=False):
    module, cls = string.rsplit(".", 1)
    if reload:
        module_imp = importlib.import_module(module)
        importlib.reload(module_imp)
    return getattr(importlib.import_module(module, package=None), cls)


import argparse
from omegaconf import OmegaConf
 
def get_parser(**parser_kwargs):
 
    parser = argparse.ArgumentParser()
    
    # Dynamically add arguments based on kwargs
    for arg_name, arg_data in parser_kwargs.items():
        parser.add_argument(
            f"--{arg_name.strip('-')}",  # Ensure the argument starts with '--'
            type=str,
            const=True,
            default=""  if len(arg_data) < 0 else arg_data ,
            nargs="?",
            help="" or "No description provided.",
        )   
    return parser
if __name__ == "__main__":
    # Create the parser with dynamic arguments
    parser = get_parser(
        base="address file*.yaml",
        gpus="",
 
    )    
    opt, unknown = parser.parse_known_args()
    config = OmegaConf.load(opt.base) 
    for key, value in vars(opt).items():
        print(f"{key}: {value}")
    print(unknown)
    model = instantiate_config(config.model)


