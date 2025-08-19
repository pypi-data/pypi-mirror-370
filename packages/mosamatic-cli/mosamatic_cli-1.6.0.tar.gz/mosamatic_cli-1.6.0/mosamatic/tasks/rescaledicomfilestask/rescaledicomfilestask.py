import os
import shutil
import numpy as np

from scipy.ndimage import zoom

from mosamatic.tasks.task import Task
from mosamatic.utils import (
    is_dicom, 
    load_dicom,
    is_jpeg2000_compressed,
)


class RescaleDicomFilesTask(Task):
    def __init__(self, images_dir, output_dir, target_size, overwrite):
        super(RescaleDicomFilesTask, self).__init__(
            input={'images_dir': images_dir}, 
            output=output_dir, 
            params={'target_size': target_size}, 
            overwrite=overwrite
        )

    def load_images(self):
        images = []
        for f in os.listdir(self.input('images_dir')):
            f_path = os.path.join(self.input('images_dir'), f)
            if os.path.isfile(f_path):
                if is_dicom(f_path):
                    images.append(f_path)
        if len(images) == 0:
            raise RuntimeError('Input directory has no DICOM files')
        return images

    def rescale_image(self, p, target_size):
        pixel_array = p.pixel_array
        hu_array = pixel_array * p.RescaleSlope + p.RescaleIntercept
        hu_air = -1000
        new_rows = max(p.Rows, p.Columns)
        new_cols = max(p.Rows, p.Columns)
        padded_hu_array = np.full((new_rows, new_cols), hu_air, dtype=hu_array.dtype)
        padded_hu_array[:pixel_array.shape[0], :pixel_array.shape[1]] = hu_array
        pixel_array_padded = (padded_hu_array - p.RescaleIntercept) / p.RescaleSlope
        pixel_array_padded = pixel_array_padded.astype(pixel_array.dtype) # Image now has largest dimensions
        pixel_array_rescaled = zoom(pixel_array_padded, zoom=(target_size / new_rows), order=3) # Cubic interpolation
        pixel_array_rescaled = pixel_array_rescaled.astype(pixel_array.dtype)
        original_pixel_spacing = p.PixelSpacing
        new_pixel_spacing = [ps * (new_rows / target_size) for ps in original_pixel_spacing]
        p.PixelSpacing = new_pixel_spacing
        p.PixelData = pixel_array_rescaled.tobytes()
        p.Rows = target_size
        p.Columns = target_size
        return p

    def run(self):
        images = self.load_images()
        target_size = int(self.param('target_size'))
        nr_steps = len(images)
        for step in range(nr_steps):
            source = images[step]
            source_name = os.path.split(source)[1]
            p = load_dicom(source)
            if is_jpeg2000_compressed(p):
                p.decompress()
            pixel_array = p.pixel_array
            if len(pixel_array.shape) == 2:
                if p.Rows != target_size or p.Columns != target_size:
                    p = self.rescale_image(p, target_size)
                    target = os.path.join(self.output(), source_name)
                    p.save_as(target)
                else:
                    target = os.path.join(self.output(), source_name)
                    shutil.copy(source, target)
            self.set_progress(step, nr_steps)
