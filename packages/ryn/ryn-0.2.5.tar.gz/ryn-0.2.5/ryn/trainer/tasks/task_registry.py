# decorator design pattern
task_factory_registry = {}

def register_task(name):
    def wrapper(cls):
        task_factory_registry[name] = cls()
        return cls
    return wrapper