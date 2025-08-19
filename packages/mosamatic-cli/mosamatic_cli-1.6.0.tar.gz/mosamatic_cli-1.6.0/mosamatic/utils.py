import os
import binascii
import struct
import time
import click
import math
import warnings
import pydicom
import numpy as np

from PIL import Image


from pydicom.uid import (
    ExplicitVRLittleEndian, ImplicitVRLittleEndian, ExplicitVRBigEndian
)

warnings.filterwarnings("ignore", message="Invalid value for VR UI:", category=UserWarning)

MUSCLE, VAT, SAT = 1, 5, 7


import textwrap

def show_doc_command(cli_group: click.Group) -> click.Command:
    @click.command(name="show-doc")
    @click.argument("command_name", required=False)
    def show_doc(command_name):
        commands = cli_group.commands
        if command_name:
            cmd = commands.get(command_name)
            if cmd and hasattr(cmd, 'callback') and cmd.callback.__doc__:
                print(textwrap.dedent(cmd.callback.__doc__).strip())
            else:
                click.echo(f"No docstring found for command: {command_name}")
        else:
            click.echo("Available commands with docstrings:")
            for name, cmd in commands.items():
                if hasattr(cmd, 'callback') and cmd.callback.__doc__:
                    click.echo(f"  {name}")
            click.echo("\nUse: `mosamatic show-doc <command>` to view a command’s docstring.")
    return show_doc


def current_time_in_milliseconds():
    return int(round(time.time() * 1000))


def current_time_in_seconds() -> int:
    return int(round(current_time_in_milliseconds() / 1000.0))


def elapsed_time_in_milliseconds(start_time_in_milliseconds):
    return current_time_in_milliseconds() - start_time_in_milliseconds


def elapsed_time_in_seconds(start_time_in_seconds):
    return current_time_in_seconds() - start_time_in_seconds


def duration(seconds):
    h = int(math.floor(seconds/3600.0))
    remainder = seconds - h * 3600
    m = int(math.floor(remainder/60.0))
    remainder = remainder - m * 60
    s = int(math.floor(remainder))
    return '{} hours, {} minutes, {} seconds'.format(h, m, s)


def input_dict_from_input(input):
    input_dict = {}
    for item in input:
        if '=' not in item:
            raise click.BadParameter('Inputs must be in the format "name=path"')
        name, path = item.split('=', 1)
        input_dict[name] = path
    return input_dict


def param_dict_from_params(params):
    param_dict = {}
    for item in params:
        if '=' not in item:
            raise click.BadParameter('Parameters must be in the format "name=value"')
        name, value = item.split('=', 1)
        param_dict[name] = value
    return param_dict


def is_dicom(f):
    try:
        pydicom.dcmread(f, stop_before_pixels=True)
        return True
    except pydicom.errors.InvalidDicomError:
        return False
    

def load_dicom(f, stop_before_pixels=False):
    if is_dicom(f):
        return pydicom.dcmread(f, stop_before_pixels=stop_before_pixels)
    return None


def is_jpeg2000_compressed(p):
    return p.file_meta.TransferSyntaxUID not in [ExplicitVRLittleEndian, ImplicitVRLittleEndian, ExplicitVRBigEndian]


def is_numpy_array(value):
    return isinstance(value, np.array)


def load_numpy_array(f):
    try:
        return np.load(f)
    except Exception as e:
        return None


def get_pixels_from_tag_file(tag_file_path):
    f = open(tag_file_path, 'rb')
    f.seek(0)
    byte = f.read(1)
    # Make sure to check the byte-value in Python 3!!
    while byte != b'':
        byte_hex = binascii.hexlify(byte)
        if byte_hex == b'0c':
            break
        byte = f.read(1)
    values = []
    f.read(1)
    while byte != b'':
        v = struct.unpack('b', byte)
        values.append(v)
        byte = f.read(1)
    values = np.asarray(values)
    values = values.astype(np.uint16)
    return values


def get_rescale_params(p):
    rescale_slope = getattr(p, 'RescaleSlope', None)
    rescale_intercept = getattr(p, 'RescaleIntercept', None)
    if rescale_slope is not None and rescale_intercept is not None:
        return rescale_slope, rescale_intercept
    # Try Enhanced DICOM structure
    if 'SharedFunctionalGroupsSequence' in p:
        fg = p.SharedFunctionalGroupsSequence[0]
        if 'PixelValueTransformationSequence' in fg:
            pvt = fg.PixelValueTransformationSequence[0]
            rescale_slope = pvt.get('RescaleSlope', 1)
            rescale_intercept = pvt.get('RescaleIntercept', 0)
            return rescale_slope, rescale_intercept
    return 1, 0


def get_pixels_from_dicom_object(p, normalize=True):
    pixels = p.pixel_array
    if not normalize:
        return pixels
    if normalize is True: # Map pixel values back to original HU values
        rescale_slope, rescale_intercept = get_rescale_params(p)
        return rescale_slope * pixels + rescale_intercept
    if isinstance(normalize, int):
        return (pixels + np.min(pixels)) / (np.max(pixels) - np.min(pixels)) * normalize
    if isinstance(normalize, list):
        return (pixels + np.min(pixels)) / (np.max(pixels) - np.min(pixels)) * normalize[1] + normalize[0]
    return pixels


