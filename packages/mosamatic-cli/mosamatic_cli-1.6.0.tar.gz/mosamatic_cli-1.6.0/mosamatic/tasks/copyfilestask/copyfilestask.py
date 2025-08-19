import os
import shutil

from mosamatic.tasks.task import Task
from mosamatic.logging import LogManager
from mosamatic.utils import (
    is_dicom, 
)

LOG = LogManager()


class CopyFilesTask(Task):
    def __init__(self, input_dir, output_dir, extension, file_type, overwrite):
        super(CopyFilesTask, self).__init__(
            input={'input_dir': input_dir},
            output=output_dir,
            params={'extension': extension, 'file_type': file_type},
            overwrite=overwrite,
        )

    def run(self):
        # Get file paths
        files = []
        for f in os.listdir(self.input('input_dir')):
            f_path = os.path.join(self.input('input_dir'), f)
            files.append(f_path)
        # Start copying files to output directory
        nr_steps = len(files)
        for step in range(nr_steps):
            source = files[step]
            if os.path.isfile(source):
                extension = self.param('extension')
                if extension == 'none':
                    file_type = self.param('file_type')
                    if file_type == 'dicom':
                        if is_dicom(f_path):
                            shutil.copy(source, self.output())
                    else:
                        raise RuntimeError(f'File extension is "none" but file type is not "dicom"')
                elif source.endswith(extension):
                    shutil.copy(source, self.output())
                else:
                    pass
            self.set_progress(step, nr_steps)