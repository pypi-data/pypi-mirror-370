from dataclasses import dataclass


CONFIG_MANAGER = TypeVar('CONFIG_MANAGER', bound=AutoSavingModel)


@dataclass
class Factory:

    @cached_property
    def memo_factory(self)->MemoFactory:
        return MemoFactory()

    def memo(self, dir_path:Path)->FileMemo:
        return self.memo_factory.make_file_memo(dir_path/self.PROPERTY_NAME)


    def make_property_manager(self, dir_path:Path)->CONFIG_MANAGER:
        return self.CONFIG_MANAGER_CLASS.load(self.memo(dir_path))

