
import itertools as it
import numpy as np
import operator as op

# import aggdraw
import copy
import time

from PIL import Image
from colour import Color
from scipy.spatial.distance import pdist
import cairo

from constants import *
from mobject.types.image_mobject import AbstractImageMobject
from mobject.mobject import Mobject
from mobject.types.point_cloud_mobject import PMobject
from mobject.types.vectorized_mobject import VMobject
from utils.color import color_to_int_rgba
from utils.color import rgb_to_hex
from utils.config_ops import digest_config
from utils.images import get_full_raster_image_path
from utils.iterables import batch_by_property
from utils.iterables import list_difference_update
from utils.iterables import remove_list_redundancies
from utils.simple_functions import fdiv
from utils.space_ops import angle_of_vector
from functools import reduce


class Camera(object):
    CONFIG = {
        "background_image": None,
        "pixel_height": DEFAULT_PIXEL_HEIGHT,
        "pixel_width": DEFAULT_PIXEL_WIDTH,
        # Note: frame height and width will be resized to match
        # the pixel aspect ratio
        "frame_height": FRAME_HEIGHT,
        "frame_width": FRAME_WIDTH,
        "frame_center": ORIGIN,
        "background_color": BLACK,
        "background_opacity": 1,
        # Points in vectorized mobjects with norm greater
        # than this value will be rescaled.
        "max_allowable_norm": FRAME_WIDTH,
        "image_mode": "RGBA",
        "n_channels": 4,
        "pixel_array_dtype": 'uint8',
        "use_z_coordinate_for_display_order": False,
        # z_buff_func is only used if the flag above is set to True.
        # round z coordinate to nearest hundredth when comparring
        "z_buff_func": lambda m: np.round(m.get_center()[2], 2),
        "cairo_line_width_multiple": 0.01,
    }

    def __init__(self, background=None, **kwargs):
        digest_config(self, kwargs, locals())
        self.rgb_max_val = np.iinfo(self.pixel_array_dtype).max
        self.cairo_context = None  # For vectorized rendering
        self.init_background()
        self.resize_frame_shape()
        self.reset()

    def __deepcopy__(self, memo):
        # This is to address a strange bug where deepcopying
        # will result in a segfault, which is somehow related
        # to the aggdraw library
        self.canvas = None
        return copy.copy(self)

    def reset_pixel_shape(self, new_height, new_width):
        self.pixel_width = new_width
        self.pixel_height = new_height
        self.init_background()
        self.resize_frame_shape()
        self.reset()

    def get_pixel_height(self):
        return self.pixel_height

    def get_pixel_width(self):
        return self.pixel_width

    def get_frame_height(self):
        return self.frame_height

    def get_frame_width(self):
        return self.frame_width

    def get_frame_center(self):
        return self.frame_center

    def set_frame_height(self, frame_height):
        self.frame_height = frame_height

    def set_frame_width(self, frame_width):
        self.frame_width = frame_width

    def set_frame_center(self, frame_center):
        self.frame_center = frame_center

    def resize_frame_shape(self, fixed_dimension=0):
        """
        Changes frame_shape to match the aspect ratio
        of the pixels, where fixed_dimension determines
        whether frame_height or frame_width
        remains fixed while the other changes accordingly.
        """
        pixel_height = self.get_pixel_height()
        pixel_width = self.get_pixel_width()
        frame_height = self.get_frame_height()
        frame_width = self.get_frame_width()
        aspect_ratio = fdiv(pixel_width, pixel_height)
        if fixed_dimension == 0:
            frame_height = frame_width / aspect_ratio
        else:
            frame_width = aspect_ratio * frame_height
        self.set_frame_height(frame_height)
        self.set_frame_width(frame_width)

    def init_background(self):
        height = self.get_pixel_height()
        width = self.get_pixel_width()
        if self.background_image is not None:
            path = get_full_raster_image_path(self.background_image)
            image = Image.open(path).convert(self.image_mode)
            # TODO, how to gracefully handle backgrounds
            # with different sizes?
            self.background = np.array(image)[:height, :width]
            self.background = self.background.astype(self.pixel_array_dtype)
        else:
            background_rgba = color_to_int_rgba(
                self.background_color, self.background_opacity
            )
            self.background = np.zeros(
                (height, width, self.n_channels),
                dtype=self.pixel_array_dtype
            )
            self.background[:, :] = background_rgba

    def get_image(self):
        return Image.fromarray(
            self.pixel_array,
            mode=self.image_mode
        )

    def get_pixel_array(self):
        return self.pixel_array

    def convert_pixel_array(self, pixel_array, convert_from_floats=False):
        retval = np.array(pixel_array)
        if convert_from_floats:
            retval = np.apply_along_axis(
                lambda f: (f * self.rgb_max_val).astype(self.pixel_array_dtype),
                2,
                retval
            )
        return retval

    def set_pixel_array(self, pixel_array, convert_from_floats=False):
        converted_array = self.convert_pixel_array(
            pixel_array, convert_from_floats)
        if not (hasattr(self, "pixel_array") and self.pixel_array.shape == converted_array.shape):
            self.pixel_array = converted_array
            self.cairo_context = None
        else:
            # Set in place
            self.pixel_array[:, :, :] = converted_array[:, :, :]

    def set_background(self, pixel_array, convert_from_floats=False):
        self.background = self.convert_pixel_array(
            pixel_array, convert_from_floats)

    def make_background_from_func(self, coords_to_colors_func):
        """
        Sets background by using coords_to_colors_func to determine each pixel's color. Each input
        to coords_to_colors_func is an (x, y) pair in space (in ordinary space coordinates; not
        pixel coordinates), and each output is expected to be an RGBA array of 4 floats.
        """

        print("Starting set_background; for reference, the current time is ", time.strftime("%H:%M:%S"))
        coords = self.get_coords_of_all_pixels()
        new_background = np.apply_along_axis(
            coords_to_colors_func,
            2,
            coords
        )
        print("Ending set_background; for reference, the current time is ", time.strftime("%H:%M:%S"))

        return self.convert_pixel_array(new_background, convert_from_floats=True)

    def set_background_from_func(self, coords_to_colors_func):
        self.set_background(
            self.make_background_from_func(coords_to_colors_func))

    def reset(self):
        self.set_pixel_array(self.background)
        return self

    ####

    def extract_mobject_family_members(self, mobjects, only_those_with_points=False):
        if only_those_with_points:
            method = Mobject.family_members_with_points
        else:
            method = Mobject.submobject_family
        return remove_list_redundancies(list(
            it.chain(*[
                method(m)
                for m in mobjects
                if not (isinstance(m, VMobject) and m.is_subpath)
            ])
        ))

    def get_mobjects_to_display(
        self, mobjects,
        include_submobjects=True,
        excluded_mobjects=None,
    ):
        if include_submobjects:
            mobjects = self.extract_mobject_family_members(
                mobjects, only_those_with_points=True
            )
            if excluded_mobjects:
                all_excluded = self.extract_mobject_family_members(
                    excluded_mobjects
                )
                mobjects = list_difference_update(mobjects, all_excluded)
        if self.use_z_coordinate_for_display_order:
            # Should perhaps think about what happens here when include_submobjects is False,
            # (for now, the onus is then on the caller to ensure this is handled correctly by
            # passing us an appropriately pre-flattened list of mobjects if need be)
            return sorted(
                mobjects,
                lambda a, b: cmp(self.z_buff_func(a), self.z_buff_func(b))
            )
        else:
            return mobjects

    def is_in_frame(self, mobject):
        fc = self.get_frame_center()
        fh = self.get_frame_height()
        fw = self.get_frame_width()
        return not reduce(op.or_, [
            mobject.get_right()[0] < fc[0] - fw,
            mobject.get_bottom()[1] > fc[1] + fh,
            mobject.get_left()[0] > fc[0] + fw,
            mobject.get_top()[1] < fc[1] - fh,
        ])

    def capture_mobject(self, mobject, **kwargs):
        return self.capture_mobjects([mobject], **kwargs)

    def capture_mobjects(self, mobjects, **kwargs):
        mobjects = self.get_mobjects_to_display(mobjects, **kwargs)

        # Organize this list into batches of the same type, and
        # apply corresponding function to those batches
        type_func_pairs = [
            (VMobject, self.display_multiple_vectorized_mobjects),
            (PMobject, self.display_multiple_point_cloud_mobjects),
            (AbstractImageMobject, self.display_multiple_image_mobjects),
            (Mobject, lambda batch: batch),  # Do nothing
        ]

        def get_mobject_type(mobject):
            for mobject_type, func in type_func_pairs:
                if isinstance(mobject, mobject_type):
                    return mobject_type
            raise Exception(
                "Trying to display something which is not of type Mobject"
            )
        batch_type_pairs = batch_by_property(mobjects, get_mobject_type)

        # Display in these batches
        for batch, batch_type in batch_type_pairs:
            # check what the type is, and call the appropriate function
            for mobject_type, func in type_func_pairs:
                if batch_type == mobject_type:
                    func(batch)

    # Methods associated with svg rendering

    def create_new_cairo_context(self):
        # TODO, make sure this isn't run too much
        pw = self.get_pixel_width()
        ph = self.get_pixel_height()
        fw = self.get_frame_width()
        fh = self.get_frame_height()
        surface = cairo.ImageSurface.create_for_data(
            self.pixel_array,
            cairo.FORMAT_ARGB32,
            pw, ph
        )
        ctx = cairo.Context(surface)
        ctx.scale(pw, ph)
        ctx.set_matrix(cairo.Matrix(
            fdiv(pw, fw), 0,
            0, -fdiv(ph, fh),
            pw / 2, ph / 2,
        ))
        return ctx

    def get_cairo_context(self):
        if self.cairo_context is None:
            ctx = self.create_new_cairo_context()
            self.cairo_context = ctx
        else:
            ctx = self.cairo_context
        return ctx

    def display_multiple_vectorized_mobjects(self, vmobjects):
        if len(vmobjects) == 0:
            return
        batch_file_pairs = batch_by_property(
            vmobjects,
            lambda vm: vm.get_background_image_file()
        )
        for batch, file_name in batch_file_pairs:
            if file_name:
                self.display_multiple_background_colored_vmobject(batch)
            else:
                self.display_multiple_non_background_colored_vmobjects(batch)

    def display_multiple_non_background_colored_vmobjects(self, vmobjects):
        for vmobject in vmobjects:
            self.display_vectorized(vmobject)

    def display_vectorized(self, vmobject):
        if vmobject.is_subpath:
            # Subpath vectorized mobjects are taken care
            # of by their parent
            return
        ctx = self.get_cairo_context()
        self.set_cairo_context_path(ctx, vmobject)
        self.apply_stroke(ctx, vmobject, background=True)
        self.apply_fill(ctx, vmobject)
        self.apply_stroke(ctx, vmobject)
        ctx.new_path()
        return self

    def set_cairo_context_path(self, ctx, vmobject):
        for vmob in it.chain([vmobject], vmobject.get_subpath_mobjects()):
            points = vmob.points
            ctx.new_sub_path()
            ctx.move_to(*points[0][:2])
            for triplet in zip(points[1::3], points[2::3], points[3::3]):
                ctx.curve_to(*it.chain(*[
                    point[:2] for point in triplet
                ]))
            if vmob.is_closed():
                ctx.close_path()
        return self

    def set_cairo_context_color(self, ctx, rgbas, vmobject):
        if len(rgbas) == 1:
            # Use reversed rgb because cairo surface is
            # encodes it in reverse order
            ctx.set_source_rgba(
                *rgbas[0][2::-1], rgbas[0][3]
            )
        else:
            points = vmobject.get_gradient_start_and_end_points()
            pat = cairo.LinearGradient(*it.chain(*[
                point[:2] for point in points
            ]))
            offsets = np.linspace(1, 0, len(rgbas))
            for rgba, offset in zip(rgbas, offsets):
                pat.add_color_stop_rgba(
                    offset, *rgba[2::-1], rgba[3]
                )
            ctx.set_source(pat)
        return self

    def apply_fill(self, ctx, vmobject):
        self.set_cairo_context_color(
            ctx, self.get_fill_rgbas(vmobject), vmobject
        )
        ctx.fill_preserve()
        return self

    def apply_stroke(self, ctx, vmobject, background=False):
        width = vmobject.get_stroke_width(background)
        self.set_cairo_context_color(
            ctx,
            self.get_stroke_rgbas(vmobject, background=background),
            vmobject
        )
        ctx.set_line_width(
            width * self.cairo_line_width_multiple
        )
        ctx.stroke_preserve()
        return self

    def get_stroke_rgbas(self, vmobject, background=False):
        return vmobject.get_stroke_rgbas(background)

    def get_fill_rgbas(self, vmobject):
        return vmobject.get_fill_rgbas()

    def get_background_colored_vmobject_displayer(self):
        # Quite wordy to type out a bunch
        bcvd = "background_colored_vmobject_displayer"
        if not hasattr(self, bcvd):
            setattr(self, bcvd, BackgroundColoredVMobjectDisplayer(self))
        return getattr(self, bcvd)

    def display_multiple_background_colored_vmobject(self, cvmobjects):
        displayer = self.get_background_colored_vmobject_displayer()
        cvmobject_pixel_array = displayer.display(*cvmobjects)
        self.overlay_rgba_array(cvmobject_pixel_array)
        return self

    # Methods for other rendering

    def display_multiple_point_cloud_mobjects(self, pmobjects):
        for pmobject in pmobjects:
            self.display_point_cloud(
                pmobject.points,
                pmobject.rgbas,
                self.adjusted_thickness(pmobject.stroke_width)
            )

    def display_point_cloud(self, points, rgbas, thickness):
        if len(points) == 0:
            return
        pixel_coords = self.points_to_pixel_coords(points)
        pixel_coords = self.thickened_coordinates(
            pixel_coords, thickness
        )
        rgba_len = self.pixel_array.shape[2]

        rgbas = (self.rgb_max_val * rgbas).astype(self.pixel_array_dtype)
        target_len = len(pixel_coords)
        factor = target_len / len(rgbas)
        rgbas = np.array([rgbas] * factor).reshape((target_len, rgba_len))

        on_screen_indices = self.on_screen_pixels(pixel_coords)
        pixel_coords = pixel_coords[on_screen_indices]
        rgbas = rgbas[on_screen_indices]

        ph = self.get_pixel_height()
        pw = self.get_pixel_width()

        flattener = np.array([1, pw], dtype='int')
        flattener = flattener.reshape((2, 1))
        indices = np.dot(pixel_coords, flattener)[:, 0]
        indices = indices.astype('int')

        new_pa = self.pixel_array.reshape((ph * pw, rgba_len))
        new_pa[indices] = rgbas
        self.set_pixel_array(new_pa.reshape((ph, pw, rgba_len)))

    def display_multiple_image_mobjects(self, image_mobjects):
        for image_mobject in image_mobjects:
            self.display_image_mobject(image_mobject)

    def display_image_mobject(self, image_mobject):
        corner_coords = self.points_to_pixel_coords(image_mobject.points)
        ul_coords, ur_coords, dl_coords = corner_coords
        right_vect = ur_coords - ul_coords
        down_vect = dl_coords - ul_coords
        center_coords = ul_coords + (right_vect + down_vect) / 2

        sub_image = Image.fromarray(
            image_mobject.get_pixel_array(),
            mode="RGBA"
        )

        # Reshape
        pixel_width = max(int(pdist([ul_coords, ur_coords])), 1)
        pixel_height = max(int(pdist([ul_coords, dl_coords])), 1)
        sub_image = sub_image.resize(
            (pixel_width, pixel_height), resample=Image.BICUBIC
        )

        # Rotate
        angle = angle_of_vector(right_vect)
        adjusted_angle = -int(360 * angle / TAU)
        if adjusted_angle != 0:
            sub_image = sub_image.rotate(
                adjusted_angle, resample=Image.BICUBIC, expand=1
            )

        # TODO, there is no accounting for a shear...

        # Paste into an image as large as the camear's pixel array
        full_image = Image.fromarray(
            np.zeros((self.get_pixel_height(), self.get_pixel_width())),
            mode="RGBA"
        )
        new_ul_coords = center_coords - np.array(sub_image.size) / 2
        new_ul_coords = new_ul_coords.astype(int)
        full_image.paste(
            sub_image,
            box=(
                new_ul_coords[0],
                new_ul_coords[1],
                new_ul_coords[0] + sub_image.size[0],
                new_ul_coords[1] + sub_image.size[1],
            )
        )
        # Paint on top of existing pixel array
        self.overlay_PIL_image(full_image)

    def overlay_rgba_array(self, arr):
        self.overlay_PIL_image(Image.fromarray(arr, mode="RGBA"))

    def overlay_PIL_image(self, image):
        self.pixel_array[:, :] = np.array(
            Image.alpha_composite(self.get_image(), image),
            dtype='uint8'
        )

    def adjust_out_of_range_points(self, points):
        if not np.any(points > self.max_allowable_norm):
            return points
        norms = np.apply_along_axis(np.linalg.norm, 1, points)
        violator_indices = norms > self.max_allowable_norm
        violators = points[violator_indices, :]
        violator_norms = norms[violator_indices]
        reshaped_norms = np.repeat(
            violator_norms.reshape((len(violator_norms), 1)),
            points.shape[1], 1
        )
        rescaled = self.max_allowable_norm * violators / reshaped_norms
        points[violator_indices] = rescaled
        return points

    def points_to_pixel_coords(self, points):
        shifted_points = points - self.get_frame_center()

        result = np.zeros((len(points), 2))
        pixel_height = self.get_pixel_height()
        pixel_width = self.get_pixel_width()
        frame_height = self.get_frame_height()
        frame_width = self.get_frame_width()
        width_mult = pixel_width / frame_width
        width_add = pixel_width / 2
        height_mult = pixel_height / frame_height
        height_add = pixel_height / 2
        # Flip on y-axis as you go
        height_mult *= -1

        result[:, 0] = shifted_points[:, 0] * width_mult + width_add
        result[:, 1] = shifted_points[:, 1] * height_mult + height_add
        return result.astype('int')

    def on_screen_pixels(self, pixel_coords):
        return reduce(op.and_, [
            pixel_coords[:, 0] >= 0,
            pixel_coords[:, 0] < self.get_pixel_width(),
            pixel_coords[:, 1] >= 0,
            pixel_coords[:, 1] < self.get_pixel_height(),
        ])

    def adjusted_thickness(self, thickness):
        # TODO: This seems...unsystematic
        big_sum = op.add(
            PRODUCTION_QUALITY_CAMERA_CONFIG["pixel_height"],
            PRODUCTION_QUALITY_CAMERA_CONFIG["pixel_width"],
        )
        this_sum = op.add(
            self.get_pixel_height(),
            self.get_pixel_width(),
        )
        factor = fdiv(big_sum, this_sum)
        return 1 + (thickness - 1) / factor

    def get_thickening_nudges(self, thickness):
        _range = list(range(-thickness / 2 + 1, thickness / 2 + 1))
        return np.array(list(it.product(_range, _range)))

    def thickened_coordinates(self, pixel_coords, thickness):
        nudges = self.get_thickening_nudges(thickness)
        pixel_coords = np.array([
            pixel_coords + nudge
            for nudge in nudges
        ])
        size = pixel_coords.size
        return pixel_coords.reshape((size / 2, 2))

    def get_coords_of_all_pixels(self):
        # These are in x, y order, to help me keep things straight
        full_space_dims = np.array([
            self.get_frame_width(),
            self.get_frame_height()
        ])
        full_pixel_dims = np.array([
            self.get_pixel_width(),
            self.get_pixel_height()
        ])

        # These are addressed in the same y, x order as in pixel_array, but the values in them
        # are listed in x, y order
        uncentered_pixel_coords = np.indices(
            [self.get_pixel_height(), self.get_pixel_width()]
        )[::-1].transpose(1, 2, 0)
        uncentered_space_coords = fdiv(
            uncentered_pixel_coords * full_space_dims,
            full_pixel_dims)
        # Could structure above line's computation slightly differently, but figured (without much
        # thought) multiplying by frame_shape first, THEN dividing by pixel_shape, is probably
        # better than the other order, for avoiding underflow quantization in the division (whereas
        # overflow is unlikely to be a problem)

        centered_space_coords = (
            uncentered_space_coords - fdiv(full_space_dims, 2)
        )

        # Have to also flip the y coordinates to account for pixel array being listed in
        # top-to-bottom order, opposite of screen coordinate convention
        centered_space_coords = centered_space_coords * (1, -1)

        return centered_space_coords


