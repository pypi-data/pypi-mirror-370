import click

from mosamatic.tasks import CopyFilesTask


@click.command(help='Copies files of certain type to the output directory')
@click.option(
    '--input_dir', 
    required=True, 
    type=click.Path(exists=True), 
    help='Directory with files',
)
@click.option(
    '--output_dir', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--extension',
    required=True,
    help='File extension of the files to copy. If "none" specify "file_type"'
)
@click.option(
    '--file_type',
    default='none',
    help='Options: "none", "dicom"'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def copyfiles(input_dir, output_dir, extension, file_type, overwrite):
    """
    Copies files of a certain type to the output directory.
    
    Parameters
    ----------
    input_dir : str
        Directory with input files.

    output_dir : str
        Path to output directory.

    extension : str
        File extension to copy. If "none", you must provide "file_type" parameter.

    file_type : str
        Options: 'none', 'dicom'
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    if extension == 'none':
        if file_type != 'dicom':
            raise RuntimeError(f'If "extension" is "none", parameter "file_type" must be "dicom"')
    task = CopyFilesTask(input_dir, output_dir, extension, file_type, overwrite=overwrite)
    task.run()