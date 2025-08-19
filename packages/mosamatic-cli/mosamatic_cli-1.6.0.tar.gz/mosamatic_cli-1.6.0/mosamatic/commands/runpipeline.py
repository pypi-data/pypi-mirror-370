import click

from mosamatic.pipelines import DefaultPipeline
from mosamatic.utils import param_dict_from_params, input_dict_from_input


@click.command(help='Runs default body composition pipeline')
@click.option(
    '--images_dir', 
    required=True, 
    type=click.Path(exists=True), 
    help='Input directory with images',
)
@click.option(
    '--model_files_dir', 
    required=True, 
    type=click.Path(exists=True), 
    help='Input directory with model files',
)
@click.option(
    '--output_dir', 
    required=True, 
    type=click.Path(), 
    help='Output directory'
)
@click.option(
    '--model_type', 
    required=True,
    help='AI model type: "tensorflow", "pytorch"'
)
@click.option(
    '--model_version', 
    required=True,
    help='Model version to use'
)
@click.option(
    '--target_size', 
    default=512,
    help='Target size of rescaled images'
)
@click.option(
    '--fig_width', 
    default=10,
    help='Figure width PNG images'
)
@click.option(
    '--fig_height', 
    default=10,
    help='Figure height PNG images'
)
@click.option(
    '--full_scan', 
    default=False,
    help='Whether this is a full scan or a set of individual images'
)
@click.option(
    '--overwrite', 
    type=click.BOOL, 
    default=False, 
    help='Overwrite (true/false)'
)
def runpipeline(images_dir, model_files_dir, output_dir, model_type, model_version, target_size, fig_width, fig_height, full_scan, overwrite):
    """
    Runs default body composition pipeline on images in input directory. The input 
    directory can either contain a set of L3 images (one for each patient) or a set
    of DICOM images corresponding to a single CT scan. In the latter case, provide
    the parameter full_scan=true.
    
    Parameters
    ----------
    images_dir : str
        Input directory with DICOM images.

    model_files_dir : str
        Input directory with AI model files.
    
    output_dir : str
        Path to output directory

    model_type : str
        Model type of AI model: "tensorflow", "pytorch"

    model_version : str
        Model version to use.

    target_size : int
        Target size for PNG images.

    fig_width : int
        Figure width for generated PNG images (default: 10)

    fig_height : int
        Figure height for generated PNG images (default: 10)

    full_scan : bool
        Whether images in input directory correspond to individual patient images or a single full scan.
    
    overwrite : bool
        Overwrite contents output directory true/false
    """
    pipeline = DefaultPipeline(
        images_dir, 
        model_files_dir, 
        output_dir, 
        model_type, 
        model_version, 
        target_size, 
        fig_width, 
        fig_height, 
        full_scan, 
        overwrite
    )
    pipeline.run()