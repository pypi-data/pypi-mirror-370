from memory_fs.path_handlers.Path__Handler              import Path__Handler
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                        import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path


class Path__Handler__Custom(Path__Handler):       # Handler that uses a custom path
    name        : Safe_Id               = Safe_Id("custom")
    custom_path : Safe_Str__File__Path

    # todo: file_id and file_ext should use Safe_Str helpers instead of raw str
    def generate_path(self, file_id: str, file_ext: str, is_metadata: bool = True) -> Safe_Str__File__Path:
        # Return the custom path as-is
        return self.custom_path




