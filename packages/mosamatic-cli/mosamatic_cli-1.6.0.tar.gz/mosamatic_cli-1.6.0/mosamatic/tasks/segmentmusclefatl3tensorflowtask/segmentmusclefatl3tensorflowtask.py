import os
import zipfile
import tempfile
import numpy as np

import models

from mosamatic.tasks.task import Task
from mosamatic.tasks.segmentmusclefatl3task.paramloader import ParamLoader
from mosamatic.utils import (
    is_dicom, 
    load_dicom,
    is_jpeg2000_compressed,
    normalize_between,
    get_pixels_from_dicom_object,
    convert_labels_to_157,
)

DEVICE = 'cpu'


class SegmentMuscleFatL3TensorFlowTask(Task):
    def __init__(self, images_dir, model_files_dir, output_dir, model_version, overwrite):
        super(SegmentMuscleFatL3TensorFlowTask, self).__init__(
            input={'images_dir': images_dir, 'model_files_dir': model_files_dir}, 
            output=output_dir, 
            params={'model_version': model_version}, 
            overwrite=overwrite
        )

    def load_images(self):
        images = []
        for f in os.listdir(self.input('images_dir')):
            f_path = os.path.join(self.input('images_dir'), f)
            if is_dicom(f_path):
                images.append(f_path)
        if len(images) == 0:
            raise RuntimeError('Images directory is empty')
        return images

    def load_model_files(self):
        model_files = []
        for f in os.listdir(self.input('model_files_dir')):
            f_path = os.path.join(self.input('model_files_dir'), f)
            if f_path.endswith('.zip') or f_path.endswith('.json'):
                model_files.append(f_path)
        if len(model_files) != 3:
            raise RuntimeError(f'Found {len(model_files)} model files. This should be 3!')
        return model_files

    def load_models_and_params(self, model_files, model_version):
        tfLoaded = False
        model, contour_model, params = None, None, None
        for f_path in model_files:
            f_name = os.path.split(f_path)[1]
            if f_name == f'model-{str(model_version)}.zip':
                if not tfLoaded:
                    import tensorflow as tf
                    tfLoaded = True
                with tempfile.TemporaryDirectory() as model_dir_unzipped:
                # model_dir_unzipped = os.path.join(os.path.split(f_path)[0], 'model_unzipped')
                    os.makedirs(model_dir_unzipped, exist_ok=True)
                    with zipfile.ZipFile(f_path) as zipObj:
                        zipObj.extractall(path=model_dir_unzipped)
                    model = tf.keras.models.load_model(model_dir_unzipped, compile=False)
            elif f_name == f'contour_model-{str(model_version)}.zip':
                if not tfLoaded:
                    import tensorflow as tf
                    tfLoaded = True
                with tempfile.TemporaryDirectory() as contour_model_dir_unzipped:
                # contour_model_dir_unzipped = os.path.join(os.path.split(f_path)[0], 'contour_model_unzipped')
                    os.makedirs(contour_model_dir_unzipped, exist_ok=True)
                    with zipfile.ZipFile(f_path) as zipObj:
                        zipObj.extractall(path=contour_model_dir_unzipped)
                    contour_model = tf.keras.models.load_model(contour_model_dir_unzipped, compile=False)
            elif f_name == f'params-{model_version}.json':
                params = ParamLoader(f_path)
            else:
                pass
        return model, contour_model, params

    def extract_contour(self, image, contour_model, params):
        ct = np.copy(image)
        ct = normalize_between(ct, params.dict['min_bound_contour'], params.dict['max_bound_contour'])
        img2 = np.expand_dims(ct, 0)
        img2 = np.expand_dims(img2, -1)
        pred = contour_model.predict([img2])
        pred_squeeze = np.squeeze(pred)
        pred_max = pred_squeeze.argmax(axis=-1)
        mask = np.uint8(pred_max)
        return mask

    def segment_muscle_and_fat(self, image, model):
        img2 = np.expand_dims(image, 0)
        img2 = np.expand_dims(img2, -1)
        pred = model.predict([img2])
        pred_squeeze = np.squeeze(pred)
        pred_max = pred_squeeze.argmax(axis=-1)
        return pred_max
        
    def process_file(self, f_path, output_dir, model, contour_model, params):
        p = load_dicom(f_path)
        if is_jpeg2000_compressed(p):
            p.decompress()
        image = get_pixels_from_dicom_object(p, normalize=True)
        if contour_model:
            mask = self.extract_contour(image, contour_model, params)
            image = normalize_between(image, params.dict['min_bound'], params.dict['max_bound'])
            image = image * mask
        image = image.astype(np.float32)
        segmentation = self.segment_muscle_and_fat(image, model)
        segmentation = convert_labels_to_157(segmentation)
        segmentation_file_name = os.path.split(f_path)[1]
        segmentation_file_path = os.path.join(output_dir, f'{segmentation_file_name}.seg.npy')
        np.save(segmentation_file_path, segmentation)

    def run(self):
        images = self.load_images()
        model_files = self.load_model_files()
        model_version = self.param('model_version')
        model, contour_model, params = self.load_models_and_params(model_files, model_version)
        nr_steps = len(images)
        for step in range(nr_steps):
            source = images[step]
            self.process_file(source, self.output(), model, contour_model, params)
            self.set_progress(step, nr_steps)