from ara_cli.commands.command import Command
from ara_cli.prompt_extractor import extract_responses
import os

class ExtractCommand(Command):
    def __init__(self, file_name, force=False, write=False, output=None, error_output=None):
        self.file_name = file_name
        self.force = force
        self.write = write
        self.output = output    # Callable for standard output (optional)
        self.error_output = error_output  # Callable for errors (optional)

    def execute(self, *args, **kwargs):
        try:
            extract_responses(self.file_name, True, force=self.force, write=self.write)
            if self.output:
                self.output("End of extraction")
        except Exception as e:
            if self.error_output:
                self.error_output(f"Extraction failed: {e}")
            else:
                raise
