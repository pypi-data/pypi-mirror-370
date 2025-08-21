
import dataclasses as dc
from dv_flow.mgr import ExtRgy as DfmExtRgy

@dc.dataclass
class ExtRgy(DfmExtRgy):
    ext_rgy : DfmExtRgy = dc.field(default=None)
    pkg_m : dict = dc.field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()
        self.ext_rgy = DfmExtRgy.inst()

    def addPackage(self, name, pkgfile):
        self.pkg_m[name] = pkgfile

    def hasPackage(self, name, search_path=True):
        if name in self.pkg_m.keys():
            return True
        else:
            return self.ext_rgy.hasPackage(name, search_path)
        
    def findPackagePath(self, name):
        if name in self.pkg_m.keys():
            return self.pkg_m[name]
        else:
            ret = self.ext_rgy.findPackagePath(name)
            return ret

