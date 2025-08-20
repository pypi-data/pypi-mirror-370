class FitzInputModule:
    __name__ = "custom_fitzzzz"  # Fake module name for logging

    def __init__(self, preloaded_text):
        self.text = preloaded_text

    def to_text(self, file_path):
        return self.text
