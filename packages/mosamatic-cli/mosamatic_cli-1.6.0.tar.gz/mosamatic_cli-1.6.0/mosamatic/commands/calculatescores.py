import click

from mosamatic.tasks import CalculateScoresTask


@click.command(help='Calculates body composition scores')
@click.option(
    '--images_dir', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with images',
)
@click.option(
    '--segmentations_dir',
    required=True,
    type=click.Path(exists=True), 
    help='Directory with segmentations',
)
@click.option(
    '--output_dir', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--file_type',
    default='npy',
    help='Options: "npy", "tag"'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def calculatescores(images_dir, segmentations_dir, output_dir, file_type, overwrite):
    """
    Calculates the following body composition scores from muscle and fat
    segmentations extracted using the "segmentmusclefatl3" command:
    
    - Skeletal muscle area
    - Skeletal muscle radiation attenuation
    - Subcutaneous fat area
    - Subcutaneous fat radiation attenuation
    - Visceral fat area
    - Visceral fat radiation attenuation
    
    Parameters
    ----------
    images_dir : str
        Directory with input images.

    segmentations_dir : str
        Directory with input segmentation files.
    
    output_dir : str
        Path to output directory.

    file_type : str
        Options: 'npy', 'tag'
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    task = CalculateScoresTask(images_dir, segmentations_dir, output_dir, file_type, overwrite=overwrite)
    task.run()