#!/usr/bin/env python3
import yaml,json,logging, sys, os, time, datetime
import re
import html

class Plugin:
    @staticmethod
    def env(var_name,**kwargs):
        """
        Get an environment variable value.
        
        Args:
            var_name (str): Name of the environment variable to retrieve
            **kwargs: Optional arguments including 'default' value if var_name is not found
            
        Returns:
            str: Value of the environment variable or default value if specified
            
        Raises:
            Exception: If environment variable is not found and no default is provided

        Examples:
            >>> Plugin.env('PATH')
            '/usr/local/bin:/usr/bin:/bin'
            >>> Plugin.env('NONEXISTENT', default='default_value')
            'default_value'
        """
        if var_name not in os.environ:
            if 'default' in kwargs:
                return kwargs['default']
            else:
                raise Exception(f"Environment variable {var_name} not found")
        else:
            return os.environ[var_name]

    @staticmethod
    def load_os_vars():
        """
        Get all environment variables as a dictionary.
        
        Returns:
            dict: Dictionary containing all environment variables
            
        Examples:
            >>> env_vars = Plugin.load_os_vars()
            >>> 'PATH' in env_vars
            True
            >>> type(env_vars['HOME'])
            <class 'str'>
        """
        return dict(os.environ)

   
    @staticmethod
    def load_files(search_string, format=json, ignore_errors=True):
        """
        Load multiple files from a search string pattern.
        
        Args:
            search_string (str): File search pattern
            format: Output format (default: json)
            ignore_errors (bool): Whether to ignore errors when loading files
            
        Returns:
            list: List of dictionaries containing file information (name, path, content)
        """
        if running_context['platform']['system'] == "Windows":
            cmd = f"dir /s /b {search_string}"
            logging.info(f"cmd: {cmd}")
            files_str = os.popen("dir /s /b " + search_string).read()
        else:
            files_str = os.popen("ls -1 " + search_string).read()

        file_list_dataset = []
        for file_name_full_path in files_str.split('\n'):
            if file_name_full_path != '':
                with open(file_name_full_path, 'r') as input_yaml:
                    try:
                        file_content =  yaml.safe_load(input_yaml)
                        if running_context['platform']['system'] == "Windows":
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
        return file_list_dataset
    
    @staticmethod
    def shell(cmd,default=None):
        """
        Execute a shell command and return its output.
        
        Args:
            cmd (str): Command to execute
            default: Default value to return if command fails (not used in current implementation)
            
        Returns:
            str: Command output
            
        Raises:
            FileNotFoundError: If bash executable is not found
            subprocess.CalledProcessError: If command execution fails

        Examples:
            >>> Plugin.shell('echo "Hello World"')
            'Hello World\n'
            >>> Plugin.shell('ls -l')
            'total 1234\ndrwxr-xr-x ...'
        """
        import subprocess
        import shutil
        # print(shutil.which("bash"))
        # print(running_context()['shell_type'])
        # exit(1)
        if running_context()['shell_type'] == "git_bash" or running_context()['shell_type'] == "cygwin":
            bash_path = shutil.which("bash.exe")
        else:
            bash_path = shutil.which("bash")

        if bash_path is None:
            raise FileNotFoundError(f"bash_path {bash_path} was not found in PATH")
        output = subprocess.run(
            [bash_path, "-c", cmd],
            check=True,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
            text=True
        )
        return output.stdout
 

def b64decode(value):
    """
    Decode a base64 encoded string.
    
    Args:
        value (str): Base64 encoded string
        
    Returns:
        str: Decoded string in UTF-8

    Examples:
        >>> b64decode('SGVsbG8gV29ybGQ=')
        'Hello World'
        >>> b64decode('UHl0aG9u')
        'Python'
    """
    import base64
    return base64.b64decode(value).decode('utf-8')

