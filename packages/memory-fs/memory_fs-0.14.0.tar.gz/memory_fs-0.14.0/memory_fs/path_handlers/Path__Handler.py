from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                        import Safe_Id
from osbot_utils.type_safe.Type_Safe                    import Type_Safe

class Path__Handler(Type_Safe):
    name: Safe_Id = None

    def generate_path(self) -> Safe_Str__File__Path:
        raise NotImplementedError()