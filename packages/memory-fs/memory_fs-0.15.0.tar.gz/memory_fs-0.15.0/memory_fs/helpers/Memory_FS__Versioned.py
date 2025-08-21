from memory_fs.Memory_FS import Memory_FS


class Memory_FS__Versioned(Memory_FS):                                                  # Versioned pattern
    def __init__(self, storage_fs = None,
                       **kwargs ):                                                      # params for Path__Handler
        super().__init__(storage_fs=storage_fs)
        self.add_handler__versioned(**kwargs)
