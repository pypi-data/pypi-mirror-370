"""
abstract_browser
=================

The `abstract_browser` module is part of the `abstract_gui` module of the `abstract_essentials` package. 
It provides an abstracted mechanism for creating and managing a file/folder browser using PySimpleGUI.

Classes and Functions:
----------------------
- get_scan_browser_layout: Returns the layout for the file/folder scanner window.
- browse_update: Updates values in the browse window.
- return_directory: Returns the current directory or parent directory if a file is selected.
- scan_window: Handles events for the file/folder scanner window.
- forward_dir: Navigate to the given directory.
- scan_directory: Returns the files or folders present in the given directory based on the selected mode.
- get_browse_scan: Initializes the scanner with default settings and runs it.

"""
import os
from .files_list_manager import FilesListManager
from .abstract_window_manager import AbstractWindowManager
from .abstract_gui import sg,get_event_key_js,make_component,text_to_key,ensure_nested_list,expandable
from abstract_utilities import eatAll
def capitalize(text):
    if text:
        text=text[0].upper()+text[1:]
    return text
class LastSelectedManager:
    def __init__(self):
        self.selections={}
    def check_selections(self,section=None):
        if str(section) not in self.selections:
            self.selections[str(section)]=[]
    def last_selected(self,selection,section=None):
        self.check_selections(section=section)
        self.selections[str(section)].append(selection)
        if len(self.selections[str(section)])>2:
            self.selections[str(section)]=self.selections[str(section)][-2:]
        if self.selections[str(section)][0] == self.selections[str(section)][1]:
            return True