def b64encode(value):
    """
    Encode a string to base64.
    
    Args:
        value (str): String to encode
        
    Returns:
        str: Base64 encoded string

    Examples:
        >>> b64encode('Hello World')
        'SGVsbG8gV29ybGQ='
        >>> b64encode('Python')
        'UHl0aG9u'
    """
    import base64
    return base64.b64encode(value.encode('utf-8')).decode('utf-8')

def escape(value,format="html"):
    """
    Escape special characters in a string.
    
    Args:
        value (str): String to escape
        format (str): Format to use for escaping ('html' or 'quote')
        
    Returns:
        str: Escaped string

    Examples:
        >>> escape('<script>alert("Hello")</script>')
        '&lt;script&gt;alert(&quot;Hello&quot;)&lt;/script&gt;'
        >>> escape('This is a "quoted" string', format='quote')
        'This is a \\"quoted\\" string'
    """
    import html
    if format == "html":
        return html.escape(value)
    elif format == "quote":
        return value.replace('\\', '\\\\').replace('"', '\\"')

def flatten(matrix):
    """
    Flatten a 2D matrix into a 1D list.
    
    Args:
        matrix (list): 2D list to flatten
        
    Returns:
        list: Flattened 1D list

    Examples:
        >>> flatten([[1, 2], [3, 4], [5, 6]])
        [1, 2, 3, 4, 5, 6]
        >>> flatten([['a', 'b'], ['c', 'd']])
        ['a', 'b', 'c', 'd']
    """
    return [item for row in matrix for item in row]

def from_flat(data, format="csv"):
    """
    Convert flat data (CSV, TSV, etc.) to a list of dictionaries.
    
    Args:
        data (str): Flat data string
        format (str): Format of the data ('csv', 'tsv', 'psv', 'ssv', 'csv_dict', 'tsv_dict', 'psv_dict', 'flat')
        
    Returns:
        list: List of dictionaries containing the parsed data

    Examples:
        >>> from_flat('name,age\nJohn,30\nJane,25', format='csv')
        [{'name': 'John', 'age': '30'}, {'name': 'Jane', 'age': '25'}]
        >>> from_flat('name\tage\nJohn\t30\nJane\t25', format='tsv')
        [{'name': 'John', 'age': '30'}, {'name': 'Jane', 'age': '25'}]
    """
    import csv
    import io
    if format == "csv":
        list_object =  list(csv.reader(io.StringIO(data)))
    elif format == "tsv":
        list_object =   list(csv.reader(io.StringIO(data), delimiter='\t'))
    elif format == "psv":
        list_object =   list(csv.reader(io.StringIO(data), delimiter='|'))
    elif format == "ssv":
        list_object =   list(csv.reader(io.StringIO(data), delimiter=';'))
    elif format == "csv_dict":
        list_object =   list(csv.DictReader(io.StringIO(data)))
    elif format == "tsv_dict":
        list_object =   list(csv.DictReader(io.StringIO(data), delimiter='\t'))
    elif format == "psv_dict":  
        list_object =   list(csv.DictReader(io.StringIO(data), delimiter='|'))
    elif format == "flat":
        out = []
        for item in data.split("\n"):
            out = out + [{"value": item}]
        return out
    headers = list_object[0]
    data = list_object[1:]
    for i in range(len(data)):
        data[i] = dict(zip(headers, data[i]))
    return data

def from_html(html_string):
    """
    Convert HTML string to JSON.
    
    Args:
        html_string (str): HTML string to convert
        
    Returns:
        dict: JSON representation of the HTML

    Examples:
        >>> from_html('<div><p>Hello</p><p>World</p></div>')
        {'div': {'p': ['Hello', 'World']}}
        >>> from_html('<ul><li>Item 1</li><li>Item 2</li></ul>')
        {'ul': {'li': ['Item 1', 'Item 2']}}
    """
    import html_to_json
    return html_to_json.convert(html_string)

def from_json(str):
    """
    Parse a JSON string into a Python object.
    
    Args:
        str (str): JSON string to parse
        
    Returns:
        object: Parsed Python object

    Examples:
        >>> from_json('{"name": "John", "age": 30}')
        {'name': 'John', 'age': 30}
        >>> from_json('[1, 2, 3, 4]')
        [1, 2, 3, 4]
    """
    return json.loads(str)

