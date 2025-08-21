class Dotdict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def __getitem__(self, key):
        res = super().__getitem__(key)
        if isinstance(res, dict):
            self[key] = Dotdict(res)
        elif isinstance(res, list):
            for i in range(len(res)):
                if isinstance(res[i], dict):
                    res[i] = Dotdict(res[i])
        return super().__getitem__(key)  # reload value again to get dotdict effect

    def __missing__(self, key):
        return rf"[~~missing-key-{key}~~]"
