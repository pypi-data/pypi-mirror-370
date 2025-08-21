class NonCloneableDict(dict):
    def __deepcopy__(self, memodict={}):  # noqa
        return self

    def __copy__(self):
        return self
