import os
import torch
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


class SegmentMuscleFatL3Task(Task):
    def __init__(self, images_dir, model_files_dir, output_dir, model_version, overwrite):
        super(SegmentMuscleFatL3Task, self).__init__(
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
            if f_path.endswith('.pt') or f_path.endswith('.json'):
                model_files.append(f_path)
        if len(model_files) != 3:
            raise RuntimeError(f'Found {len(model_files)} model files. This should be 3!')
        return model_files

    def load_models_and_params(self, model_files, model_version):
        params = None
        for f_path in model_files:
            f_name = os.path.split(f_path)[1]
            if f_name == f'params-{str(model_version)}.json':
                params = ParamLoader(f_path)
                break
        if params is None:
            raise RuntimeError('Could not load parameters')
        model, contour_model = None, None
        for f_path in model_files:
            f_name = os.path.split(f_path)[1]
            if f_name == f'model-{str(model_version)}.pt':
                model = models.UNet(params, 4).to(device=DEVICE)
                model.load_state_dict(torch.load(f_path, weights_only=False, map_location=torch.device(DEVICE)))
                model.eval()
            elif f_name == f'contour_model-{str(model_version)}.pt':
                contour_model = models.UNet(params, 2).to(device=DEVICE)
                contour_model.load_state_dict(torch.load(f_path, weights_only=False, map_location=torch.device(DEVICE)))
                contour_model.eval()
            else:
                pass
        return model, contour_model, params

    def extract_contour(self, image, contour_model):
        with torch.no_grad():
            # Create 4D Tensor input
            input = np.expand_dims(image, 0)
            input = np.expand_dims(input, 0)
            input = torch.Tensor(input)
            input = input.to(DEVICE, dtype=torch.float)
            # Predict
            prediction = contour_model(input)
            prediction = torch.argmax(prediction, axis=1)
            prediction = prediction.squeeze()
            prediction = prediction.detach().cpu().numpy()
        return image * prediction
    
    def segment_muscle_and_fat(self, image, model):
        input = np.expand_dims(image, 0)
        input = np.expand_dims(input, 0)
        input = torch.Tensor(input)
        input = input.to(DEVICE, dtype=torch.float)
        segmentation = model(input)
        segmentation = torch.argmax(segmentation, axis=1)
        segmentation = segmentation.squeeze()
        segmentation = segmentation.detach().cpu().numpy()
        return segmentation
    
    def process_file(self, f_path, output_dir, model, contour_model, params):
        p = load_dicom(f_path)
        if is_jpeg2000_compressed(p):
            p.decompress()
        image = get_pixels_from_dicom_object(p, normalize=True)
        image = normalize_between(image, params.dict['lower_bound'], params.dict['upper_bound'])
        image = self.extract_contour(image, contour_model)
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