class ContextSwitchable:
    def __init__(self, parent):
        self._parent = parent
        self._context = self._determine_context()

    def _determine_context(self):
        parent_class_names = {cls.__name__ for cls in self._parent.__class__.__mro__}
        if "AnalysisWorksheet" in parent_class_names:
            return "worksheet"
        elif "AnalysisWorkstep" in parent_class_names:
            return "workstep"
        else:
            raise ValueError(f"Unsupported parent class: {self._parent.__class__.__name__}")

    @property
    def _getter_workstep(self):
        if self._context == "worksheet":
            return self._parent.current_workstep()
        elif self._context == "workstep":
            return self._parent
        return None

    @property
    def _setter_workstep(self):
        if self._context == "worksheet":
            return self._parent.branch_current_workstep()
        elif self._context == "workstep":
            return self._parent
        return None
