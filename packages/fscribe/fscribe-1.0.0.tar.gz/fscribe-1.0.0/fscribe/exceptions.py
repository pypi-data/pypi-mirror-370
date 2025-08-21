class FscribeException(Exception):
    pass


class FileReadError(FscribeException):
    def __init__(self, file_path: str, original_error: Exception):
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(f"Failed to read file {file_path}: {original_error}")


class DirectoryAnalysisError(FscribeException):
    def __init__(self, directory_path: str, original_error: Exception):
        self.directory_path = directory_path
        self.original_error = original_error
        super().__init__(f"Failed to analyze directory {directory_path}: {original_error}")


class ConfigurationError(FscribeException):
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class OutputWriteError(FscribeException):
    def __init__(self, output_path: str, original_error: Exception):
        self.output_path = output_path
        self.original_error = original_error
        super().__init__(f"Failed to write output to {output_path}: {original_error}")


class InvalidFormatError(FscribeException):
    def __init__(self, format_name: str):
        self.format_name = format_name
        super().__init__(f"Unsupported output format: {format_name}")