def convert_labels_to_157(label_image: np.array) -> np.array:
    label_image157 = np.copy(label_image)
    label_image157[label_image157 == 1] = 1
    label_image157[label_image157 == 2] = 5
    label_image157[label_image157 == 3] = 7
    return label_image157


def normalize_between(img: np.array, min_bound: int, max_bound: int) -> np.array:
    img = (img - min_bound) / (max_bound - min_bound)
    img[img > 1] = 0
    img[img < 0] = 0
    c = (img - np.min(img))
    d = (np.max(img) - np.min(img))
    img = np.divide(c, d, np.zeros_like(c), where=d != 0)
    return img


def apply_window_center_and_width(image: np.array, center: int, width: int) -> np.array:
    image_min = center - width // 2
    image_max = center + width // 2
    windowed_image = np.clip(image, image_min, image_max)
    windowed_image = ((windowed_image - image_min) / (image_max - image_min)) * 255.0
    return windowed_image.astype(np.uint8)


def calculate_area(labels: np.array, label, pixel_spacing) -> float:
    mask = np.copy(labels)
    mask[mask != label] = 0
    mask[mask == label] = 1
    area = np.sum(mask) * (pixel_spacing[0] * pixel_spacing[1]) / 100.0
    return area


def calculate_index(area: float, height: float) -> float:
    return area / (height * height)


def calculate_mean_radiation_attenuation(image: np.array, labels: np.array, label: int) -> float:
    mask = np.copy(labels)
    mask[mask != label] = 0
    mask[mask == label] = 1
    subtracted = image * mask
    mask_sum = np.sum(mask)
    if mask_sum > 0.0:
        mean_radiation_attenuation = np.sum(subtracted) / np.sum(mask)
    else:
        # print('Sum of mask pixels is zero, return zero radiation attenuation')
        mean_radiation_attenuation = 0.0
    return mean_radiation_attenuation


def calculate_dice_score(ground_truth: np.array, prediction: np.array, label: int) -> float:
    numerator = prediction[ground_truth == label]
    numerator[numerator != label] = 0
    n = ground_truth[prediction == label]
    n[n != label] = 0
    if np.sum(numerator) != np.sum(n):
        raise RuntimeError('Mismatch in Dice score calculation!')
    denominator = (np.sum(prediction[prediction == label]) + np.sum(ground_truth[ground_truth == label]))
    dice_score = np.sum(numerator) * 2.0 / denominator
    return dice_score


def convert_dicom_to_numpy_array(dicom_file_path: str, window_level: int=50, window_width: int=400, normalize=True) -> np.array:
    p = pydicom.dcmread(dicom_file_path)
    pixels = p.pixel_array
    pixels = pixels.reshape(p.Rows, p.Columns)
    if normalize:
        b = p.RescaleIntercept
        m = p.RescaleSlope
        pixels = m * pixels + b
    pixels = apply_window_center_and_width(pixels, window_level, window_width)
    return pixels


class ColorMap:
    def __init__(self, name: str) -> None:
        self._name = name
        self._values = []

    def name(self) -> str:
        return self._name
    
    def values(self):
        return self._values
    

class GrayScaleColorMap(ColorMap):
    def __init__(self) -> None:
        super(GrayScaleColorMap, self).__init__(name='GrayScaleColorMap')
        # Implement your own gray scale map or let NumPy do this more efficiently?
        pass    

class AlbertaColorMap(ColorMap):
    def __init__(self) -> None:
        super(AlbertaColorMap, self).__init__(name='AlbertaColorMap')
        for i in range(256):
            if i == 1:  # muscle
                self.values().append([255, 0, 0])
            elif i == 2:  # inter-muscular adipose tissue
                self.values().append([0, 255, 0])
            elif i == 5:  # visceral adipose tissue
                self.values().append([255, 255, 0])
            elif i == 7:  # subcutaneous adipose tissue
                self.values().append([0, 255, 255])
            elif i == 12:  # unknown
                self.values().append([0, 0, 255])
            else:
                self.values().append([0, 0, 0])


def apply_color_map(pixels: np.array, color_map: ColorMap) -> np.array:
    pixels_new = np.zeros((*pixels.shape, 3), dtype=np.uint8)
    np.take(color_map.values(), pixels, axis=0, out=pixels_new)
    return pixels_new


def convert_numpy_array_to_png_image(
        numpy_array_file_path_or_object: str, output_dir_path: str, color_map: ColorMap=None, png_file_name: str=None, fig_width: int=10, fig_height: int=10) -> str:
    if isinstance(numpy_array_file_path_or_object, str):
        numpy_array = np.load(numpy_array_file_path_or_object)
    else:
        numpy_array = numpy_array_file_path_or_object
        if not png_file_name:
            raise RuntimeError('PNG file name required for NumPy array object')
    if color_map:
        numpy_array = apply_color_map(pixels=numpy_array, color_map=color_map)
    image = Image.fromarray(numpy_array)
    if not png_file_name:
        numpy_array_file_name = os.path.split(numpy_array_file_path_or_object)[1]
        png_file_name = numpy_array_file_name + '.png'      
    elif not png_file_name.endswith('.png'):
        png_file_name += '.png'
    png_file_path = os.path.join(output_dir_path, png_file_name)
    image.save(png_file_path)
    return png_file_path