from collections.abc import Sequence
import enum
import os
import pathlib
from typing import Optional

import lagrange


class FileEncoding(enum.Enum):
    """File encoding type"""

    Binary = 0
    """Binary encoding"""

    Ascii = 1
    """ASCII text encoding"""

class LoadOptions:
    """
    Options used when loading a mesh or a scene. Note that not all options are supported for all backends or filetypes
    """

    def __init__(self) -> None: ...

    @property
    def triangulate(self) -> bool:
        """Triangulate any polygonal facet with > 3 vertices"""

    @triangulate.setter
    def triangulate(self, arg: bool, /) -> None: ...

    @property
    def load_normals(self) -> bool:
        """Load vertex normals"""

    @load_normals.setter
    def load_normals(self, arg: bool, /) -> None: ...

    @property
    def load_tangents(self) -> bool:
        """Load tangents and bitangents"""

    @load_tangents.setter
    def load_tangents(self, arg: bool, /) -> None: ...

    @property
    def load_uvs(self) -> bool:
        """Load texture coordinates"""

    @load_uvs.setter
    def load_uvs(self, arg: bool, /) -> None: ...

    @property
    def load_weights(self) -> bool:
        """Load skinning weights attributes (joints id and weight)"""

    @load_weights.setter
    def load_weights(self, arg: bool, /) -> None: ...

    @property
    def load_materials(self) -> bool:
        """Load material ids as facet attribute"""

    @load_materials.setter
    def load_materials(self, arg: bool, /) -> None: ...

    @property
    def load_vertex_colors(self) -> bool:
        """Load vertex colors as vertex attribute"""

    @load_vertex_colors.setter
    def load_vertex_colors(self, arg: bool, /) -> None: ...

    @property
    def load_object_ids(self) -> bool:
        """Load object ids as facet attribute"""

    @load_object_ids.setter
    def load_object_ids(self, arg: bool, /) -> None: ...

    @property
    def search_path(self) -> pathlib.Path:
        """
        Search path for related files, such as .mtl, .bin, or image textures. By default, searches the same folder as the provided filename
        """

    @search_path.setter
    def search_path(self, arg: str | os.PathLike, /) -> None: ...

class SaveOptions:
    """
    Options used when saving a mesh or a scene. Note that not all options are supported for all backends or filetypes
    """

    def __init__(self) -> None: ...

    @property
    def encoding(self) -> FileEncoding:
        """
        Whether to encode the file as plain text or binary. Some filetypes only support Ascii and will ignore this parameter
        """

    @encoding.setter
    def encoding(self, arg: FileEncoding, /) -> None: ...

    @property
    def output_attributes(self) -> SaveOptions.OutputAttributes:
        """Which attributes to save with the mesh"""

    @output_attributes.setter
    def output_attributes(self, arg: SaveOptions.OutputAttributes, /) -> None: ...

    @property
    def selected_attributes(self) -> list[int]:
        """Attributes to output, usage depends on output_attributes setting"""

    @selected_attributes.setter
    def selected_attributes(self, arg: Sequence[int], /) -> None: ...

    @property
    def attribute_conversion_policy(self) -> SaveOptions.AttributeConversionPolicy:
        """
        The attribute conversion policy to use. While Lagrange SurfaceMesh supports vertex, facet, corner, edge and indexed attributes, many filetypes only support a subset of these attribute types
        """

    @attribute_conversion_policy.setter
    def attribute_conversion_policy(self, arg: SaveOptions.AttributeConversionPolicy, /) -> None: ...

    @property
    def embed_images(self) -> bool:
        """Whether to embed images in the file (if supported by the filetype)"""

    @embed_images.setter
    def embed_images(self, arg: bool, /) -> None: ...

    @property
    def export_materials(self) -> bool:
        """Whether to export materials and textures."""

    @export_materials.setter
    def export_materials(self, arg: bool, /) -> None: ...

    class OutputAttributes(enum.Enum):
        """Which attributes to save with the mesh"""

        All = 0
        """All attributes (default)"""

        SelectedOnly = 1
        """Only attributes listed in selected_attributes"""

    class AttributeConversionPolicy(enum.Enum):
        """
        Attribute conversion policy. Provides options to handle non-supported attributes when saving them
        """

        ExactMatchOnly = 0
        """Ignore mismatched attributes and print a warning"""

        ConvertAsNeeded = 1
        """Convert attribute to supported attribute type when possible"""

def load_mesh(filename: str | os.PathLike, triangulate: bool = False, load_normals: bool = True, load_tangents: bool = True, load_uvs: bool = True, load_weights: bool = True, load_materials: bool = True, load_vertex_colors: bool = True, load_object_ids: bool = True, load_images: bool = True, stitch_vertices: bool = False, search_path: str | os.PathLike = ...) -> lagrange.core.SurfaceMesh:
    """
    Load mesh from a file.

    :param filename:           The input file name.
    :param triangulate:        Whether to triangulate the mesh if it is not already triangulated. Defaults to False.
    :param load_normals:       Whether to load vertex normals from mesh if available. Defaults to True.
    :param load_tangents:      Whether to load tangents and bitangents from mesh if available. Defaults to True.
    :param load_uvs:           Whether to load texture coordinates from mesh if available. Defaults to True.
    :param load_weights:       Whether to load skinning weights attributes from mesh if available. Defaults to True.
    :param load_materials:     Whether to load material ids from mesh if available. Defaults to True.
    :param load_vertex_colors: Whether to load vertex colors from mesh if available. Defaults to True.
    :param load_object_id:     Whether to load object ids from mesh if available. Defaults to True.
    :param load_images:        Whether to load external images if available. Defaults to True.
    :param stitch_vertices:    Whether to stitch vertices based on position. Defaults to False.
    :param search_path:        Optional search path for external references (e.g. .mtl, .bin, etc.). Defaults to None.

    :return SurfaceMesh: The mesh object extracted from the input string.
    """

