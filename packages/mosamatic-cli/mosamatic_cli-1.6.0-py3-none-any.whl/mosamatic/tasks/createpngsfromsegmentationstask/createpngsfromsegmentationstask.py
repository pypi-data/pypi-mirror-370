import os
import shutil

from mosamatic.tasks.task import Task
from mosamatic.logging import LogManager
from mosamatic.utils import (
    convert_numpy_array_to_png_image, 
    AlbertaColorMap, 
    load_numpy_array,
)

LOG = LogManager()


class CreatePngsFromSegmentationsTask(Task):
    def __init__(self, segmentations_dir, output_dir, fig_width, fig_height, overwrite):
        super(CreatePngsFromSegmentationsTask, self).__init__(
            input={'segmentations_dir': segmentations_dir}, 
            output=output_dir, 
            params={'fig_width': fig_width, 'fig_height': fig_height}, 
            overwrite=overwrite,
        )

    def load_segmentations(self):
        segmentations = []
        for f in os.listdir(self.input('segmentations_dir')):
            f_path = os.path.join(self.input('segmentations_dir'), f)
            if f.endswith('.seg.npy'):
                segmentations.append(f_path)
        if len(segmentations) == 0:
            raise RuntimeError('Input directory has no segmentation files')
        return segmentations

    def run(self):
        segmnentations = self.load_segmentations()
        nr_steps = len(segmnentations)
        for step in range(nr_steps):
            source = segmnentations[step]
            source_name = os.path.split(source)[1]
            source_image = load_numpy_array(source)
            if source_image is not None:
                png_file_name = source_name + '.png'
                convert_numpy_array_to_png_image(
                    source_image, 
                    self.output(),
                    AlbertaColorMap(), 
                    png_file_name,
                    fig_width=int(self.param('fig_width')),
                    fig_height=int(self.param('fig_height')),
                )
            else:
                LOG.warning(f'File {source} is not a valid NumPy array file')
            self.set_progress(step, nr_steps)
