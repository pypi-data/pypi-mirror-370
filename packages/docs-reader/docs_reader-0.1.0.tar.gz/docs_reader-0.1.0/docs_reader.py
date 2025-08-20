import inspect, linecache
import re
import time
import sys

class DocsReader():
    '''
        this tool/module help to automatically find and show the essentials documents of the given nearest import module with offline mode.

        Examples: 
        1. import in your <filename>.py (e.g. main.py)
            import numpy
            import pandas as pd
            from docs_reader import DocsReader
            DocsReader()

          descriptions:
            # run the <file>.py (e.g. python main.py)
            # after that it will automatically show it's documentation. 
               1. in the above 'numpy' is import that's why show it's documentation.
               2. now it show only the nearest modules documentation of pandas as: pd.

        2.  if any newline is contains before the 'from doc_reader import DocsReader', it can't be parse.
            import numpy
            import pandas as pd

            from doc_reader import DocsReader
            DocsReader()

        descriptions:
            # run the <file>.py (e.g. python main.py)
            # it will show that "could not parse the module" if newlines are contains.      
    '''
    
    # constructor or caller object
    def __init__(self, module_name=None):
        self.module_name = module_name
        current_frame = inspect.currentframe().f_back
        self.filename = current_frame.f_code.co_filename
        self.line_no = current_frame.f_lineno
        self.caller_globals = current_frame.f_globals
        # print(self.caller_globals)
        self.codes = []
        code_line = linecache.getline(self.filename,self.line_no-2).strip()
        # print(code_line, self.line_no-2)

        if code_line == "":
            print("Sorry!! could not parse module.")
            return
        
        # find [from, import, as] if include
        self.module_name = None
        import_as_pattern = r"import\s+(\w+)(\s+as\s+(\w+))?"
        from_import_as_pattern = r"from\s+([\w\.]+)(\s+import\s+(\w+))"
        
        # test = "import abc as ABC"
        # res = re.match(import_pattern, test)
        # print(res.group(3) or res.group(1))

        if match := re.match(import_as_pattern, code_line):
            self.module_name = match.group(3) or match.group(1)
        elif match := re.match(from_import_as_pattern, code_line):
             self.module_name = match.group(2)
             
        if not self.module_name:
            print("Could not resolve module name.")
            return
        
        print(f"Wait system is trying to detect module : '{self.module_name}' ")

        # getting module documents on the system
        target_obj = None

        if self.module_name in self.caller_globals:
            target_obj = self.caller_globals[self.module_name]
        elif self.module_name in sys.modules:
            target_obj = sys.modules[self.module_name]
        
        time.sleep(2)
        if target_obj:
            print(f"\n============== HELP ON '{self.module_name}' ==============")
            help(target_obj)
        else:
            print(f"\nNo accessible object found for '{self.module_name}' ")


    # manually reads by calling read().
    def read(self)-> None:
        help(self.module_name)

   