from memory_fs.file_fs.File_FS                              import File_FS
from memory_fs.schemas.Schema__Memory_FS__File__Type        import Schema__Memory_FS__File__Type
from memory_fs.storage_fs.Storage_FS                        import Storage_FS
from osbot_utils.type_safe.type_safe_core.decorators.type_safe             import type_safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                            import Safe_Id
from memory_fs.project.Schema__Memory_FS__Project__Config   import Schema__Memory_FS__Project__Config, Schema__Memory_FS__Project__Path_Strategy
from osbot_utils.type_safe.Type_Safe                        import Type_Safe

class Memory_FS__Project(Type_Safe):
    config      : Schema__Memory_FS__Project__Config
    storage_fs  : Storage_FS

    def file(self, file_id     : Safe_Id,
                   path_strategy: Schema__Memory_FS__Project__Path_Strategy,
                   file_type    : Schema__Memory_FS__File__Type
              ) -> File_FS:

        file_paths = []
        for path_handler in path_strategy.path_handlers:
            file_path = path_handler().generate_path()
            file_paths.append(file_path)

        with File_FS() as file:
            with file.file__config as _:
                _.file_type  = file_type
                _.file_paths = file_paths
                _.file_id  = file_id
            return file

    @type_safe
    def path_strategy(self, path_strategy_name:Safe_Id) -> Schema__Memory_FS__Project__Path_Strategy:
        return self.config.path_strategies.get(path_strategy_name)
