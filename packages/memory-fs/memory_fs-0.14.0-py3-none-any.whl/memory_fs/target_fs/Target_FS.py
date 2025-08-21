from typing                                             import List, Type
from memory_fs.file_types.Memory_FS__File__Type__Json   import Memory_FS__File__Type__Json
from osbot_utils.type_safe.type_safe_core.decorators.type_safe         import type_safe
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                        import Safe_Id
from memory_fs.file_fs.File_FS                          import File_FS
from memory_fs.path_handlers.Path__Handler              import Path__Handler
from memory_fs.schemas.Schema__Memory_FS__File__Type    import Schema__Memory_FS__File__Type
from memory_fs.storage_fs.Storage_FS                    import Storage_FS
from memory_fs.schemas.Schema__Memory_FS__File__Config  import Schema__Memory_FS__File__Config
from osbot_utils.type_safe.Type_Safe                    import Type_Safe


class Target_FS(Type_Safe):
    storage_fs    : Storage_FS
    path__handlers: List[Path__Handler]

    @type_safe
    def file_fs(self, file_id  : Safe_Id,
                      file_type: Type[Schema__Memory_FS__File__Type]
                 ) -> File_FS:
        file_config = self.file_config(file_id=file_id, file_type=file_type)
        return File_FS(file__config=file_config, storage_fs=self.storage_fs)          # todo: refactor this so that we pass a schema object (for example Schema__Target_FS) that has the references to the file_config and storage objects

    def file_fs__json(self, file_id: Safe_Id):
        file_fs = self.file_fs(file_id=file_id, file_type=Memory_FS__File__Type__Json)
        return file_fs

    def file_config(self, file_id  : Safe_Id                      ,
                          file_type: Type[Schema__Memory_FS__File__Type]
                      )-> Schema__Memory_FS__File__Config:
        kwargs      = dict(file_id    = file_id          ,          # use the file_id provider
                           file_paths = self.file_paths(),          # calculate the paths
                           file_type  = file_type()      )          # create an object of file_type
        file_config = Schema__Memory_FS__File__Config(**kwargs)
        return file_config

    def file_paths(self):
        file_paths = []
        for path_handler in self.path__handlers:
            file_path = path_handler.generate_path()
            file_paths.append(file_path)
        return file_paths
