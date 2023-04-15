class CustomDialogState(dict):
    def __init__(self, *args, **kwargs):
        super(CustomDialogState, self).__init__(*args, **kwargs)
        self.dialog_stack = []