class AbstractBrowser:
    """
    This class aims to provide a unified way of browsing through different sources.
    It could be used as the base class for browsing through different APIs, files, databases, etc.
    The actual implementation of how to retrieve or navigate through the data should be done in the derived classes.
    """
    def __init__(self, window_mgr=None,window_name=None,window=None):
        self.window_mgr = window_mgr
        if window_mgr:
            if hasattr(window_mgr, 'window'):
                self.window = window_mgr.window
        elif window_name:
            if hasattr(window_mgr, 'get_window'):
                self.window=window_mgr.get_window(window_name=window_name)
        else:
            self.window = make_component('Window','File/Folder Scanner', layout=self.get_scan_browser_layout())
        self.event = None
        self.values = None
        self.files_list_mgr = FilesListManager()
        self.last_selected_mgr = LastSelectedManager()
        self.mode_tracker={}
        self.last_selected=None
        self.scan_mode = "all"
        self.history = [os.getcwd()]
        self.ext_keys=["-FILE_EXT_CHECK-",'-FILE_EXT_DROP-',"-FILE_EXT-"]
        self.modes = ['-SCAN_MODE_FILES-','-SCAN_MODE_FOLDERS-','-SCAN_MODE_ALL-']
        self.key_list = ['-BROWSER_LIST-','-CLEAR_LIST-','-REMOVE_FROM_LIST-','-MOVE_UP_LIST-','-MOVE_DOWN_LIST-','-ADD_TO_LIST-',"-FILES_BROWSER-","-DIR-","-DIRECTORY_BROWSER-","-FILES_LIST-","-SCAN_MODE_ALL-","-SELECT_HIGHLIGHTED-","-SCAN-", "-SELECT_HIGHLIGHTED-", "-MODE-", "-BROWSE_BACKWARDS-", "-BROWSE_FORWARDS-"]+self.modes+self.ext_keys
    def initiate_browser_window(self,window_name="Browser_Window",title="Abstract Browser",extra_buttons=[],section=None,event_handlers=[],exit_events=[]):
        self.window_mgr = AbstractWindowManager()
        self.window_name = self.window_mgr.add_window(window_name=window_name,title=title,layout=self.get_scan_browser_layout(extra_buttons=extra_buttons,section=section),**expandable(),exit_events=exit_events)
        self.window = self.window_mgr.get_window_method(self.window_name)
        event_handlers.append(self.handle_event)
        self.window_mgr.while_window(window_name=self.window_name, event_handlers=event_handlers)
    def handle_event(self,event,values,window):
        
        self.event,self.values,self.window=event,values,window
        self.event_key_js = get_event_key_js(self.event,key_list=self.key_list)
        if self.event_key_js['section']==None:
            none_js={'event':event,'found':event,'section':None}
            for key in self.key_list:
                none_js[key]=key
            self.event_key_js=none_js
        if event not in self.key_list:
            
            try:
                self.event_key_js = get_event_key_js(self.event,key_list=self.key_list)
            except:
                self.event_key_js={"found":event,"section":'',"event":event}

        if self.event_key_js['found']:
            return self.while_static(event_key_js=self.event_key_js, values=self.values,window=self.window)
        else:
            return self.event, self.values
    def scan_it(self,directory):
        if os.path.isdir(self.values[self.event_key_js['-DIR-']]):
            self.scan_results = self.scan_directory(directory, self.scan_mode)
            self.browse_update(key=self.event_key_js['-BROWSER_LIST-'],args={"values":self.scan_results})
            self.check_ext()
    @staticmethod
    def get_scan_browser_layout(section=None, extra_buttons=[]):
        """
        Generate the layout for the file/folder scanning window.

        Returns:
            --------
            list:
                A list of list of PySimpleGUI elements defining the window layout.
            """
            
        # More complex layout with additional elements
        browser_buttons_layout = [sg.Column([[sg.Checkbox('All', default=True, key=text_to_key(text='scan mode all',section=section), enable_events=True)],
                       [sg.Checkbox('Folders', key=text_to_key(text='scan mode folders',section=section), enable_events=True)],
                       [sg.Checkbox('Files', key=text_to_key(text='scan mode files',section=section), enable_events=True)]]),
                                  sg.Column([[sg.Frame('.ext',[[sg.Checkbox('',key=text_to_key(text="-FILE_EXT_CHECK-",section=section),enable_events=True),sg.Input('',size=(5,1),key=text_to_key(text="-FILE_EXT-",section=section),enable_events=True)]]),
                                              sg.Frame('/map',[[sg.Combo(['norm','map','spec'],key=text_to_key(text='-FILE_EXT_DROP-',section=section),enable_events=True)]])]])]
        listboxes_layout=[]
        listboxes_layout.append(sg.Frame('browser',layout=ensure_nested_list([[sg.Listbox(values=[], size=(50, 10), key=text_to_key(text='browser list',section=section), enable_events=True)],
                                                                             [sg.Push(),sg.Button('<-', key=text_to_key(text='browse backwards',section=section)),
                                                                              sg.Button('Scan', key=text_to_key(text='scan',section=section)),
                                                                              sg.Button('->', key=text_to_key(text='browse forwards',section=section)),sg.Button('ADD', key=text_to_key(text='add_to_list',section=section)),sg.Push()]])))

        listboxes_layout.append(sg.Frame('files',layout=ensure_nested_list([[sg.Listbox(values=[], size=(50, 10), key=text_to_key(text='files list',section=section), enable_events=True)],
                                                                             [sg.Push(),sg.Button('UP', key=text_to_key(text='move up list',section=section)),sg.Button('DOWN', key=text_to_key(text='move down list',section=section)),
                                                                              sg.Button('REMOVE', key=text_to_key(text='remove from list',section=section)),
                                                                              sg.Button('Clear', key=text_to_key(text='clear list',section=section)),sg.Push()]])))


        layout = [[sg.Text('Directory to scan:'), sg.InputText(os.getcwd(),key=text_to_key(text='dir',section=section)),sg.FolderBrowse('Folders', key=text_to_key(text='directory browser',section=section)),sg.FileBrowse('Files', key=text_to_key(text='file browser',section=section))],
            [sg.Column([listboxes_layout,browser_buttons_layout])]]
        if extra_buttons:
            layout.append(extra_buttons)         
        return layout
    def return_remaining(self,comp,neg):
        list_obj=[]
        for each in comp:
            if each not in neg:
                list_obj.append(each)
        return list_obj
    def get_opposite_scans(self,key):
        bool_key = self.values[key]
        each_type = [self.event_key_js['found']]
        
        if bool_key:
            returned = self.return_remaining(self.modes,each_type)
            each_type.append(returned[0])
            self.window[self.event_key_js[each_type[-1]]].update(False)
            returned = self.return_remaining(self.modes,each_type)[0]
            each_type.append(returned)
            self.window[self.event_key_js[each_type[-1]]].update(False)
            self.scan_it(self.return_directory())
            return
        each_type.remove(each_type[0])
        each_type.append(self.values[self.event_key_js[each_type][0]])
        each_type.remove(each_type[1])
        each_type.append(self.values[self.event_key_js[each_type][1]])
        if True not in each_type:
            self.window[self.event_key_js[key]].update(True)
    def check_ext(self):
        if self.values[self.event_key_js["-FILE_EXT_CHECK-"]]:
            file_ext =self.values[self.event_key_js["-FILE_EXT-"]]
            if file_ext:
                directory = self.values[self.event_key_js["-DIR-"]]
                browser_values = self.window[self.event_key_js['-BROWSER_LIST-']].Values
                ext_list = []
                for item in browser_values:
                    path=os.path.join(directory,item)
                    if os.path.isfile(path) or (os.path.isdir(path) and (self.values[self.event_key_js['-SCAN_MODE_FOLDERS-']] or self.values[self.event_key_js['-SCAN_MODE_ALL-']])):
                        basename,ext = os.path.splitext(path)
                        if eatAll(ext,'.') == eatAll(file_ext,'.') or (os.path.isdir(path) and (self.values[self.event_key_js['-SCAN_MODE_FOLDERS-']] or self.values[self.event_key_js['-SCAN_MODE_ALL-']])):
                           ext_list.append(item)
                
                self.window[self.event_key_js['-BROWSER_LIST-']].update(values=ext_list)
    def while_static(self,event_key_js,values,window):
        self.event_key_js,self.values,self.window=event_key_js,values,window
        self.section_key = key = self.event_key_js['section']
        if self.event_key_js['found'] in self.ext_keys:
            if self.event_key_js['found'] in ["-FILE_EXT_CHECK-","-FILE_EXT-"]:
                self.check_ext()
        if self.event_key_js['found'] == "-FILES_BROWSER-":
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":self.values[self.event_key_js["-FILES_BROWSER-"]]})
        if self.event_key_js['found'] == "-DIRECTORY_BROWSER-":
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":self.values[self.event_key_js["-DIRECTORY_BROWSER-"]]})
        if self.event_key_js['found'] == '-SCAN-':
            self.scan_it(self.return_directory())
        if self.event_key_js['found'] == "-SELECT_HIGHLIGHTED-":
            if len(self.values[self.event_key_js['-BROWSER_LIST-']])>0:
                self.browse_update(key=self.event_key_js['-DIR-'],args={"value":os.path.join(self.return_directory(), self.values[self.event_key_js['-BROWSER_LIST-']][0])})
        if self.event_key_js['found'][:len('-SCAN_MODE')]=='-SCAN_MODE':
            self.get_opposite_scans(self.event_key_js['event'])
        if self.event_key_js['found'] in self.modes:
            for mode in self.modes:
                if self.event_key_js['found'] == mode:
                    if self.values[self.event_key_js[mode]]:
                        self.scan_mode = eatAll(mode[1:-1].split('_')[-1].lower(),['s'])
                        for each_mode in self.modes:
                            if each_mode != mode:
                                self.window[self.event_key_js[each_mode]].update(False)
        if self.event_key_js['found'] == '-MODE-':
            if self.event_key_js['found'] not in self.mode_tracker:
                self.mode_tracker[self.event_key_js['-MODE-']]=[self.scan_mode,self.scan_mode]
            self.scan_it(self.return_directory())    
        if self.event_key_js['found'] in ['-MOVE_UP_LIST-','-MOVE_DOWN_LIST-','-REMOVE_FROM_LIST-']:
            list_value = self.values[self.event_key_js['-FILES_LIST-']]
            if list_value:
                display_number=list_value[0]
                if self.event_key_js['found'] == '-MOVE_UP_LIST-':
                    display_values = self.files_list_mgr.move_up(self.section_key,display_number)
                elif self.event_key_js['found'] == '-MOVE_DOWN_LIST-':
                    display_values = self.files_list_mgr.move_down(self.section_key,display_number)
                elif self.event_key_js['found'] == '-REMOVE_FROM_LIST-':
                    display_values = self.files_list_mgr.remove_item(self.section_key,display_number)
                self.window[self.event_key_js['-FILES_LIST-']].update(display_values)
        if self.event_key_js['found'] == '-ADD_TO_LIST-':
            self.files_list_mgr.check_files_list_key(self.section_key)
            file_list = self.values[self.event_key_js['-BROWSER_LIST-']]
            path_dir = self.values[self.event_key_js['-DIR-']]
            if file_list:
                filename = file_list[0]
                file_path = os.path.join(path_dir,filename)
                self.files_list_mgr.add_to_files_list_dict(self.section_key,file_path)
                self.window[self.event_key_js['-FILES_LIST-']].update(self.files_list_mgr.return_display_names(self.section_key))
        if self.event_key_js['found'] == '-CLEAR_LIST-':
            self.window[self.event_key_js['-FILES_LIST-']].update(self.files_list_mgr.clear_list(key))
        if self.event_key_js['found'] == "-BROWSE_BACKWARDS-":
            # Navigate up to the parent directory
            if self.return_directory() not in self.history:
                self.history.append(self.return_directory())
            directory = os.path.dirname(self.return_directory())  # This will give the parent directory
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":directory})
            self.browse_update(key=self.event_key_js['-BROWSER_LIST-'],args={"values":self.scan_directory(directory, self.scan_mode)})
            self.scan_it(directory)
        if self.event_key_js['found'] in ["-BROWSE_FORWARDS-",'-BROWSER_LIST-']:
            directory=None
            try:
                # Navigate down into the selected directory or move to the next history path
                if self.values[self.event_key_js['-BROWSER_LIST-']]:  # If there's a selected folder in the listbox
                    obj = self.values[self.event_key_js['-BROWSER_LIST-']][0]
                    if self.last_selected_mgr.last_selected(selection=obj,
                                                        section=self.event_key_js['section']):
                        directory = os.path.join(self.return_directory(),obj)
                    if os.path.isdir(directory):
                        self.forward_dir(directory)
                        self.scan_it(directory)
                elif self.history:  # If there's a directory in the history stack
                    directory = self.history.pop()
                    self.browse_update(key=self.event_key_js['-DIR-'],args={"value":directory})
                    self.browse_update(key=self.event_key_js['-BROWSER_LIST-'],args={"values":self.scan_directory(directory, self.scan_mode)})
            except:
                print(f'could not scan directory {directory}')
        return self.event,self.values
    def return_directory(self):
        """
        Return the current directory or parent directory if a file path is provided.

        Returns:
        --------
        str:
            Directory path.
        """
        directory = self.values[self.event_key_js['-DIR-']]
        if os.path.isfile(self.values[self.event_key_js['-DIR-']]):
            directory = os.path.dirname(self.values[self.event_key_js['-DIR-']])
        if directory == '':
            directory = os.getcwd()
        return directory
    def browse_update(self,key: str = None, args: dict = {}):
        """
        Update specific elements in the browse window.

        Parameters:
        -----------
        window : PySimpleGUI.Window
            The window to be updated. Default is the global `browse_window`.
        key : str, optional
            The key of the window element to update.
        args : dict, optional
            Arguments to be passed for the update operation.
        """
        self.window[key](**args)
    def read_window(self):
        self.event,self.values=self.window.read()
        return self.event,self.values
    def get_values(self):
        if self.values==None:
            self.read_window()
        return self.vaues
    def get_event(self):
        if self.values==None:
            self.read_window()
        return self.event
    def scan_window(self):
        """
        Event handler function for the file/folder scanning window.

        Parameters:
        -----------
        event : str
            Name of the event triggered in the window.
        """
        while True:
            self.read_window()
            if self.event == None:
                break
            while_static(event)
        self.window.close()

    def forward_dir(self,directory):
        """
        Navigate and update the scanner to display contents of the given directory.

        Parameters:
        -----------
        directory : str
            Path to the directory to navigate to.
        """
        if os.path.isdir(directory):
            self.browse_update(key=self.event_key_js['-DIR-'],args={"value":directory})
            self.browse_update(key=self.event_key_js['-BROWSER_LIST-'],args={"values":self.scan_directory(directory, self.scan_mode)})
    def scan_directory(self,directory_path, mode):
        """
        List files or folders in the given directory based on the provided mode.

        Parameters:
        -----------
        directory_path : str
            Path to the directory to scan.
        mode : str
            Either 'file' or 'folder' to specify what to list.

        Returns:
        --------
        list:
            List of file/folder names present in the directory.
        """
        if mode == 'file':
            return [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        elif mode == 'folder':
            return [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
        return [d for d in os.listdir(directory_path)]
  
    @staticmethod
    def popup_T_F(title:str="popup window",text:str="popup window text"):
        answer = get_yes_no(title=title,text=text)
        if answer == "Yes":
            return True
        return False
    @staticmethod
    def create_new_entity(event:str=None, entity_type:str="Folder"):
        # Retrieve values from the GUI
        if "-ENTITY_TYPE-" in self.values:
            entity_type = self.values["-ENTITY_TYPE-"]
        if event in ["-FOLDER_BROWSE-",'-ENTITY_NAME-']:
            if os.path.isfile(self.values['-ENTITY_NAME-']):
                self.browse_update("-PARENT_DIR-",args={"value":self.get_directory(self.values['-ENTITY_NAME-'])})
                file_name = os.path.basename(self.values['-ENTITY_NAME-'])
                self.browse_update('-ENTITY_NAME-',args={"value":file_name})
        if event == "Create":
            exists =False
            if values['-ENTITY_NAME-'] and self.values['-PARENT_DIR-']:
                entity_path = os.path.join(self.values['-PARENT_DIR-'],self.values['-ENTITY_NAME-'])
                if entity_type == "Folder":
                    exists = os.path.exists(entity_path)  # changed from os.path.dir_exists(entity_path)
                if entity_type == "File":
                    exists = os.path.exists(entity_path)
                if exists:
                    if not popup_T_F(title=f"Override the {entity_type}?",text=f"looks like the {entity_type} path {entity_path} already exists\n did you want to overwrite it?"):
                        return False
                if entity_type == "Folder" and not exists:
                    os.makedirs(entity_path, exist_ok=True)
                elif entity_type == "File":
                    with open(entity_path, 'w') as f:
                        if "save_data" in js_browse_bridge:
                            f.write(self.save_data)  # writes the save_data to the file
                        else:
                            pass  # creates an empty file, or you can handle this differently
                self.browse_update("-FINAL_OUTPUT-",args={"value":entity_path})
                self.browse_update("-SAVE_PROMPT-",args={"visible":True})
                self.window.Element("Cancel").update(text="Exit")

                return "Cancel"
