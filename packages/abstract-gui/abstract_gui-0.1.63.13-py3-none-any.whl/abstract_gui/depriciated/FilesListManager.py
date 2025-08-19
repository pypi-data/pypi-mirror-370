class FilesListManager:
    def __init__(self):
        self.files_list_dict={}
    def check_files_list_key(self,key):
        if key not in self.files_list_dict:
            self.files_list_dict[key]=[]
        return self.files_list_dict[key]
    def clear_list(self,key):
        self.files_list_dict[key]=[]
        return []
    def revise_display_names(self,key):
        file_names_dict={}
        for i,file_refference in enumerate(self.files_list_dict[key]):
            file_name = file_refference['filename']
            if file_name not in file_names_dict:
                file_names_dict[file_name]=0
            else:
                file_names_dict[file_name]+=1
            display_name = file_refference['filename'] if file_names_dict[file_name] == 0 else f"{file_refference['filename']} ({file_names_dict[file_name]})"
            self.files_list_dict[key][i]['display_name'] = display_name
    def is_display_name(self,key,display_name):
        for i,file_refference in enumerate(self.check_files_list_key(key)):
            if display_name == file_refference['display_name']:
                return i
        return display_name
    
    def add_to_files_list_dict(self,key,file_path):
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        for i,file_refference in enumerate(self.check_files_list_key(key)):
            if file_refference['filepath'] == file_path:
                return
        self.files_list_dict[key].append({"dirname":directory,"filename":filename,"filepath":file_path,"display_name":filename})
        self.revise_display_names(key)
    def return_display_names(self,key):
        display_names = []
        for file_refference in self.files_list_dict[key]:
            display_names.append(file_refference['display_name'])
        return display_names
    def re_arrange_display(self,key,position_numbers):
        current_positions = [self.files_list_dict[key][position_numbers[0]],self.files_list_dict[key][position_numbers[1]]]
        new_poisitions = [current_positions[1],current_positions[0]]
        self.files_list_dict[key][position_numbers[0]]=new_poisitions[0]
        self.files_list_dict[key][position_numbers[1]]=new_poisitions[1]
    def remove_item(self,key,display_number):
        new_key_refference = []
        display_number = self.is_display_name(key,display_number)
        for i,file_refference in enumerate(self.files_list_dict[key]):
            if i != display_number:
                new_key_refference.append(self.files_list_dict[key][i])
        self.files_list_dict[key]=new_key_refference
        return self.return_display_names(key)
    def move_up(self,key,display_number):
        display_number = self.is_display_name(key,display_number)
        if display_number >0:
            position_numbers = display_number-1,display_number
            self.re_arrange_display(key,position_numbers)
        return self.return_display_names(key)
    def move_down(self,key,display_number):
        display_number = self.is_display_name(key,display_number)
        if display_number < len(self.files_list_dict[key])-1:
            position_numbers = display_number,display_number+1
            self.re_arrange_display(key,position_numbers)
        return self.return_display_names(key)
    def get_file_path(self,key,display_number):
        display_number = self.is_display_name(key,display_number)
        return self.files_list_dict[key][display_number]['filepath']
    def get_file_path_list(self,key):
        path_list = []
        for file_refference in self.check_files_list_key(key):
            path_list.append(file_refference['filepath'])
        return path_list
