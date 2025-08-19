import click

from mosamatic.tasks import DecompressDicomFilesTask


@click.command(help='Decompress DICOM files')
@click.option(
    '--images_dir', 
    required=True, 
    type=click.Path(exists=True), 
    help='Input directory with DICOM images'
)
@click.option(
    '--output_dir', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def decompressdicomfiles(images_dir, output_dir, overwrite):
    """
    Decompresses DICOM files.
    
    Parameters
    ----------
    images_dir : str
        Path to directory with DICOM files.
    
    output_dir : str
        Path to output directory.
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    task = DecompressDicomFilesTask(images_dir, output_dir, overwrite)
    task.run()