def from_yaml(data):
    """
    Parse a YAML string into a Python object.
    
    Args:
        data (str): YAML string to parse
        
    Returns:
        object: Parsed Python object

    Examples:
        >>> from_yaml('name: John\nage: 30')
        {'name': 'John', 'age': 30}
        >>> from_yaml('- item1\n- item2\n- item3')
        ['item1', 'item2', 'item3']
    """
    return yaml.safe_load(data)

def from_json_or_yaml(data):
    """
    Parse a JSON or YAML string into a Python object.
    
    Args:
        data (str): JSON or YAML string to parse
        
    Returns:
        object: Parsed Python object

    Examples:
        >>> from_json_or_yaml('{"name": "John", "age": 30}')
        {'name': 'John', 'age': 30}
        >>> from_json_or_yaml('name: John\nage: 30')
        {'name': 'John', 'age': 30}
    """
    return yaml.safe_load(data)

def from_xml(data):
    """
    Parse an XML string into a Python dictionary.
    
    Args:
        data (str): XML string to parse
        
    Returns:
        dict: Parsed XML as dictionary

    Examples:
        >>> from_xml('<root><name>John</name><age>30</age></root>')
        {'root': {'name': 'John', 'age': '30'}}
        >>> from_xml('<items><item>1</item><item>2</item></items>')
        {'items': {'item': ['1', '2']}}
    """
    import xmltodict
    return xmltodict.parse(data)

def from_yaml_all(data):
    """
    Parse multiple YAML documents from a string.
    
    Args:
        data (str): YAML string containing multiple documents
        
    Returns:
        generator: Generator yielding parsed YAML documents

    Examples:
        >>> list(from_yaml_all('---\nname: John\n---\nname: Jane'))
        [{'name': 'John'}, {'name': 'Jane'}]
        >>> list(from_yaml_all('---\n- 1\n- 2\n---\n- 3\n- 4'))
        [[1, 2], [3, 4]]
    """
    return yaml.safe_load_all(data)

def intersect(a, b):
    """
    Find the intersection of two lists.
    
    Args:
        a (list): First list
        b (list): Second list
        
    Returns:
        list: List containing elements present in both input lists

    Examples:
        >>> intersect([1, 2, 3, 4], [3, 4, 5, 6])
        [3, 4]
        >>> intersect(['a', 'b', 'c'], ['b', 'c', 'd'])
        ['b', 'c']
    """
    return list(set(a).intersection(b))

def running_context():
    """
    Get information about the current running environment.
    
    Returns:
        dict: Dictionary containing platform, shell, and terminal information
    """
    import platform
    import os
    import shutil
    import json

    platform_system = platform.system()
    terminal_name = os.environ.get('TERM', '') 

    ms_system = os.environ.get('MSYSTEM', '')
    if platform_system == "Windows":
        if ms_system == "MINGW64" or ms_system == "CLANGARM64":
            shell_type = "git_bash"
            shell_family = "linux"
        elif terminal_name  == "xterm":
            shell_type = "cygwin"
            shell_family = "linux"
        else:
            shell_type = "windows"
            shell_family = "windows"
    else:
        shell_type = "Linux"
        shell_family = "linux"
    terminal_size = shutil.get_terminal_size()
    terminal = {
        "columns": terminal_size.columns,
        "lines": terminal_size.lines,
        "name": terminal_name,
    }

    running_platform = {
        "system": platform_system,
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "ms_system": ms_system
    }

    return {"platform": running_platform, "shell_family": shell_family, "shell_type": shell_type, "terminal": terminal}

def unescape(value,format="html"):
    """
    Unescape special characters in a string.
    
    Args:
        value (str): String to unescape
        format (str): Format to use for unescaping ('html' or 'quote')
        
    Returns:
        str: Unescaped string
    """
    if format == "html":
        return html.unescape(value)
    elif format == "quote":
        return value.replace('\\"', '"').replace('\\\\', '\\')

