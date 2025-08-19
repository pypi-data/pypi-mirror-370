import click

from mosamatic.tasks import SegmentMuscleFatL3TensorFlowTask


@click.command(help='Extracts muscle and fat regions from CT images at L3 (uses PyTorch)')
@click.option(
    '--images_dir', 
    required=True, 
    type=click.Path(), 
    help='Input directory with images'
)
@click.option(
    '--model_files_dir', 
    required=True, 
    type=click.Path(), 
    help='Input directory with AI model files'
)
@click.option(
    '--output_dir', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--model_version', 
    required=True, 
    type=str, 
    help='Model version to use'
)
@click.option(
    '--overwrite', 
    default=False, 
    type=click.BOOL, 
    help='Overwrite (true/false)'
)
def segmentmusclefatl3tensorflow(images_dir, model_files_dir, output_dir, model_version, overwrite):
    """
    Automatically extracts muscle and fat regions from CT images at the L3
    vertebral level. Outputs segmentation files in NumPy (.npy) format. This
    command uses a TensorFlow AI model.
    
    Parameters
    ----------
    images_dir : str
        Path to directory with images.

    model_files_dir : str
        Path to directory with PyTorch model files. This should
            be the following files:
            - model-<version>.zip
            - contour_model-<version>.zip
            - params-<version>.json
    
    output_dir : str
        Path to output directory with segmentation files.

    model_version : str
        Model version to use
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    task = SegmentMuscleFatL3TensorFlowTask(images_dir, model_files_dir, output_dir, model_version, overwrite)
    task.run()