#!/usr/bin/env python3
import sys, json, re, os, inspect, logging, logging.config, shutil
from os import isatty
from sys import exit
from typing import Any, Dict, Optional
# import filters as Filters

jtable_path = os.path.dirname(os.path.abspath(__file__))

if jtable_path not in sys.path:
    sys.path.insert(0, jtable_path)
from logger import CustomFormatter, CustomFilter, _ExcludeErrorsFilter, logging_config

import version
import tabulate
import yaml

import functions

# Import ToTable and path_auto_discover from the new module
import to_table
ToTable = to_table.ToTable
path_auto_discover = to_table.path_auto_discover
Styling = to_table.Styling

Filters = functions
Plugin = functions.Plugin
InspectDataset = functions.InspectDataset
running_context = functions.running_context()

# Import Templater from the new module
import templater
Templater = templater.Templater

def create_templater(*args, **kwargs):
    """Helper function to create Templater instances with to_table filter"""
    to_table_filter = to_table.ToTable().render_object
    return Templater(*args, to_table_filter=to_table_filter, **kwargs)

def stdin_has_data():
    """Retourne True si des données sont envoyées sur stdin (ex: via pipe ou redirection)"""
    return not sys.stdin.isatty()

class JtableCli:
    def __init__(self):
        self.path = ""
        self.dataset = {}
        
    def play_task_file(self, query_file_path):
        """Load and process a query file (YAML format)"""
        logging.info(f"loading query file: {query_file_path}")
        with open(query_file_path, 'r') as file:
            try:
                query_file = yaml.safe_load(file)
            except Exception as error:
                logging.error(f"Fail to load query file {query_file_path}, check Yaml format")
                logging.error(f"error was:\n{error}")
                exit(2)
        return query_file
        
    def parse_args(self):

        select = []
        queryset = {}
        self.tabulate_var_name="stdin"
        if 'JTABLE_RENDER' in os.environ:
            render=os.environ['JTABLE_RENDER']
        else:
            render="jinja_native"

        import argparse

        parser = argparse.ArgumentParser(
            prog='jtable',
            description='Tabulate your JSON/Yaml data and transform it using Jinja',
            add_help=False)

        subparsers = parser.add_subparsers(dest='command')
        # load_parser = subparsers.add_parser('load')
        load_parser = argparse.ArgumentParser(add_help=False)

        # load_parser.add_argument("-h", "--help",nargs="*", help = "Show this help")
        load_parser.add_argument("-p", "--json_path", help = "json path")
        load_parser.add_argument("-s", "--select", help = "select key_1,key_2,...")
        load_parser.add_argument("-w", "--when", help = "key_1 == 'value'")
        load_parser.add_argument("-f", "--format", help = "Table format applied in simple,json,th,td... list below")
        load_parser.add_argument("-us", "--unselect", help = "Unselect unwanted key_1,key_2,...")
        load_parser.add_argument("--inspect", action="store_true", help="Inspect stdin")
        load_parser.add_argument("-vq", "--view_query", action="store_true", help = "View query")
        parser.add_argument('--version', action='version', version=version.__version__)
        load_parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level')
        load_parser.add_argument('-d', '--debug', action="store_true", help='Add code row number in log')
        load_parser.add_argument('-pf', '--post_filter', help='Additionnal filter to apply on stdout, eg: jtable ..-f json -pf "from_json | to_nice_yaml"')
        load_parser.add_argument('-c', '--context', help='Add context')
        load_parser.add_argument('-pl', '--play', help='Execute a query file (YAML)')
        load_parser.add_argument('-lv', '--load_os_vars', action="store_true", help='Load OS environment variables into vars context')
        # load_parser.add_argument('file', nargs='?', help='Path to JSON file (or piped via stdin)')
        # args = parser.parse_args()
        global terminal_size
        terminal_size = shutil.get_terminal_size((80, 20))  # Largeur par défaut 80, hauteur 20

        # parse_known_args = load_parser.parse_known_args()[0]
        # print(parse_known_args)

        load_json_parser = subparsers.add_parser(
        'load_json', parents=[load_parser], help='Load JSON dataset'
        )

        load_yaml_parser = subparsers.add_parser(
        'load_yaml', parents=[load_parser], help='Load YAML dataset'
        )

        load_json_files_parser = subparsers.add_parser(
        'load_json_files', parents=[load_parser], help='Load multiple JSON files'
        )

        load_yaml_files_parser = subparsers.add_parser(
        'load_yaml_files', parents=[load_parser], help='Load multiple YAML files'
        )

        play_parser = subparsers.add_parser(
        'play', parents=[load_parser], help='Execute a query file (YAML)'
        )

        template_parser = subparsers.add_parser(
        'template',  help='Process template with optional environment variables'
        )
        
        # Add debug options to template_parser
        template_parser.add_argument('-v', '--verbose', action='count', default=0, help='Verbosity level')
        template_parser.add_argument('-d', '--debug', action="store_true", help='Add code row number in log')
        template_parser.add_argument('-c', '--context', help='Add context')
        template_parser.add_argument('-lv', '--load_os_vars', action="store_true", help='Load OS environment variables into vars context')

        load_json_parser.add_argument('file', nargs='?', help='Path to JSON file (or piped via stdin)')
        load_yaml_parser.add_argument('file', nargs='?', help='Path to YAML file (or piped via stdin)')
        load_json_files_parser.add_argument('files', nargs='+', help='File patterns for JSON files (e.g., "folder/*/*.json" or "{var_name}:folder/*/*.json")')
        load_yaml_files_parser.add_argument('files', nargs='+', help='File patterns for YAML files (e.g., "folder/*/*.yml" or "{var_name}:folder/*/*.yml")')
        play_parser.add_argument('query_file', help='Path to query file (YAML)')
        template_parser.add_argument('string', help='Free template string to process')
        # exit(0)

        # Check for --version first
        if len(sys.argv) > 1 and '--version' in sys.argv:
            args = parser.parse_args()
            return
            
        # Check for help requests
        help_requested = '--help' in sys.argv or '-h' in sys.argv
        
        if len(sys.argv) > 1 and sys.argv[1] in {'load_json','load_yaml','load_json_files','load_yaml_files','play','template'}:
            # Commande explicite → on parse normalement
            args = parser.parse_args()
        elif stdin_has_data():
            # Pas de commande explicite mais stdin actif → injecter "load_json" avant les arguments
            sys.argv.insert(1, 'load_json')
            args = parser.parse_args()
        else:
            # Pas de commande explicite et pas de stdin → afficher aide
            parser.print_help()
            sys.exit(1)

        # print(args.debug)
        # exit(0)

        if os.environ.get('JTABLE_LOGGING') == "DEBUG" or args.debug:
            logging_config['formatters']['my_formatter']['format'] = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)-16s | %(levelname)s %(message)s'
        else:
            logging_config['formatters']['my_formatter']['format'] = '%(asctime)s %(class_name)s.%(parent_function)-15s | %(levelname)s %(message)s'

        
        if args.verbose == 0:
            logging_config['handlers']['console_stderr']['level'] = 'WARNING'
        if args.verbose == 1:
            logging_config['handlers']['console_stderr']['level'] = 'INFO'
        elif args.verbose == 2:
            logging_config['handlers']['console_stderr']['level'] = 'DEBUG'
        logging.config.dictConfig(logging_config)
        logging.info(f"running_context: {running_context}")
        # logging_format = '%(asctime)s (%(lineno)s) %(class_name)s.%(parent_function)s | %(levelname)s %(message)s'
        
        if args.context:
            print(f"Loading context from: {args.context}")
            logging.info(f"Loading context from: {args.context}")
            queryset = json.loads(args.context)
            print(f"queryset: {queryset}")
            exit(0)
            
        # Handle --play option for load commands
        if hasattr(args, 'play') and args.play:
            query_file = self.play_task_file(args.play)



                
        is_pipe = not isatty(sys.stdin.fileno())

        stdin=""
        if is_pipe:
            logging.info("stdin is a pipe")
            for line in sys.stdin:
                stdin = stdin + line
            self.dataset = { self.tabulate_var_name: stdin }
        load_parser_commands = {'load_json', 'load_yaml', 'load_json_files', 'load_yaml_files', 'play'}
        should_show_detailed_help = (not is_pipe and not args.command) or (help_requested and args.command in load_parser_commands)
        
        if should_show_detailed_help:
            if args.command:
                # For specific commands, print their help first
                parser.print_help(sys.stdout)
            else:
                # For general help, print main parser help
                parser.print_help(sys.stdout)
            
            jtable_core_filters = [name for name, func in inspect.getmembers(Filters, predicate=inspect.isfunction)]
            jtable_plugins = [name for name, func in inspect.getmembers(Plugin, predicate=inspect.isfunction)]
            print(f"\njtable core filters:\n   {', '.join(jtable_core_filters)}\n")
            tablulate_formats = next((value for name, value in inspect.getmembers(tabulate) if name == 'tabulate_formats'), None)
            jtable_formats = ['json','gitlab_json_table','td','th']
            print(f"tabulate formats:\n   {', '.join(sorted(tablulate_formats))}\n")
            print(f"jtable additional formats:\n   {', '.join(sorted(jtable_formats))}\n")
            print(f"jtable plugins:\n   {', '.join(jtable_plugins)}\n")
            print(f"More help with jtable -h <help topic>")
            print(f"  colors:\n    type jtable -h color | jtable\n")
            exit(1)


        def load_multiple_inputs(file_search_string,format):
            logging.info(f"loading {format} files: {file_search_string}")
            err_help = f"\n[ERROR] {format}_files must looks like this:\n\n\
                jtable load_{format}_files \"{{target_var_name}}:folder_1/*/*/config.{format}\"\n"
            got_variable_name_pattern = r'^\{[a-zA-Z_1-9]+\}:.*'
            if re.match(got_variable_name_pattern, file_search_string):
                logging.info(f"Contains variable name file_names: {file_search_string}")
                splitted_path = file_search_string[1:].split('}:')
                path=splitted_path[1]
                self.tabulate_var_name = splitted_path[0]
            else:
                self.tabulate_var_name = "input_1"
                logging.info(f"Adding var_name: {self.tabulate_var_name}")
                path = file_search_string
            logging.info(f"var_name: {self.tabulate_var_name}, path: {path}")
            logging.info(f"path: {path}")
            if running_context['shell_family'] == "windows":
                cmd = f"dir /s /b {path}"
                logging.info(f"cmd: {cmd}")
                files_str = os.popen("dir /s /b " + path).read()
            else:
                files_str = os.popen("ls -1 " + path).read()
            files_str = os.popen("ls -1 " + path).read()
            logging.info(f"files_str: {files_str}")
            file_list_dataset = []
            for file_name_full_path in files_str.split('\n'):
                if file_name_full_path != '':
                    with open(file_name_full_path, 'r') as input_file:
                        try:
                            if format == 'json':
                                file_content = json.load(input_file)
                            else:
                                file_content = yaml.safe_load(input_file)
                            if running_context['shell_family'] == "windows":
                                sep = "\\"
                                file_path = sep.join(file_name_full_path.split('\\')[:-1])
                                file_name = file_name_full_path.split('\\')[-1]
                            else:
                                file_path = "/".join(file_name_full_path.split('/')[:-1])
                                file_name = file_name_full_path.split('/')[-1]
                            file = { 
                                    "name": file_name,
                                    "path": file_path,
                                    "content": file_content
                                    }
                            file_list_dataset = file_list_dataset + [{ **file }]
                        except Exception as error:
                            logging.warning(f"fail loading file {file_name_full_path}, skipping")
            self.dataset = {**self.dataset, **{ self.tabulate_var_name: file_list_dataset } }

        if args.command == 'load_json' or args.command == 'load_yaml':
            if stdin_has_data() and not args.file:
                dict_content = stdin
            else:
                file_type = "_".join(args.command.split('_')[1:]).upper()
                if not args.file:
                    logging.error(f"No {file_type} file provided, please provide a file or pipe {file_type} content to stdin")
                    exit(1)
                logging.info(f"loading {args.command} file: {args.file}")
                self.tabulate_var_name = "input"
                file_name = args.file
                with open(file_name, 'r') as file_content:
                    try:
                        if args.command == 'load_yaml':
                            dict_content = yaml.safe_load(file_content)
                        else:
                            # Assume JSON file
                            dict_content = json.load(file_content)
                    except Exception as error:
                        logging.error(f"Failed to load {args.command} file {file_name}, error was:\n{error}")
                        logging.error(f"File path: {os.path.abspath(file_name)}")
                        logging.error(f"File exists: {os.path.exists(file_name)}")
                        if os.path.exists(file_name):
                            logging.error(f"File size: {os.path.getsize(file_name)} bytes")
                        exit(2)
                
                # Check if the loaded content is None
                if dict_content is None:
                    logging.error(f"Loaded content from {file_name} is None. Please check the file content.")
                    exit(2)
                    
            self.dataset = {**self.dataset, **{ self.tabulate_var_name: dict_content } }
        elif args.command == 'load_json_files' or args.command == 'load_yaml_files':
            file_type = "_".join(args.command.split('_')[1:]).upper()
            for file_pattern in args.files:
                load_multiple_inputs(file_pattern, file_type.lower())
        elif args.command == 'play':
            query_file = self.play_task_file(args.query_file)

        if hasattr(args, 'play') and args.play:
            query_file = self.play_task_file(args.play)


        if 'query_file' in locals() and query_file:
            if 'vars' in query_file:
                if 'queryset' in query_file['vars']:
                    queryset = query_file['vars']['queryset']

        
        if 'json_path' in args and args.json_path:
            new_path = args.json_path
            expr_end_by_braces=(re.sub('.*({).*(})$',r'\1\2',args.json_path))
            if expr_end_by_braces != "{}":
                new_path = new_path + "{}"
            queryset['path'] = new_path

        # Load OS environment variables if requested (always do this first)
        if hasattr(args, 'load_os_vars') and args.load_os_vars:
            env_vars = Plugin.load_os_vars()
            vars = env_vars
            self.dataset = {**self.dataset,**vars, **{"vars": vars}}
            logging.info(f"Loaded {len(env_vars)} environment variables into vars context")

        # Process query file if it was loaded (either from play command or other sources)
        if 'query_file' in locals() and query_file:

            if 'vars' in query_file:
                # Get existing vars (including env vars if loaded above)
                vars = self.dataset.get('vars', {})
                
                for key,value in query_file['vars'].items():
                    logging.info(f"Covering vars, key: {key}")
                    jinja_eval = create_templater(template_string=str(value), static_context=self.dataset).render({},eval_str=True)
                    vars.update({key: jinja_eval})
                    self.dataset = {**self.dataset,**vars, **{"vars": vars}}

        # print(f"debug queryset['select']: {queryset.get('select', [])}")
        # print(f"debug queryset: {queryset}")
            
        if 'select' in queryset:
            select = queryset['select']

        if hasattr(args, 'unselect') and args.unselect:
           queryset['unselect'] = args.unselect

        if hasattr(args, 'select') and args.select:
            # If queryset already has a complex select definition, filter it
            if 'select' in queryset and isinstance(queryset['select'], list):
                # Filter existing select fields by the 'as' field names
                requested_fields = args.select.split(',')
                filtered_select = [field for field in queryset['select'] 
                                 if 'as' in field and field['as'] in requested_fields]
                queryset['select'] = filtered_select
            else:
                # Simple case: no complex select in queryset
                queryset['select'] = args.select

        if 'when' in queryset and hasattr(args, 'when') and args.when:
            queryset['when'] = args.when

        if not 'path' in queryset:
            queryset['path'] = "{}"
                    
        if not "format" in queryset:
            queryset['format'] = 'simple'

        if hasattr(args, 'format') and args.format:
            queryset['format'] = args.format

        if hasattr(args, 'view_query') and args.view_query:
            original_format = queryset['format']
            queryset['format'] = "th"
            
        if args.command == 'template':
            # For template command, create a minimal query_file structure
            query_file = {'stdout': args.string}
            out_expr = args.string
        else:
            if self.tabulate_var_name == "stdin":
                if hasattr(args, 'post_filter') and args.post_filter:
                    original_out_expr = "{{ " + self.tabulate_var_name + " | from_json_or_yaml | to_table(queryset=queryset) }}"
                    out_expr = "{{ " + self.tabulate_var_name + f" | from_json_or_yaml | to_table(queryset=queryset) | {args.post_filter} }}}}"
                else:
                    out_expr = "{{ " + self.tabulate_var_name + " | from_json_or_yaml | to_table(queryset=queryset) }}"
            else:
                out_expr = "{{ " + self.tabulate_var_name + " | to_table(queryset=queryset) }}"


        if 'query_file' in locals() and query_file:
            if 'stdout' in query_file:
                out_expr = query_file['stdout']
            
        if hasattr(args, 'inspect') and args.inspect:
            if self.tabulate_var_name == "stdin":
                inspected_paths = InspectDataset().view_paths(yaml.safe_load(stdin))
            else:
                inspected_paths = InspectDataset().view_paths(self.dataset[self.tabulate_var_name])
            tbl = tabulate.tabulate(inspected_paths,['path','value'])
            print(tbl)
            return

        if hasattr(args, 'view_query') and args.view_query:
            if hasattr(args, 'post_filter') and args.post_filter:
                out = create_templater(template_string=original_out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=True)
            else:
                out = create_templater(template_string=out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=True)
            query_file_out = {}
            query_set_out = {}
            fields = out
            if select == []:
                for field in fields:
                    select = select + [ {'as': field, 'expr': field }  ]
            query_set_out['path'] = queryset['path']
            query_set_out['select'] = select
            query_set_out['format'] = original_format
            if hasattr(args, 'when') and args.when:
                query_set_out['when'] = args.when
            query_file_out['vars'] = {'queryset': query_set_out }
            query_file_out['stdout'] = out_expr



            yaml_query_out = yaml.dump(query_file_out, allow_unicode=True,sort_keys=False)
            print(yaml_query_out)
        else:
            logging.info(f"queryset: {queryset}")
            logging.info(f"out_expr: {out_expr}")
            out = create_templater(template_string=out_expr, static_context={**self.dataset,**{"queryset": queryset}}).render({},eval_str=False)
            print(out)


def main():
    try:
        JtableCli().parse_args()
    except KeyboardInterrupt:
        exit(1)
    except Exception as error:
        print(f"Unexpected failure: {error}", file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    main()