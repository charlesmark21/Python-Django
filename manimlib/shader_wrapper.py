import os
import logging
import re
import moderngl
import numpy as np
import copy

from manimlib.utils.directories import get_shader_dir
from manimlib.utils.file_ops import seek_full_path_from_defaults

# Mobjects that should be rendered with
# the same shader will be organized and
# clumped together based on keeping track
# of a dict holding all the relevant information
# to that shader


class ShaderWrapper(object):
    def __init__(self,
                 vert_data=None,
                 vert_indices=None,
                 shader_folder=None,
                 uniforms=None,  # A dictionary mapping names of uniform variables
                 texture_paths=None,  # A dictionary mapping names to filepaths for textures.
                 depth_test=False,
                 render_primitive=moderngl.TRIANGLE_STRIP,
                 ):
        self.vert_data = vert_data
        self.vert_indices = vert_indices
        self.vert_attributes = vert_data.dtype.names
        self.shader_folder = shader_folder
        self.uniforms = uniforms or dict()
        self.texture_paths = texture_paths or dict()
        self.depth_test = depth_test
        self.render_primitive = str(render_primitive)
        self.id = self.create_id()
        self.program_id = self.create_program_id()

    def copy(self):
        result = copy.copy(self)
        result.vert_data = np.array(self.vert_data)
        if result.vert_indices is not None:
            result.vert_indices = np.array(self.vert_indices)
        if self.uniforms:
            result.uniforms = dict(self.uniforms)
        if self.texture_paths:
            result.texture_paths = dict(self.texture_paths)
        return result

    def is_valid(self):
        return all([
            self.vert_data is not None,
            self.shader_folder,
        ])

    def get_id(self):
        return self.id

    def get_program_id(self):
        return self.program_id

    def create_id(self):
        # A unique id for a shader
        return "|".join(map(str, [
            self.shader_folder,
            self.uniforms,
            self.texture_paths,
            self.depth_test,
            self.render_primitive,
        ]))

    def refresh_id(self):
        self.id = self.create_id()

    def create_program_id(self):
        return self.shader_folder

    def get_program_code(self):
        def get_code(name):
            return get_shader_code_from_file(
                os.path.join(self.shader_folder, f"{name}.glsl")
            )

        return {
            "vertex_shader": get_code("vert"),
            "geometry_shader": get_code("geom"),
            "fragment_shader": get_code("frag"),
        }

    def combine_with(self, *shader_wrappers):
        # Assume they are of the same type
        if len(shader_wrappers) == 0:
            return
        if self.vert_indices is not None:
            num_verts = len(self.vert_data)
            indices_list = [self.vert_indices]
            data_list = [self.vert_data]
            for sw in shader_wrappers:
                indices_list.append(sw.vert_indices + num_verts)
                data_list.append(sw.vert_data)
                num_verts += len(sw.vert_data)
            self.vert_indices = np.hstack(indices_list)
            self.vert_data = np.hstack(data_list)
        else:
            self.vert_data = np.hstack([self.vert_data, *[sw.vert_data for sw in shader_wrappers]])
        return self


def get_shader_code_from_file(filename):
    if not filename:
        return None

    try:
        filepath = seek_full_path_from_defaults(
            filename,
            directories=[get_shader_dir(), "/"],
            extensions=[],
        )
    except IOError:
        return None

    with open(filepath, "r") as f:
        result = f.read()

    # To share functionality between shaders, some functions are read in
    # from other files an inserted into the relevant strings before
    # passing to ctx.program for compiling
    # Replace "#INSERT " lines with relevant code
    insertions = re.findall(r"^#INSERT .*\.glsl$", result, flags=re.MULTILINE)
    for line in insertions:
        inserted_code = get_shader_code_from_file(
            os.path.join("inserts", line.replace("#INSERT ", ""))
        )
        result = result.replace(line, inserted_code)
    return result
