import ast
import os
import importlib.util
import pkgutil
import sys
import traceback
import site
import PySimpleGUI as sg
from .abstract_browser import AbstractBrowser
from .abstract_window_manager import AbstractWindowManager
from .simple_gui_functions_manager import make_component
from .abstract_gui import expandable
from abstract_modules import *
# Global variables
module = None
functions = {}
def find_all_site_packages():
    """
    Find all site-packages directories on the system.
    
    Returns:
        list: Sorted list of unique site-packages paths.
    """
    paths = set()  # Use a set to avoid duplicates
    
    # From site module
    paths.update(site.getsitepackages())
    
    # From sys.path
    paths.update(path for path in sys.path if 'site-packages' in path)
    
    # From filesystem (limited to home directory for speed)
    try:
        for dirpath, dirnames, _ in os.walk('/home/computron'):
            if 'site-packages' in dirnames:
                paths.add(os.path.join(dirpath, 'site-packages'))
    except PermissionError:
        print("Permission denied in some directories")
    
    return sorted(paths)
def file_events(event, values, window):
    global module, functions
    print("Event:", event)

    # Select a site-packages path from listbox
    if event == '-SITE_PACKAGES_LIST-':
        selected_path = values['-SITE_PACKAGES_LIST-']
        if selected_path:
            selected_path = selected_path[0]  # Listbox returns a list
            modules = get_installed_modules(selected_path)
            window['-MODULE_LIST-'].update(values=modules)
            window['-STREAM_OUTPUT-'].update(window['-STREAM_OUTPUT-'].get() + f"Selected site-packages: {selected_path}\nModules loaded: {len(modules)}\n")

    # Load from a file
    elif event == 'Load File':
        directory = values.get('-DIR-')
        basename = values.get('-FILES_LIST-')[0]
        file_path = os.path.join(directory, basename)
        filename, ext = os.path.splitext(basename)
        if file_path and os.path.isfile(file_path) and ext == '.py':
            try:
                functions = parse_functions_from_file(file_path)
                module = load_module_from_file(file_path)
                window['-FUNCTION_LIST-'].update(values=list(functions.keys()))
                stream_output = window['-STREAM_OUTPUT-'].get() + "Loaded functions from file:\n" + "\n".join(functions.keys()) + "\n"
                window['-STREAM_OUTPUT-'].update(stream_output)
                update_argument_fields(window, [])
            except Exception as e:
                error_str = f"Error loading file: {e}\n{traceback.format_exc()}\n"
                window['-STREAM_OUTPUT-'].update(window['-STREAM_OUTPUT-'].get() + error_str)
        else:
            sg.popup_error("Please select a valid Python file.")

    # Load from an installed module
    elif event in ['-MODULE_LIST-', 'Load Module']:
        selected_module = values.get('-MODULE_LIST-')
        if selected_module:
            selected_module = selected_module[0]  # Listbox returns a list
            try:
                module = importlib.import_module(selected_module)
                functions = parse_functions_from_module(module)
                window['-FUNCTION_LIST-'].update(values=list(functions.keys()))
                stream_output = window['-STREAM_OUTPUT-'].get() + f"Loaded functions from module '{selected_module}':\n" + "\n".join(functions.keys()) + "\n"
                window['-STREAM_OUTPUT-'].update(stream_output)
                update_argument_fields(window, [])
            except Exception as e:
                error_str = f"Error loading module: {e}\n{traceback.format_exc()}\n"
                window['-STREAM_OUTPUT-'].update(window['-STREAM_OUTPUT-'].get() + error_str)
        else:
            sg.popup_error("Please select a module.")

    # When a function is selected from the listbox
    elif event == '-FUNCTION_LIST-':
        selected_function = values['-FUNCTION_LIST-']
        if selected_function:
            selected_function = selected_function[0]  # Listbox returns a list
            if selected_function in functions:
                arg_names = functions[selected_function]
                update_argument_fields(window, arg_names)
            else:
                update_argument_fields(window, [])  # Hide all if no valid function

    # Run the selected function with provided arguments
    elif event == 'Run Function':
        selected_function = values['-FUNCTION_LIST-']
        if not selected_function:
            sg.popup_error("No function selected.")
            return
        selected_function = selected_function[0]  # Listbox returns a list
        if module is None:
            sg.popup_error("No module loaded.")
            return
        try:
            args = []
            for arg in functions[selected_function]:
                arg_value = values.get(f'-ARG_{arg}-', '')
                args.append(arg_value if arg_value != '' else None)
            func = getattr(module, selected_function)
            result = func(*args)
            output_str = f"Result from {selected_function}({', '.join(map(str, args))}):\n{result}\n"
            window['-FUNCTION_OUTPUT-'].update(output_str)
        except Exception as e:
            error_str = f"Error running function {selected_function}: {e}\n{traceback.format_exc()}\n"
            window['-FUNCTION_OUTPUT-'].update(error_str)



