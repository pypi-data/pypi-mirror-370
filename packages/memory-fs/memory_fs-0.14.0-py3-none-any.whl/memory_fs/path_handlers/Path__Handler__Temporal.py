from datetime                                           import datetime
from typing                                             import List
from memory_fs.path_handlers.Path__Handler              import Path__Handler
from osbot_utils.type_safe.primitives.safe_str.identifiers.Safe_Id                        import Safe_Id
from osbot_utils.type_safe.primitives.safe_str.filesystem.Safe_Str__File__Path  import Safe_Str__File__Path


class Path__Handler__Temporal(Path__Handler):                               # Handler that stores files in temporal directory structure
    name  : Safe_Id       = Safe_Id("temporal")
    areas : List[Safe_Id]                                                   # todo: refactor to Path__Handler__Areas, this Path__Handler__Temporal should only have the date based path

    # todo: refactor to the more comprehensive date path generation we have in the HackerNews (where we can also control which date and time element to use (from year to miliseconds)
    def generate_path(self) -> Safe_Str__File__Path:
        time_path  = self.path_now()
        areas_path = "/".join(str(area) for area in self.areas) if self.areas else ""

        if areas_path:
            return Safe_Str__File__Path(f"{time_path}/{areas_path}")
        else:
            return Safe_Str__File__Path(f"{time_path}")

    def path_now(self):
        now       = datetime.now()
        time_path = now.strftime("%Y/%m/%d/%H")
        return time_path