def wrap_html(data,title=""):
    """
    Wrap data in an HTML template with CSS and JavaScript.
    
    Args:
        data (str): Content to wrap
        title (str): Page title
        
    Returns:
        str: Complete HTML document
    """
    if running_context()['platform']['system'] == "Windows":
        path_sep = "\\"
    else:
        path_sep = "/"
    base_path = getattr(sys, '_MEIPASS', os.path.abspath(path_sep.join(__file__.split(path_sep)[:-1])))
    logging.info(f"base_path: {base_path}")
    resources_path = f"{base_path}{path_sep}resources"
    def load_file(expected_file_name):
        with open(resources_path + path_sep + expected_file_name, 'r') as file:
            content = file.read()
        return content
    
    js_wrapper_css = load_file("js_wrapper.css")
    js_wrapper_script = load_file("js_wrapper.js")

    return f"""<!DOCTYPE html>
<html lang="fr">
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.4/jquery.min.js"></script>
    <style>
        {js_wrapper_css}
    </style>
<body>
<div id="toc"></div>
{data}
<button id="scrollTopButton" onclick="scrollToTop()">Top</button>
<script>
    {js_wrapper_script}
</script>
</body>
</html>
        """

def m5(data):
    """
    Calculate MD5 hash of a string.
    
    Args:
        data (str): String to hash
        
    Returns:
        str: MD5 hash in hexadecimal format

    Examples:
        >>> m5('Hello World')
        'b10a8db164e0754105b7a99be72e3fe5'
        >>> m5('Python')
        'a7f5f35426b927411fc9231b56382173'
    """
    import hashlib
    return hashlib.md5(data.encode()).hexdigest()

def regex_replace(value="", pattern="", replacement="", ignorecase=False):
    """
    Perform a regex replacement on a string.
    
    Args:
        value (str): String to perform replacement on
        pattern (str): Regex pattern to match
        replacement (str): Replacement string
        ignorecase (bool): Whether to ignore case in pattern matching
        
    Returns:
        str: String with replacements made

    Examples:
        >>> regex_replace('Hello World', 'World', 'Python')
        'Hello Python'
        >>> regex_replace('hello world', 'world', 'python', ignorecase=True)
        'hello python'
    """
    if ignorecase:
        flags = re.I
    else:
        flags = 0
    _re = re.compile(pattern, flags=flags)
    return _re.sub(replacement, value)

def strftime(string_format, second=None):
    """
    Format a timestamp using strftime format string.
    
    Args:
        string_format (str): Format string (see Python time.strftime documentation)
        second (int, optional): Unix timestamp to format. If None, uses current time.
        
    Returns:
        str: Formatted date string
        
    Raises:
        Exception: If second parameter is invalid

    Examples:
        >>> strftime('%Y-%m-%d', 1609459200)  # 2021-01-01 00:00:00
        '2021-01-01'
        >>> strftime('%H:%M:%S', 1609459200)
        '00:00:00'
    """
    if second is not None:
        try:
            second = int(second)
        except Exception:
            raise "Invalid value for epoch value (%s)" % second
    return time.strftime(string_format, time.localtime(second))


def template(input_str, env_dict = {}):
    """
    Render a template string with given keyword arguments.
    
    Args:
        template (str): Template string with placeholders
        **kwargs: Keyword arguments to replace placeholders in the template
        
    Returns:
        str: Rendered template string

    Examples:
        >>> template('Hello, {name}!', name='John')
        'Hello, John!'
        >>> template('Today is {day} of {month}.', day='Monday', month='January')
        'Today is Monday of January.'
    """
    from jinja2 import Environment
    env = Environment()
    return env.from_string(input_str).render(env_dict)



