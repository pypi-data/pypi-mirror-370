from typing                                 import Type, List, Dict
from memory_fs.storage_fs.Storage_FS        import Storage_FS
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id            import Safe_Id
from memory_fs.path_handlers.Path__Handler  import Path__Handler
from osbot_utils.type_safe.Type_Safe        import Type_Safe

class Schema__Memory_FS__Project__Path_Strategy(Type_Safe):
    name         : Safe_Id = None
    path_handlers: List[Type[Path__Handler]]

class Schema__Memory_FS__Project__Config(Type_Safe):
    storage_fs     : Type[Storage_FS]
    path_strategies: Dict[Safe_Id, Schema__Memory_FS__Project__Path_Strategy]
    name           : Safe_Id  = None