def update_argument_fields(window, arg_names):
    """Show/hide and label input fields based on the function's arguments."""
    max_args = 10  # Same as the number of predefined fields in the layout
    for i in range(max_args):
        text_key = f'-ARG_TEXT_{i}-'
        input_key = f'-ARG_{i}-'
        if i < len(arg_names):
            window[text_key].update(value=f"{arg_names[i]}:", visible=True)
            window[input_key].update(value='', visible=True)
            window[input_key].Key = f'-ARG_{arg_names[i]}-'
        else:
            window[text_key].update(visible=False)
            window[input_key].update(visible=False)

def run_functions_gui():
    # Get all site-packages paths for the listbox
    site_packages_paths = find_all_site_packages()
    default_path = site_packages_paths[0]
    # Define the General Output frame (new text output on the left)
    general_output_frame = sg.Frame('General Output', [[make_component("Multiline", key='-FUNCTION_OUTPUT-', **expandable(size=(30, 90)))]])

    # Define the Stream Output frame
    stream_output_frame = sg.Frame('Stream Output', [[make_component("Multiline", key='-STREAM_OUTPUT-', **expandable(size=(30, 10)))]])

    # Define the Function Output frame
    function_output_frame = sg.Frame('Modules', [[sg.Listbox(get_installed_modules(default_path), size=(30, 10), key='-MODULE_LIST-', enable_events=True, expand_x=True)]])

    # Left column with General Output
    left_column = [
        [general_output_frame]
    ]

    # Main layout with two columns
    outputs_layout = [stream_output_frame,function_output_frame]
    


    # Right column with the full previous layout
    right_column = [
     
        outputs_layout,
        [sg.Text('Load from File:'), sg.Button('Load File')],
        [sg.Frame('Site-packages Path', [[sg.Listbox(site_packages_paths, default_values=[default_path], key='-SITE_PACKAGES_LIST-', enable_events=True, size=(70, 10))]])],
        [sg.Frame('Functions', [[sg.Listbox([], size=(30, 10), key='-FUNCTION_LIST-', enable_events=True, expand_x=True)]])],
        [sg.Button('Load Module')]
        
    ]
    function_column = [*[[sg.Text('', key=f'-ARG_TEXT_{i}-', visible=False),
           sg.Input('', key=f'-ARG_{i}-', visible=False, size=(30, 1))] for i in range(10)],
        [sg.Button('Run Function')]]
    # Main layout with two columns
    main_layout = [
        [sg.Column(left_column, expand_x=True, expand_y=True),
         sg.Column(function_column, expand_x=True, expand_y=True),
         
         sg.Column(right_column, expand_y=True)]
    ]

    # Integrate with AbstractBrowser
    browser_layout = AbstractBrowser().get_scan_browser_layout(extra_buttons=main_layout)

    # Start the browser with AbstractWindowManager
    window_mgr = AbstractWindowManager()
    window_name = window_mgr.add_window(title="File/Folder Browser", layout=browser_layout, event_handlers=[file_events],**expandable())
    window_mgr.while_window(window_name=window_name,)