def to_datetime(_string, format=r"%Y-%m-%d %H:%M:%S"):
    """
    Convert a string to datetime object.
    
    Args:
        _string (str): Date string to convert
        format (str): Format string for parsing the date
        
    Returns:
        datetime: Datetime object

    Examples:
        >>> to_datetime('2021-01-01 12:00:00')
        datetime.datetime(2021, 1, 1, 12, 0)
        >>> to_datetime('01/01/2021', format='%d/%m/%Y')
        datetime.datetime(2021, 1, 1, 0, 0)
    """
    import datetime
    return datetime.datetime.strptime(_string, format)

def to_epoch(date_str):
    """
    Convert a date string to Unix epoch timestamp.
    
    Args:
        date_str (str): Date string in format "%Y-%m-%d %H:%M:%S"
        
    Returns:
        int: Unix epoch timestamp

    Examples:
        >>> to_epoch('2021-01-01 00:00:00')
        1609459200
        >>> to_epoch('2021-01-01 12:00:00')
        1609502400
    """
    return int(time.mktime(datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timetuple()))

def to_json(a, *args, **kw):
    """
    Convert a Python object to JSON string.
    
    Args:
        a: Python object to convert
        *args: Additional positional arguments for json.dumps
        **kw: Additional keyword arguments for json.dumps
        
    Returns:
        str: JSON string representation of the object

    Examples:
        >>> to_json({'name': 'John', 'age': 30})
        '{"name": "John", "age": 30}'
        >>> to_json([1, 2, 3, 4])
        '[1, 2, 3, 4]'
    """
    return json.dumps(a, *args, **kw)

def to_pie(dataset):
    """
    Convert dataset to Mermaid pie chart format.
    
    Args:
        dataset (list): List of dictionaries containing pie chart data
        
    Returns:
        str: Mermaid pie chart syntax

    Examples:
        >>> to_pie([{'name': 'A', 'value': 30}, {'name': 'B', 'value': 70}])
        '```mermaid\n  pie\n      title name\n      "A (30)" : 30\n      "B (70)" : 70\n```'
        >>> to_pie([{'fruit': 'Apple', 'count': 5}, {'fruit': 'Banana', 'count': 3}])
        '```mermaid\n  pie\n      title fruit\n      "Apple (5)" : 5\n      "Banana (3)" : 3\n```'
    """
    title = [list(key.keys()) for key in dataset][0][0]
    out = f"```mermaid\n  pie\n      title {title}\n"
    for item in dataset:
        item_prop = list(item.keys())
        out = out + f"      \"{item[item_prop[0]]} ({str(item[item_prop[1]])})\" : {str(item[item_prop[1]])}\n"
    out = out + "```"
    return out

def to_nice_json(v, *args, **kw):
    """
    Convert a Python object to a nicely formatted JSON string.
    
    Args:
        v: Python object to convert
        *args: Additional positional arguments for json.dumps
        **kw: Additional keyword arguments for json.dumps
        
    Returns:
        str: Formatted JSON string

    Examples:
        >>> to_nice_json({'name': 'John', 'age': 30})
        '{\n  "name": "John",\n  "age": 30\n}'
        >>> to_nice_json([1, 2, 3, 4])
        '[\n  1,\n  2,\n  3,\n  4\n]'
    """
    out = json.dumps(v, indent=2, separators=(',', ': '))
    return out    

def to_nice_yaml(v,indent=2):
    """
    Convert a Python object to a nicely formatted YAML string.
    
    Args:
        v: Python object to convert
        indent (int): Number of spaces for indentation
        
    Returns:
        str: Formatted YAML string

    Examples:
        >>> to_nice_yaml({'name': 'John', 'age': 30})
        'name: John\nage: 30\n'
        >>> to_nice_yaml([1, 2, 3, 4])
        '- 1\n- 2\n- 3\n- 4\n'
    """
    return yaml.dump(v, allow_unicode=True,indent=indent)

def to_yaml(v):
    """
    Convert a Python object to a compact YAML string.
    
    Args:
        v: Python object to convert
        
    Returns:
        str: Compact YAML string

    Examples:
        >>> to_yaml({'name': 'John', 'age': 30})
        'name: John age: 30'
        >>> to_yaml([1, 2, 3, 4])
        '[1, 2, 3, 4]'
    """
    out = "".join([v.strip() for v in yaml.dump(v,default_flow_style=True).split('\n')])
    return out