# TODO
class BackgroundColoredVMobjectDisplayer(object):
    def __init__(self, camera):
        self.camera = camera
        self.file_name_to_pixel_array_map = {}
        self.init_canvas()

    def init_canvas(self):
        self.pixel_array = np.zeros(
            self.camera.pixel_array.shape,
            dtype=self.camera.pixel_array_dtype,
        )
        self.reset_canvas()

    def reset_canvas(self):
        image = Image.fromarray(self.pixel_array, mode=self.camera.image_mode)
        self.canvas = aggdraw.Draw(image)

    def resize_background_array(
        self, background_array,
        new_width, new_height,
        mode="RGBA"
    ):
        image = Image.fromarray(background_array)
        image = image.convert(mode)
        resized_image = image.resize((new_width, new_height))
        return np.array(resized_image)

    def resize_background_array_to_match(self, background_array, pixel_array):
        height, width = pixel_array.shape[:2]
        mode = "RGBA" if pixel_array.shape[2] == 4 else "RGB"
        return self.resize_background_array(background_array, width, height, mode)

    def get_background_array(self, file_name):
        if file_name in self.file_name_to_pixel_array_map:
            return self.file_name_to_pixel_array_map[file_name]
        full_path = get_full_raster_image_path(file_name)
        image = Image.open(full_path)
        array = np.array(image)

        camera = self.camera
        if not np.all(camera.pixel_array.shape == array.shape):
            array = self.resize_background_array_to_match(
                array, camera.pixel_array)

        self.file_name_to_pixel_array_map[file_name] = array
        return array

    def display(self, *cvmobjects):
        batch_image_file_pairs = batch_by_property(
            cvmobjects, lambda cv: cv.get_background_image_file()
        )
        curr_array = None
        for batch, image_file in batch_image_file_pairs:
            background_array = self.get_background_array(image_file)
            for cvmobject in batch:
                self.camera.display_vectorized(cvmobject, self.canvas)
            self.canvas.flush()
            new_array = np.array(
                (background_array * self.pixel_array.astype('float') / 255),
                dtype=self.camera.pixel_array_dtype
            )
            if curr_array is None:
                curr_array = new_array
            else:
                curr_array = np.maximum(curr_array, new_array)
            self.pixel_array[:, :] = 0
            self.reset_canvas()
        return curr_array
