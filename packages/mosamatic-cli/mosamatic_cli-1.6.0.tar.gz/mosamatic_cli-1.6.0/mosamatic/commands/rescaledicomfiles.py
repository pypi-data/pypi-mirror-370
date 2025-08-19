import click

from mosamatic.tasks import RescaleDicomFilesTask
from mosamatic.utils import param_dict_from_params


@click.command(help='Rescale DICOM files to target size')
@click.option(
    '--images_dir', 
    required=True, 
    type=click.Path(exists=True), 
    help='Input directory with images'
)
@click.option(
    '--output_dir', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--target_size', 
    default=512,
    help='Target size of rescaled images (default: 512)'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def rescaledicomfiles(images_dir, output_dir, target_size, overwrite):
    """
    Rescales DICOM images to 512 x 512 (or any square dimension). Images that are
    already at the target size are copied to the output directory without modification.
    
    Parameters
    ----------
    images_dir : str
        Path to directory with images.
    
    output_dir : str
        Path to output directory.

    target_size : int
        Target size of rescaled images (default: 512)
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    task = RescaleDicomFilesTask(images_dir, output_dir, target_size, overwrite)
    task.run()