def type_debug(o):
    """
    Get the class name of an object.
    
    Args:
        o: Object to get class name from
        
    Returns:
        str: Class name of the object

    Examples:
        >>> type_debug("Hello")
        'str'
        >>> type_debug([1, 2, 3])
        'list'
        >>> type_debug({'a': 1})
        'dict'
    """
    return  o.__class__.__name__


class InspectDataset:
    """
    Class for inspecting and exploring dataset structures.
    
    This class provides methods to traverse nested data structures
    and discover all available paths and values within them.
    """
    def __init__(self):
        self.out = []
        
    def add_row(self, row):
        """
        Add a row to the output list.
        
        Args:
            row (list): Row data containing path and value
        """
        self.out = self.out + [ [row[0]] + [row[1]] ]
        logging.info("Covering " + " / ".join(flatten([ [row[0]] + [row[1]] ])))
        
    def view_paths(self, dataset, path="", max_depth=0):
        """
        Get all paths and values in a dataset.
        
        Args:
            dataset: The dataset to inspect
            path (str): Current path being explored
            max_depth (int): Maximum depth to explore (0 = unlimited)
            
        Returns:
            list: List of [path, value] pairs
        """
        self.cover_data(dataset, path="", max_depth=0)
        return self.out
        
    def cover_data(self, dataset, path="", max_depth=0):
        """
        Recursively cover all data in a dataset structure.
        
        Args:
            dataset: The dataset to cover
            path (str): Current path being explored
            max_depth (int): Maximum depth to explore (0 = unlimited)
        """
        if type(dataset) is dict:
            for key, value in dataset.items():
                if " " in str(key):
                    the_path = path + "['" + str(key) + "']"
                else:
                    if path == "":
                        the_path = path + str(key)
                    else:
                        the_path = path + "." + str(key)
                self.cover_data(value, the_path)
        elif type(dataset) is list:
            index = 0
            for item in dataset:
                the_path = path + "[" + str(index) + "]"
                index += 1
                self.cover_data(item, the_path)
        else:
            self.add_row([path] + [str(dataset)])






if __name__ == "__main__":
    import sys,inspect
    current_module = sys.modules[__name__]
    safe_globals = {
        name: obj
        for name, obj in inspect.getmembers(current_module, inspect.isfunction)
    }

    if len(sys.argv) < 2:
        print(f"Usage: ./functions.py [options] \"expression\"")
        print("Options:")
        print("  -h <function_name>    Display help for a specific function")
        print("  --help <function_name>    Display help for a specific function")
        print("\nAvailable functions:")
        print(", ".join(sorted(safe_globals.keys())))
        sys.exit(1)

    # Support both -h and --help for function docstring
    if (sys.argv[1] == "-h" or sys.argv[1] == "--help"):
        if len(sys.argv) != 3:
            print("Usage: ./functions.py -h <function_name>")
            print("   or: ./functions.py --help <function_name>")
            print("\nAvailable functions:")
            print(", ".join(sorted(safe_globals.keys())))
            sys.exit(1)
        
        function_name = sys.argv[2]
        if function_name in safe_globals:
            print(f"\nHelp for function '{function_name}':")
            print("-" * (len(function_name) + 15))
            print(inspect.getdoc(safe_globals[function_name]))
            sys.exit(0)
        else:
            print(f"Error: Function '{function_name}' not found")
            print("\nAvailable functions:")
            print(", ".join(sorted(safe_globals.keys())))
            sys.exit(1)

    # Dynamically build safe_globals from functions defined in this module
    py_expr = sys.argv[1]

    try:
        # Evaluate the expression safely
        result = eval(py_expr, {"__builtins__": None}, safe_globals)
        print(result)
    except Exception as e:
        print(f"Error: {e}")

