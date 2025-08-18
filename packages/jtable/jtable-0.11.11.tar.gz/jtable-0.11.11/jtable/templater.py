#!/usr/bin/env python3
import sys, json, re, os, ast, inspect, datetime, time, logging, logging.config, html, shutil, platform
from os import isatty
from sys import exit
from typing import Any, Dict, Optional

# Import required modules
import functions
Filters = functions
Plugin = functions.Plugin
running_context = functions.running_context()


class Templater:
    """
    A Jinja2 template renderer with custom filters and plugins.
    
    This class provides template rendering functionality with built-in support
    for jtable filters and plugins.
    """
    def __init__(self, template_string = "", static_context = {}, strict_undefined = True, to_table_filter=None):
        from jinja2 import Environment
        env = Environment()
        self.strict_undefined = strict_undefined
        import random
        self.id = random.randint(0,1000000)

        # Add jtable core filters
        jtable_core_filters = [name[0] for name in inspect.getmembers(Filters, predicate=inspect.isfunction)]
        for filter_name in jtable_core_filters:
            env.filters[filter_name] = getattr(Filters, filter_name)
        
        # Add to_table filter if provided
        if to_table_filter:
            env.filters['to_table'] = to_table_filter
        
        # logging.info(f"jtable_core_filters: {jtable_core_filters}")

        ####################  Add plugin function ####################
        jtable_core_plugins = [name[0] for name in inspect.getmembers(Plugin, predicate=inspect.isfunction)]
        logging.info(f"jtable_core_plugins: {jtable_core_plugins}")
        
        class plugin_fct(object):
            def process_plugin(self,*args, **kwargs):
                if len(args) == 0 and len(kwargs) == 0:
                    logging.error("plugin function must have at least one argument in:")
                    exit(3)
                if args[0] not in jtable_core_plugins:
                    logging.error(f"plugin function {args[0]} not found in {', '.join(jtable_core_plugins)}")
                    exit(3)
                method_to_call = getattr(Plugin, args[0], None)
                try:
                    res = method_to_call(*args[1:],**kwargs)
                except Exception as error:
                    logging.error(f"Failed to call plugin function {args[0]}, error was:\n  {str(error)}")
                    exit(3)
                return res
            
        plugin = lambda: plugin_fct().process_plugin
        logging.debug(f"({self.id}) strict_undefined: {strict_undefined}, static_context: {static_context}")
        static_context = {**static_context, **{"plugin": plugin()}}

        ##############################################################
        logging.info(f"({self.id}) compiling template_string: {template_string}")
        logging.info(f"({self.id}) template_string type  {type(template_string)}")
        try:
            self.template = env.from_string(template_string, globals=static_context)
        except Exception as error:
            logging.error(f"({self.id}) Failed to compile template, error was:\n  {str(error)}")
            exit(3)
    
    def render(self, vars, eval_str = False):
        """
        Render the template with the given variables.
        
        Args:
            vars: Variables to pass to the template
            eval_str (bool): Whether to evaluate the output as a Python expression
            
        Returns:
            The rendered template output
        """
        logging.debug(f"({self.id}) Rendering template, self.strict_undefined: {self.strict_undefined}, vars: {vars}")
        
        try:
            out_str = self.template.render(vars)
        except Exception as error:
            if str(error)[0:30] == "'dict object' has no attribute" \
                or str(error)[0:30] == "'list object' has no attribute"\
                or str(error).__contains__("is undefined"):
                    if self.strict_undefined == True:
                        logging.error(f"({self.id}) Failed while rendering context, error was:\n  {str(error)}")
                        logging.error(f"({self.id}) debug strict_undefined: {self.strict_undefined}")
                        logging.error(f"({self.id}) debug vars: {vars}")
                        raise error
                        # out = out_str =""
                    else:
                        out = out_str =""
            else:
                out = out_str = error
                logging.error(f"Failed while rendering context, error was:\n  {str(error)}")
                raise out
                # out = out_str =""
            
        if eval_str == True:
            try:
                expr = ast.parse(out_str, mode='eval').body
                expr_type = expr.__class__.__name__
                if expr_type == 'List' or expr_type == 'Dict':
                    out =  ast.literal_eval(out_str)
                elif expr_type == 'Name':
                    out = out_str
                else:
                    out = str(out_str)
            except:
                out = out_str
        else:
            out = out_str
                    
        return out
