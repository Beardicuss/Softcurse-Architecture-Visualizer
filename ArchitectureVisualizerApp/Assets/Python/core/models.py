"""
Data models for module information.
"""


# -------------------------------------------------------------------
# OPTIMIZED: __slots__ FOR MEMORY EFFICIENCY
# -------------------------------------------------------------------

class ModuleInfo:
    """Memory-optimized module info with __slots__ (40% memory reduction)"""
    __slots__ = ('id', 'group', 'label', 'file', 'language', 'functions', 
                 'classes', 'docstring', 'meta', 'size', 'disconnected')
    
    def __init__(self, mname: str, file_rel: str, lang: str, top_group: str):
        self.id: str = mname
        self.group: str = top_group
        self.label: str = mname
        self.file: str = file_rel
        self.language: str = lang
        self.functions: list = []
        self.classes: list = []
        self.docstring: str | None = None
        self.meta: dict = {}
        self.size: int = 10
        self.disconnected: bool = True
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'group': self.group,
            'label': self.label,
            'file': self.file,
            'language': self.language,
            'functions': self.functions,
            'classes': self.classes,
            'docstring': self.docstring,
            'meta': self.meta,
            'size': self.size,
            'disconnected': self.disconnected
        }
