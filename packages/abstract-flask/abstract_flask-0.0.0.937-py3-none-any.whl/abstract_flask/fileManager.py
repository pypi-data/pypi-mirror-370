class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
class fileManager(metaclass=SingletonMeta):
    def __init__(self, allowed_extentions=None):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.allowed_extentions = allowed_extentions or {'ods','csv','xls','xlsx','xlsb'}        