def load_scene(filename: str | os.PathLike, options: LoadOptions = ...) -> lagrange.scene.Scene:
    """
    Load a scene.

    :param filename:    The input file name.
    :param options:     Load scene options. Check the class for more details.

    :return Scene: The loaded scene object.
    """

def load_simple_scene(filename: str | os.PathLike, triangulate: bool = False, search_path: Optional[str | os.PathLike] = None) -> lagrange.scene.SimpleScene3D:
    """
    Load a simple scene from file.

    :param filename:    The input file name.
    :param triangulate: Whether to triangulate the scene if it is not already triangulated. Defaults to False.
    :param search_path: Optional search path for external references (e.g. .mtl, .bin, etc.). Defaults to None.

    :return SimpleScene: The scene object extracted from the input string.
    """

def mesh_to_string(mesh: lagrange.core.SurfaceMesh, format: str = 'ply', binary: bool = True, exact_match: bool = True, selected_attributes: Optional[Sequence[int]] = None) -> bytes:
    """
    Convert a mesh to a binary string based on specified format.

    :param mesh: The input mesh.
    :param format: Format to use. Supported formats are "obj", "ply", "gltf" and "msh".
    :param binary: Whether to save the mesh in binary format if supported. Defaults to True. Only `msh`, `ply` and `glb` support binary format.
    :param exact_match: Whether to save attributes in their exact form. Some mesh formats may not support all the attribute types. If set to False, attributes will be converted to the closest supported attribute type. Defaults to True.
    :param selected_attributes: A list of attribute ids to save. If not specified, all attributes will be saved. Defaults to None.

    :return str: The string representing the input mesh.
    """

def save_mesh(filename: str | os.PathLike, mesh: lagrange.core.SurfaceMesh, binary: bool = True, exact_match: bool = True, selected_attributes: Optional[Sequence[int]] = None) -> None:
    """
    Save mesh to file.

    Filename extension determines the file format. Supported formats are: `obj`, `ply`, `msh`, `glb` and `gltf`.

    :param filename: The output file name.
    :param mesh: The input mesh.
    :param binary: Whether to save the mesh in binary format if supported. Defaults to True. Only `msh`, `ply` and `glb` support binary format.
    :param exact_match: Whether to save attributes in their exact form. Some mesh formats may not support all the attribute types. If set to False, attributes will be converted to the closest supported attribute type. Defaults to True.
    :param selected_attributes: A list of attribute ids to save. If not specified, all attributes will be saved. Defaults to None.
    """

def save_scene(filename: str | os.PathLike, scene: lagrange.scene.Scene, options: SaveOptions = ...) -> None:
    """
    Save a scene. Supports gltf, glb, obj.

    :param filename:    The output file name.
    :param scene:       The scene to save.
    :param options:     Save options. Check the class for more details.
    """

def save_simple_scene(filename: str | os.PathLike, scene: lagrange.scene.SimpleScene3D, binary: bool = True) -> None:
    """
    Save a simple scene to file. Supports gltf, glb, obj.

    :param filename: The output file name.
    :param scene:    The input scene.
    :param binary:   Whether to save the scene in binary format if supported. Defaults to True. Only `glb` supports binary format.
    """

def scene_to_string(scene: lagrange.scene.Scene, format: str, binary: bool = True, exact_match: bool = True, embed_images: bool = False, selected_attributes: Optional[Sequence[int]] = None) -> bytes:
    """
    Convert a scene to a binary string based on specified format.

    :param scene:    The input scene.
    :param format:   Format to use. Supported formats are "gltf" and "glb".
    :param binary:   Whether to save the scene in binary format if supported. Defaults to True. Only `glb` supports binary format.
    :param exact_match: Whether to save attributes in their exact form. Some mesh formats may not support all the attribute types. If set to False, attributes will be converted to the closest supported attribute type. Defaults to True.
    :param selected_attributes: A list of attribute ids to save. If not specified, all attributes will be saved. Defaults to None.

    :return str: The string representing the input scene.
    """

def string_to_mesh(data: bytes, triangulate: bool = False) -> lagrange.core.SurfaceMesh:
    """
    Convert a binary string to a mesh.

    The binary string should use one of the supported formats. Supported formats include `obj`, `ply`,
    `gltf`, `glb`, `fbx` and `msh`. Format is automatically detected.

    :param data:        A binary string representing the mesh data in a supported format.
    :param triangulate: Whether to triangulate the mesh if it is not already triangulated. Defaults to False.

    :return SurfaceMesh: The mesh object extracted from the input string.
    """

def string_to_scene(data: bytes, triangulate: bool = False) -> lagrange.scene.Scene:
    """
    Convert a binary string to a scene.

    The binary string should use one of the supported formats (i.e. `gltf`, `glb` and `fbx`).

    :param data:        A binary string representing the scene data in a supported format.
    :param triangulate: Whether to triangulate the scene if it is not already triangulated. Defaults to False.

    :return Scene: The scene object extracted from the input string.
    """
