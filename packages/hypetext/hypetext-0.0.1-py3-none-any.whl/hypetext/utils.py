class ResourceFilter:
    def __init__(self):
        self.resources = set()

    def __call__(self, parts):
        for part in parts:
            match part:
                case ("res", resource):
                    if resource not in self.resources:
                        self.resources.add(resource)
                        yield part
                case other:
                    yield other
