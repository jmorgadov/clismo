class OptimizableObject:
    def __init__(self, *childrens_names):
        self.posible_changes = []
        self.childrens_names = list(childrens_names) or []

    def add_possible_change(self, func, attr_name):
        self.posible_changes.append((self, attr_name, func))

    def get_possible_changes(self):
        ans = self.posible_changes
        for child in self.childrens_names:
            child = getattr(self, child)
            if isinstance(child, OptimizableObject):
                ans += child.get_possible_changes()
            elif isinstance(child, list):
                for item in child:
                    if isinstance(item, OptimizableObject):
                        ans += item.get_possible_changes()
        return ans
