
from typing import List
import os
import re
import itertools

root_dir = r"C:\Users\tedlo\Documents\uv\pyvol_terminal\.venv\Lib\site-packages\pyqtgraph"
#root_dir = r"C:\Qt\QtForPython\6.9.1\Src"
root_dir = r"C:\Users\tedlo\Documents\uv\pyvol_terminal\pyvol_terminal"
                
def search_string(r_dir, r_disclude=None, search_strings: List[str]="", file_ext="", max_distance=30, context=60, e=False) -> None:
    
    
    print(f"\nSearch results for {search_strings} within {max_distance} characters of each other:")

    for dirpath, _, filenames in os.walk(r_dir):
        for filename in filenames:
            if filename.endswith(f"{file_ext}"):
                
                full_path = os.path.join(dirpath, filename)
                if not r_disclude is None:
                    if r_disclude in full_path:
                        continue
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                        # Get list of positions for each search string
                        positions = []
                        for s in search_strings:
                            matches = [m.start() for m in re.finditer(re.escape(s), content)]
                            if not matches:
                                break  # One of the strings not found at all
                            positions.append(matches)
                        else:
                            # Try all combinations of one position per string
                            if e:

                                for combo in itertools.product(*positions):
                                    if max(combo) - min(combo) <= max_distance:
                                        # Get the surrounding text to check if it's inside a print()
                                        start_pos = min(combo)
                                        end_pos = max(combo) + len(search_strings[combo.index(max(combo))])
                                        snippet = content[max(0, start_pos-context):end_pos+context]
                                        
                                        # Check if the pattern is inside a print() call
                                        if re.search(r'print\s*\(.*' + re.escape(search_string2) + r'.*\)', snippet):
                                            print(full_path)
                                            break  # No need to keep checking this file
                            else:
                                for combo in itertools.product(*positions):
                                    if max(combo) - min(combo) <= max_distance:
                                        print(full_path)
                
                                        
                                        #for i, pos in enumerate(combo):
                                        #    s = search_strings[i]
                                        #    snippet = content[max(0, pos):pos + len(s) + context]
                                        #    print(f"Found '{s}' at {pos}:\n...{snippet}...")
                                        break  # N  o need to keep checking this file
                except (UnicodeDecodeError, FileNotFoundError, PermissionError) as e:
                    print(f"Could not read {full_path}: {e}")

def search_file_names(r_dir, fname):
    for dirpath, _, filenames in os.walk(r_dir):
        for filename in filenames:
            if fname in filename:
                full_path = os.path.join(dirpath, filename)
                print(full_path)
            


search_string1 = "dependency"
search_string2 = "engine"
strings = [search_string1,
        #   search_string2
           ]
dir_disclude =  None
file_ext = ".py"
#fle_ext_disclude = 
max_distance=20

search_string(root_dir, search_strings=strings, file_ext=file_ext, max_distance=max_distance, e=False)
#search_file_names(root_dir, strings[0])