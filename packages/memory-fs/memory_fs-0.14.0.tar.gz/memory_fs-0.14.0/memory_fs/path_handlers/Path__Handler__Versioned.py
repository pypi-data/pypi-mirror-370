from memory_fs.path_handlers.Path__Handler              import Path__Handler
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                        import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path


class Path__Handler__Versioned(Path__Handler):    # Handler that stores files with version numbers (calculated from chain)
    name : Safe_Id = Safe_Id("versioned")

    # todo: review the use of this generate_path since with the current implementation we have a difference signature than Path__Handler
    # todo: file_id and file_ext should use Safe_Str helpers rather than raw str types
    def generate_path(self, file_id: str, file_ext: str, is_metadata: bool = True, version: int = 1) -> Safe_Str__File__Path:
        ext = ".json" if is_metadata else f".{file_ext}"
        return Safe_Str__File__Path(f"v{version}/{file_id}{ext}")
