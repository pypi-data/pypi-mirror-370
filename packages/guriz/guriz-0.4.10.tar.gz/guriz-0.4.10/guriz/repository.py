from .SQL.query import BaseRepository

class Repository(BaseRepository):
    def __init__(self, tablename: str):
        super().__init__(tablename)

    @classmethod
    def attach_model(cls, model_cls):
        repo_instance = cls(model_cls.__tablename__)

        def make_proxy(method_name):
            def proxy(cls, *args, **kwargs): 
                method = getattr(repo_instance, method_name)
                return method(*args, **kwargs)  
            return proxy

        for name in dir(repo_instance):
            if not name.startswith('_') and callable(getattr(repo_instance, name)):
                setattr(model_cls, name, classmethod(make_proxy(name)))

        return model_cls