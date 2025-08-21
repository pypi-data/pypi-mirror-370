from typing                                                         import List
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id  import Safe_Id
from memory_fs.Memory_FS                                            import Memory_FS


class Memory_FS__Temporal(Memory_FS):                                                   # Temporal-only pattern
    def __init__(self, storage_fs = None  ,
                       areas      : List[Safe_Id] = None,
                       **kwargs ):                                                      # params for Path__Handler
        super().__init__(storage_fs=storage_fs)
        self.add_handler__temporal(areas=areas, **kwargs)
