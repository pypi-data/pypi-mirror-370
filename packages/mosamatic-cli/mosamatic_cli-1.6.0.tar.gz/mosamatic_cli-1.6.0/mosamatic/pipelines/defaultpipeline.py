import os

from mosamatic.pipelines.pipeline import Pipeline
from mosamatic.tasks import (
    DecompressDicomFilesTask, 
    RescaleDicomFilesTask, 
    SegmentMuscleFatL3Task,
    SegmentMuscleFatL3TensorFlowTask,
    CreatePngsFromSegmentationsTask,
    CalculateScoresTask,
)


class DefaultPipeline(Pipeline):
    def __init__(self, images_dir, model_files_dir, output_dir, model_type, model_version, target_size, fig_width, fig_height, full_scan, overwrite):
        super(DefaultPipeline, self).__init__(
            input={'images_dir': images_dir, 'model_files_dir': model_files_dir}, 
            output=output_dir, 
            params={'model_type': model_type, 'model_version': model_version, 'target_size': target_size, 'fig_width': fig_width, 'fig_height': fig_height, 'full_scan': full_scan}, 
            overwrite=overwrite
        )
        model_type = self.param('model_type')
        segmentation_task_class = SegmentMuscleFatL3Task if model_type == 'pytorch' else SegmentMuscleFatL3TensorFlowTask
        self.add_task(
            DecompressDicomFilesTask(
                images_dir=self.input('images_dir'),
                output_dir=self.output(), 
                overwrite=overwrite,
            )
        )
        self.add_task(
            RescaleDicomFilesTask(
                images_dir=os.path.join(self.output(), 'DecompressDicomFilesTask'), 
                target_size=self.param('target_size'),
                output_dir=self.output(), 
                overwrite=overwrite,
            )
        )
        self.add_task(
            segmentation_task_class(
                images_dir=os.path.join(self.output(), 'RescaleDicomFilesTask'),
                model_files_dir=self.input('model_files_dir'),
                model_version=self.param('model_version'),
                output_dir=self.output(), 
                overwrite=overwrite,
            )
        )
        self.add_task(
            CreatePngsFromSegmentationsTask(
                segmentations_dir=os.path.join(
                    self.output(), 
                    'SegmentMuscleFatL3Task' if model_type == 'pytorch' else 'SegmentMuscleFatL3TensorFlowTask'
                ),
                output_dir=self.output(),
                fig_width=self.param('fig_width'),
                fig_height=self.param('fig_height'),
                overwrite=overwrite,
            )
        )
        self.add_task(
            CalculateScoresTask(
                images_dir=os.path.join(self.output(), 'RescaleDicomFilesTask'),
                segmentations_dir=os.path.join(
                    self.output(), 
                    'SegmentMuscleFatL3Task' if model_type == 'pytorch' else 'SegmentMuscleFatL3TensorFlowTask'
                ),
                output_dir=self.output(), 
                file_type='npy',
                overwrite=overwrite,
            )
        )