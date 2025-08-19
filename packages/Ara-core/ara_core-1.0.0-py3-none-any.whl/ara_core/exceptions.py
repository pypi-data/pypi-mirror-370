class AppError(Exception):
    pass

class FrameUIError(AppError):
    pass

class CallbackError(AppError):
    pass

class TerminateError(AppError):
    pass

class ModuleError(AppError):
    pass

class ModuleInitError(ModuleError):
    pass

class ModuleInputError(ModuleError):
    pass

class ModuleRenderError(ModuleError):
    pass

class ModuleUpdateError(ModuleError):
    pass

class ModuleTerminateError(ModuleError):
    pass