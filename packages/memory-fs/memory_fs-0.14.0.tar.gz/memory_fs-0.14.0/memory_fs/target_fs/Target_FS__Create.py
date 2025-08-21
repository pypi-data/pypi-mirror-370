from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from memory_fs.storage_fs.Storage_FS                    import Storage_FS
from osbot_utils.utils.Json                             import bytes_to_json
from memory_fs.target_fs.Target_FS                      import Target_FS
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class Target_FS__Create(Type_Safe):
    storage_fs  : Storage_FS
    # todo: this needs to be re-implemented to take into account the new Target_FS architecture
    def from_path__config(self, path : Safe_Str__File__Path) -> Target_FS:                  # Load a File_Fs object from a config path
        raise NotImplementedError
        with self.storage_fs as _:                                                          # todo: refactor the logic to load the config file from storage into a separate method or class
            if _.file__exists(path):                                                        # todo add a check if path is indeed a .config file
                file_bytes  = _.file__bytes(path)
                file_json   = bytes_to_json(file_bytes)
                file_config = Schema__Memory_FS__File__Config.from_json(file_json)          # todo: add error handling and the cases when file_json is not Schema__Memory_FS__File__Config
                target_fs   = Target_FS(file__config=file_config, storage_fs=self.storage_fs)
                return target_fs                                                            # todo: change the logic since we should be able to always return a target_fs (regardless if the file existed or not)