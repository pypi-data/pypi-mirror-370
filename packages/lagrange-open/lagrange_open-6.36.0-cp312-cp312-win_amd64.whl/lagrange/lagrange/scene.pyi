from collections.abc import Iterable, Iterator
import enum
from typing import Annotated, overload

from numpy.typing import ArrayLike

import lagrange


class Animation:
    """Animation"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Animation name"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def extensions(self) -> Extensions:
        """Animation extensions"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

class AnimationList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: AnimationList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Animation], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Animation]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Animation: ...

    @overload
    def __getitem__(self, arg: slice, /) -> AnimationList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Animation, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Animation, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Animation:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: AnimationList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Animation, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: AnimationList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class BufferList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: BufferList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[int], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[int]: ...

    @overload
    def __getitem__(self, arg: int, /) -> int: ...

    @overload
    def __getitem__(self, arg: slice, /) -> BufferList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: int, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: int, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> int:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: BufferList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: int, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: BufferList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: int, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: int, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: int, /) -> None:
        """Remove first occurrence of `arg`."""

class Camera:
    """Camera"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Camera name"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def position(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """
        Camera position. Note that the camera is part of the scene graph, and has an associated transform in its node. This value is relative to the coordinate system defined by the node
        """

    @position.setter
    def position(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def up(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """Camera up vector"""

    @up.setter
    def up(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def look_at(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """Camera look-at point"""

    @look_at.setter
    def look_at(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def near_plane(self) -> float:
        """Distance of the near clipping plane. This value cannot be 0"""

    @near_plane.setter
    def near_plane(self, arg: float, /) -> None: ...

    @property
    def far_plane(self) -> float:
        """Distance of the far clipping plane"""

    @far_plane.setter
    def far_plane(self, arg: float, /) -> None: ...

    @property
    def type(self) -> Camera.Type:
        """Camera type"""

    @type.setter
    def type(self, arg: Camera.Type, /) -> None: ...

    @property
    def aspect_ratio(self) -> float:
        """
        Screen aspect ratio. This is the value of width / height of the screen. aspect_ratio = tan(horizontal_fov / 2) / tan(vertical_fov / 2)
        """

    @aspect_ratio.setter
    def aspect_ratio(self, arg: float, /) -> None: ...

    @property
    def horizontal_fov(self) -> float:
        """
        Horizontal field of view angle, in radians. This is the angle between the left and right borders of the viewport. It should not be greater than Pi. fov is only defined when the camera type is perspective, otherwise it should be 0
        """

    @horizontal_fov.setter
    def horizontal_fov(self, arg: float, /) -> None: ...

    @property
    def orthographic_width(self) -> float:
        """
        Half width of the orthographic view box. Or horizontal magnification. This is only defined when the camera type is orthographic, otherwise it should be 0
        """

    @orthographic_width.setter
    def orthographic_width(self, arg: float, /) -> None: ...

    @property
    def get_vertical_fov(self) -> float:
        """
        Get the vertical field of view. Make sure aspect_ratio is set before calling this
        """

    @property
    def set_horizontal_fov_from_vertical_fov(self, arg: float, /) -> None:
        """
        Set horizontal fov from vertical fov. Make sure aspect_ratio is set before calling this
        """

    @property
    def extensions(self) -> Extensions:
        """Camera extensions"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    class Type(enum.Enum):
        """Camera type"""

        Perspective = 0
        """Perspective projection"""

        Orthographic = 1
        """Orthographic projection"""

class CameraList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: CameraList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Camera], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Camera]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Camera: ...

    @overload
    def __getitem__(self, arg: slice, /) -> CameraList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Camera, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Camera, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Camera:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: CameraList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Camera, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: CameraList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class ElementIdList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ElementIdList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[int], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[int]: ...

    @overload
    def __getitem__(self, arg: int, /) -> int: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ElementIdList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: int, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: int, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> int:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ElementIdList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: int, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ElementIdList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

    def __eq__(self, arg: object, /) -> bool: ...

    def __ne__(self, arg: object, /) -> bool: ...

    @overload
    def __contains__(self, arg: int, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def count(self, arg: int, /) -> int:
        """Return number of occurrences of `arg`."""

    def remove(self, arg: int, /) -> None:
        """Remove first occurrence of `arg`."""

class Extensions:
    def __repr__(self) -> str: ...

    @property
    def size(self) -> int: ...

    @property
    def empty(self) -> bool: ...

    @property
    def data(self) -> ValueUnorderedMap: ...

    @data.setter
    def data(self, arg: ValueUnorderedMap, /) -> None: ...

class FacetAllocationStrategy(enum.Enum):
    EvenSplit = 0

    RelativeToMeshArea = 1

    RelativeToNumFacets = 2

    Synchronized = 3

class Image:
    """
    Image structure that can store either image data or reference to an image file
    """

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Image name. Not guaranteed to be unique and can be empty"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def image(self) -> ImageBuffer:
        """Image data"""

    @image.setter
    def image(self, arg: ImageBuffer, /) -> None: ...

    @property
    def uri(self) -> str | None:
        """
        Image file path. This path is relative to the file that contains the scene. It is only valid if image data should be mapped to an external file
        """

    @uri.setter
    def uri(self, arg: str, /) -> None: ...

    @property
    def extensions(self) -> Extensions:
        """Image extensions"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

class ImageBuffer:
    """Minimalistic image data structure that stores the raw image data"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def width(self) -> int:
        """Image width"""

    @property
    def height(self) -> int:
        """Image height"""

    @property
    def num_channels(self) -> int:
        """Number of image channels (must be 1, 3, or 4)"""

    @property
    def data(self) -> object:
        """
        Raw buffer of size (width * height * num_channels * num_bits_per_element / 8) bytes containing image data
        """

    @data.setter
    def data(self, arg: Annotated[ArrayLike, dict(order='C', device='cpu')], /) -> None: ...

    @property
    def dtype(self) -> type | None:
        """The scalar type of the elements in the buffer"""

class ImageList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ImageList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Image], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Image]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Image: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ImageList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Image, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Image, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Image:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ImageList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Image, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ImageList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class Light:
    """Light"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Light name"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def type(self) -> Light.Type:
        """Light type"""

    @type.setter
    def type(self, arg: Light.Type, /) -> None: ...

    @property
    def position(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """
        Light position. Note that the light is part of the scene graph, and has an associated transform in its node. This value is relative to the coordinate system defined by the node
        """

    @position.setter
    def position(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def direction(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """Light direction"""

    @direction.setter
    def direction(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def up(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """Light up vector"""

    @up.setter
    def up(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def intensity(self) -> float:
        """Light intensity"""

    @intensity.setter
    def intensity(self, arg: float, /) -> None: ...

    @property
    def attenuation_constant(self) -> float:
        """
        Attenuation constant. Intensity of light at a given distance 'd' is: intensity / (attenuation_constant + attenuation_linear * d + attenuation_quadratic * d * d + attenuation_cubic * d * d * d)
        """

    @attenuation_constant.setter
    def attenuation_constant(self, arg: float, /) -> None: ...

    @property
    def attenuation_linear(self) -> float:
        """Linear attenuation factor"""

    @attenuation_linear.setter
    def attenuation_linear(self, arg: float, /) -> None: ...

    @property
    def attenuation_quadratic(self) -> float:
        """Quadratic attenuation factor"""

    @attenuation_quadratic.setter
    def attenuation_quadratic(self, arg: float, /) -> None: ...

    @property
    def attenuation_cubic(self) -> float:
        """Cubic attenuation factor"""

    @attenuation_cubic.setter
    def attenuation_cubic(self, arg: float, /) -> None: ...

    @property
    def range(self) -> float:
        """
        Range is defined for point and spot lights. It defines a distance cutoff at which the light intensity is to be considered zero. When the value is 0, range is assumed to be infinite
        """

    @range.setter
    def range(self, arg: float, /) -> None: ...

    @property
    def color_diffuse(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """Diffuse color"""

    @color_diffuse.setter
    def color_diffuse(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def color_specular(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """Specular color"""

    @color_specular.setter
    def color_specular(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def color_ambient(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """Ambient color"""

    @color_ambient.setter
    def color_ambient(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def angle_inner_cone(self) -> float:
        """
        Inner angle of a spot light's light cone. 2PI for point lights, undefined for directional lights
        """

    @angle_inner_cone.setter
    def angle_inner_cone(self, arg: float, /) -> None: ...

    @property
    def angle_outer_cone(self) -> float:
        """
        Outer angle of a spot light's light cone. 2PI for point lights, undefined for directional lights
        """

    @angle_outer_cone.setter
    def angle_outer_cone(self, arg: float, /) -> None: ...

    @property
    def size(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')]:
        """Size of area light source"""

    @size.setter
    def size(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')], /) -> None: ...

    @property
    def extensions(self) -> Extensions:
        """Light extensions"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    class Type(enum.Enum):
        """Light type"""

        Undefined = 0
        """Undefined light type"""

        Directional = 1
        """Directional light"""

        Point = 2
        """Point light"""

        Spot = 3
        """Spot light"""

        Ambient = 4
        """Ambient light"""

        Area = 5
        """Area light"""

class LightList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: LightList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Light], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Light]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Light: ...

    @overload
    def __getitem__(self, arg: slice, /) -> LightList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Light, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Light, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Light:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: LightList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Light, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: LightList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class Material:
    """
    PBR material, based on the gltf specification. This is subject to change, to support more material models
    """

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Material name. May not be unique, and can be empty"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def base_color_value(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(4), order='C')]:
        """Base color value"""

    @base_color_value.setter
    def base_color_value(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(4), order='C')], /) -> None: ...

    @property
    def base_color_texture(self) -> TextureInfo:
        """Base color texture"""

    @base_color_texture.setter
    def base_color_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def alpha_mode(self) -> Material.AlphaMode:
        """
        The alpha mode specifies how to interpret the alpha value of the base color
        """

    @alpha_mode.setter
    def alpha_mode(self, arg: Material.AlphaMode, /) -> None: ...

    @property
    def alpha_cutoff(self) -> float:
        """Alpha cutoff value"""

    @alpha_cutoff.setter
    def alpha_cutoff(self, arg: float, /) -> None: ...

    @property
    def emissive_value(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')]:
        """Emissive color value"""

    @emissive_value.setter
    def emissive_value(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(3), order='C')], /) -> None: ...

    @property
    def emissive_texture(self) -> TextureInfo:
        """Emissive texture"""

    @emissive_texture.setter
    def emissive_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def metallic_value(self) -> float:
        """Metallic value"""

    @metallic_value.setter
    def metallic_value(self, arg: float, /) -> None: ...

    @property
    def roughness_value(self) -> float:
        """Roughness value"""

    @roughness_value.setter
    def roughness_value(self, arg: float, /) -> None: ...

    @property
    def metallic_roughness_texture(self) -> TextureInfo:
        """
        Metalness and roughness are packed together in a single texture. Green channel has roughness, blue channel has metalness
        """

    @metallic_roughness_texture.setter
    def metallic_roughness_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def normal_texture(self) -> TextureInfo:
        """Normal texture"""

    @normal_texture.setter
    def normal_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def normal_scale(self) -> float:
        """
        Normal scaling factor. normal = normalize(<sampled tex value> * 2 - 1) * vec3(scale, scale, 1)
        """

    @normal_scale.setter
    def normal_scale(self, arg: float, /) -> None: ...

    @property
    def occlusion_texture(self) -> TextureInfo:
        """Occlusion texture"""

    @occlusion_texture.setter
    def occlusion_texture(self, arg: TextureInfo, /) -> None: ...

    @property
    def occlusion_strength(self) -> float:
        """
        Occlusion strength. color = lerp(color, color * <sampled tex value>, strength)
        """

    @occlusion_strength.setter
    def occlusion_strength(self, arg: float, /) -> None: ...

    @property
    def double_sided(self) -> bool:
        """Whether the material is double-sided"""

    @double_sided.setter
    def double_sided(self, arg: bool, /) -> None: ...

    @property
    def extensions(self) -> Extensions:
        """Material extensions"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    class AlphaMode(enum.Enum):
        """Alpha mode"""

        Opaque = 0
        """Alpha is ignored, and rendered output is opaque"""

        Mask = 1
        """
        Output is either opaque or transparent depending on the alpha value and the alpha_cutoff value
        """

        Blend = 2
        """Alpha value is used to composite source and destination"""

class MaterialList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: MaterialList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Material], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Material]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Material: ...

    @overload
    def __getitem__(self, arg: slice, /) -> MaterialList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Material, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Material, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Material:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: MaterialList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Material, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: MaterialList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class MeshInstance3D:
    """A single mesh instance in a scene"""

    def __init__(self) -> None: ...

    @property
    def mesh_index(self) -> int: ...

    @mesh_index.setter
    def mesh_index(self, arg: int, /) -> None: ...

    @property
    def transform(self) -> Annotated[ArrayLike, dict(dtype='float64', order='C', device='cpu')]: ...

    @transform.setter
    def transform(self, arg: Annotated[ArrayLike, dict(dtype='float64', order='C', device='cpu')], /) -> None: ...

class Node:
    """Represents a node in the scene hierarchy"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Node name. May not be unique and can be empty"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def transform(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(4, 4), order='F')]:
        """Transform of the node, relative to its parent"""

    @transform.setter
    def transform(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(4, 4), writable=False)], /) -> None: ...

    @property
    def parent(self) -> int | None:
        """Parent index. May be invalid if the node has no parent (e.g. the root)"""

    @parent.setter
    def parent(self, arg: int, /) -> None: ...

    @property
    def children(self) -> ElementIdList:
        """Children indices. May be empty"""

    @children.setter
    def children(self, arg: ElementIdList, /) -> None: ...

    @property
    def meshes(self) -> SceneMeshInstanceList:
        """List of meshes contained in this node"""

    @meshes.setter
    def meshes(self, arg: SceneMeshInstanceList, /) -> None: ...

    @property
    def cameras(self) -> ElementIdList:
        """List of cameras contained in this node"""

    @cameras.setter
    def cameras(self, arg: ElementIdList, /) -> None: ...

    @property
    def lights(self) -> ElementIdList:
        """List of lights contained in this node"""

    @lights.setter
    def lights(self, arg: ElementIdList, /) -> None: ...

    @property
    def extensions(self) -> Extensions: ...

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

class NodeList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: NodeList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Node], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Node]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Node: ...

    @overload
    def __getitem__(self, arg: slice, /) -> NodeList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Node, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Node, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Node:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: NodeList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Node, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: NodeList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class RemeshingOptions:
    def __init__(self) -> None: ...

    @property
    def facet_allocation_strategy(self) -> FacetAllocationStrategy: ...

    @facet_allocation_strategy.setter
    def facet_allocation_strategy(self, arg: FacetAllocationStrategy, /) -> None: ...

    @property
    def min_facets(self) -> int: ...

    @min_facets.setter
    def min_facets(self, arg: int, /) -> None: ...

class Scene:
    """A 3D scene"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Name of the scene"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def nodes(self) -> NodeList:
        """
        Scene nodes. This is a list of nodes, the hierarchy information is contained by each node having a list of children as indices to this vector
        """

    @nodes.setter
    def nodes(self, arg: NodeList, /) -> None: ...

    @property
    def root_nodes(self) -> ElementIdList:
        """Root nodes. This is typically one. Must be at least one"""

    @root_nodes.setter
    def root_nodes(self, arg: ElementIdList, /) -> None: ...

    @property
    def meshes(self) -> SurfaceMeshList:
        """Scene meshes"""

    @meshes.setter
    def meshes(self, arg: SurfaceMeshList, /) -> None: ...

    @property
    def images(self) -> ImageList:
        """Images"""

    @images.setter
    def images(self, arg: ImageList, /) -> None: ...

    @property
    def textures(self) -> TextureList:
        """Textures. They can reference images"""

    @textures.setter
    def textures(self, arg: TextureList, /) -> None: ...

    @property
    def materials(self) -> MaterialList:
        """Materials. They can reference textures"""

    @materials.setter
    def materials(self, arg: MaterialList, /) -> None: ...

    @property
    def lights(self) -> LightList:
        """Lights in the scene"""

    @lights.setter
    def lights(self, arg: LightList, /) -> None: ...

    @property
    def cameras(self) -> CameraList:
        """Cameras. The first camera (if any) is the default camera view"""

    @cameras.setter
    def cameras(self, arg: CameraList, /) -> None: ...

    @property
    def skeletons(self) -> SkeletonList:
        """Scene skeletons"""

    @skeletons.setter
    def skeletons(self, arg: SkeletonList, /) -> None: ...

    @property
    def animations(self) -> AnimationList:
        """Animations (unused for now)"""

    @animations.setter
    def animations(self, arg: AnimationList, /) -> None: ...

    @property
    def extensions(self) -> Extensions:
        """Scene extensions"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    def add(self, element: Node | lagrange.core.SurfaceMesh | Image | Texture | Material | Light | Camera | Skeleton | Animation) -> int:
        """
        Add an element to the scene.

        :param element: The element to add to the scene. E.g. node, mesh, image, texture, material, light, camera, skeleton, or animation.

        :returns: The id of the added element.
        """

    def add_child(self, parent_id: int, child_id: int) -> None:
        """
        Add a child node to a parent node. The parent-child relationship will be updated for both nodes.

        :param parent_id: The parent node id.
        :param child_id: The child node id.

        :returns: The id of the added child node.
        """

class SceneMeshInstance:
    """Pairs a mesh with its materials (zero, one, or more)"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def mesh(self) -> int | None:
        """
        Mesh index. Has to be a valid index in the scene.meshes vector (None if invalid)
        """

    @mesh.setter
    def mesh(self, arg: int, /) -> None: ...

    @property
    def materials(self) -> ElementIdList:
        """
        Material indices in the scene.materials vector. This is typically a single material index. When a single mesh uses multiple materials, the AttributeName::material_id facet attribute should be defined.
        """

    @materials.setter
    def materials(self, arg: ElementIdList, /) -> None: ...

class SceneMeshInstanceList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: SceneMeshInstanceList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[SceneMeshInstance], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[SceneMeshInstance]: ...

    @overload
    def __getitem__(self, arg: int, /) -> SceneMeshInstance: ...

    @overload
    def __getitem__(self, arg: slice, /) -> SceneMeshInstanceList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: SceneMeshInstance, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: SceneMeshInstance, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> SceneMeshInstance:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: SceneMeshInstanceList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: SceneMeshInstance, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: SceneMeshInstanceList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class SimpleScene3D:
    """Simple scene container for instanced meshes"""

    def __init__(self) -> None: ...

    @property
    def num_meshes(self) -> int:
        """Number of meshes in the scene"""

    def num_instances(self, mesh_index: int) -> int: ...

    @property
    def total_num_instances(self) -> int:
        """Total number of instances for all meshes in the scene"""

    def get_mesh(self, mesh_index: int) -> lagrange.core.SurfaceMesh: ...

    def ref_mesh(self, mesh_index: int) -> lagrange.core.SurfaceMesh: ...

    def get_instance(self, mesh_index: int, instance_index: int) -> MeshInstance3D: ...

    def reserve_meshes(self, num_meshes: int) -> None: ...

    def add_mesh(self, mesh: lagrange.core.SurfaceMesh) -> int: ...

    def reserve_instances(self, mesh_index: int, num_instances: int) -> None: ...

    def add_instance(self, instance: MeshInstance3D) -> int: ...

class Skeleton:
    """Skeleton"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def meshes(self) -> ElementIdList:
        """
        This skeleton is used to deform those meshes. This will typically contain one value, but can have zero or multiple meshes. The value is the index in the scene meshes
        """

    @meshes.setter
    def meshes(self, arg: ElementIdList, /) -> None: ...

    @property
    def extensions(self) -> Extensions:
        """Skeleton extensions"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

class SkeletonList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: SkeletonList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Skeleton], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Skeleton]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Skeleton: ...

    @overload
    def __getitem__(self, arg: slice, /) -> SkeletonList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Skeleton, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Skeleton, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Skeleton:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: SkeletonList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Skeleton, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: SkeletonList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class SurfaceMeshList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: SurfaceMeshList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[lagrange.core.SurfaceMesh], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[lagrange.core.SurfaceMesh]: ...

    @overload
    def __getitem__(self, arg: int, /) -> lagrange.core.SurfaceMesh: ...

    @overload
    def __getitem__(self, arg: slice, /) -> SurfaceMeshList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: lagrange.core.SurfaceMesh, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: lagrange.core.SurfaceMesh, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> lagrange.core.SurfaceMesh:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: SurfaceMeshList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: lagrange.core.SurfaceMesh, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: SurfaceMeshList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class Texture:
    """Texture"""

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def name(self) -> str:
        """Texture name"""

    @name.setter
    def name(self, arg: str, /) -> None: ...

    @property
    def image(self) -> int | None:
        """Index of image in scene.images vector (None if invalid)"""

    @image.setter
    def image(self, arg: int, /) -> None: ...

    @property
    def mag_filter(self) -> Texture.TextureFilter:
        """
        Texture magnification filter, used when texture appears larger on screen than the source image
        """

    @mag_filter.setter
    def mag_filter(self, arg: Texture.TextureFilter, /) -> None: ...

    @property
    def min_filter(self) -> Texture.TextureFilter:
        """
        Texture minification filter, used when the texture appears smaller on screen than the source image
        """

    @min_filter.setter
    def min_filter(self, arg: Texture.TextureFilter, /) -> None: ...

    @property
    def wrap_u(self) -> Texture.WrapMode:
        """Texture wrap mode for U coordinate"""

    @wrap_u.setter
    def wrap_u(self, arg: Texture.WrapMode, /) -> None: ...

    @property
    def wrap_v(self) -> Texture.WrapMode:
        """Texture wrap mode for V coordinate"""

    @wrap_v.setter
    def wrap_v(self, arg: Texture.WrapMode, /) -> None: ...

    @property
    def scale(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')]:
        """Texture scale"""

    @scale.setter
    def scale(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')], /) -> None: ...

    @property
    def offset(self) -> Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')]:
        """Texture offset"""

    @offset.setter
    def offset(self, arg: Annotated[ArrayLike, dict(dtype='float32', shape=(2), order='C')], /) -> None: ...

    @property
    def rotation(self) -> float:
        """Texture rotation"""

    @rotation.setter
    def rotation(self, arg: float, /) -> None: ...

    @property
    def extensions(self) -> Extensions:
        """Texture extensions"""

    @extensions.setter
    def extensions(self, arg: Extensions, /) -> None: ...

    class WrapMode(enum.Enum):
        """Texture wrap mode"""

        Wrap = 0
        """u|v becomes u%1|v%1"""

        Clamp = 1
        """Coordinates outside [0, 1] are clamped to the nearest value"""

        Decal = 2
        """
        If the texture coordinates for a pixel are outside [0, 1], the texture is not applied
        """

        Mirror = 3
        """Mirror wrap mode"""

    class TextureFilter(enum.Enum):
        """Texture filter mode"""

        Undefined = 0
        """Undefined filter"""

        Nearest = 9728
        """Nearest neighbor filtering"""

        Linear = 9729
        """Linear filtering"""

        NearestMipmapNearest = 9984
        """Nearest mipmap nearest filtering"""

        LinearMipmapNearest = 9985
        """Linear mipmap nearest filtering"""

        NearestMipmapLinear = 9986
        """Nearest mipmap linear filtering"""

        LinearMipmapLinear = 9987
        """Linear mipmap linear filtering"""

class TextureInfo:
    """
    Pair of texture index (which texture to use) and texture coordinate index (which set of UVs to use)
    """

    def __init__(self) -> None: ...

    def __repr__(self) -> str: ...

    @property
    def index(self) -> int | None:
        """Texture index. Index in scene.textures vector. `None` if not set"""

    @index.setter
    def index(self, arg: int, /) -> None: ...

    @property
    def texcoord(self) -> int:
        """
        Index of UV coordinates. Usually stored in the mesh as `texcoord_x` attribute where x is this variable. This is typically 0
        """

    @texcoord.setter
    def texcoord(self, arg: int, /) -> None: ...

class TextureList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: TextureList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Texture], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Texture]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Texture: ...

    @overload
    def __getitem__(self, arg: slice, /) -> TextureList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Texture, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Texture, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Texture:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: TextureList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Texture, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: TextureList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class ValueList:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ValueList) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: Iterable[Value], /) -> None:
        """Construct from an iterable object"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the vector is nonempty"""

    def __repr__(self) -> str: ...

    def __iter__(self) -> Iterator[Value]: ...

    @overload
    def __getitem__(self, arg: int, /) -> Value: ...

    @overload
    def __getitem__(self, arg: slice, /) -> ValueList: ...

    def clear(self) -> None:
        """Remove all items from list."""

    def append(self, arg: Value, /) -> None:
        """Append `arg` to the end of the list."""

    def insert(self, arg0: int, arg1: Value, /) -> None:
        """Insert object `arg1` before index `arg0`."""

    def pop(self, index: int = -1) -> Value:
        """Remove and return item at `index` (default last)."""

    def extend(self, arg: ValueList, /) -> None:
        """Extend `self` by appending elements from `arg`."""

    @overload
    def __setitem__(self, arg0: int, arg1: Value, /) -> None: ...

    @overload
    def __setitem__(self, arg0: slice, arg1: ValueList, /) -> None: ...

    @overload
    def __delitem__(self, arg: int, /) -> None: ...

    @overload
    def __delitem__(self, arg: slice, /) -> None: ...

class ValueMap:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ValueMap) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: dict[str, Value], /) -> None:
        """Construct from a dictionary"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the map is nonempty"""

    def __repr__(self) -> str: ...

    @overload
    def __contains__(self, arg: str, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __getitem__(self, arg: str, /) -> Value: ...

    def __delitem__(self, arg: str, /) -> None: ...

    def clear(self) -> None:
        """Remove all items"""

    def __setitem__(self, arg0: str, arg1: Value, /) -> None: ...

    def update(self, arg: ValueMap, /) -> None:
        """Update the map with element from `arg`"""

    class ItemView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[tuple[str, Value]]: ...

    class KeyView:
        @overload
        def __contains__(self, arg: str, /) -> bool: ...

        @overload
        def __contains__(self, arg: object, /) -> bool: ...

        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[str]: ...

    class ValueView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[Value]: ...

    def keys(self) -> ValueMap.KeyView:
        """Returns an iterable view of the map's keys."""

    def values(self) -> ValueMap.ValueView:
        """Returns an iterable view of the map's values."""

    def items(self) -> ValueMap.ItemView:
        """Returns an iterable view of the map's items."""

class ValueUnorderedMap:
    @overload
    def __init__(self) -> None:
        """Default constructor"""

    @overload
    def __init__(self, arg: ValueUnorderedMap) -> None:
        """Copy constructor"""

    @overload
    def __init__(self, arg: dict[str, Value], /) -> None:
        """Construct from a dictionary"""

    def __len__(self) -> int: ...

    def __bool__(self) -> bool:
        """Check whether the map is nonempty"""

    def __repr__(self) -> str: ...

    @overload
    def __contains__(self, arg: str, /) -> bool: ...

    @overload
    def __contains__(self, arg: object, /) -> bool: ...

    def __iter__(self) -> Iterator[str]: ...

    def __getitem__(self, arg: str, /) -> Value: ...

    def __delitem__(self, arg: str, /) -> None: ...

    def clear(self) -> None:
        """Remove all items"""

    def __setitem__(self, arg0: str, arg1: Value, /) -> None: ...

    def update(self, arg: ValueUnorderedMap, /) -> None:
        """Update the map with element from `arg`"""

    class ItemView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[tuple[str, Value]]: ...

    class KeyView:
        @overload
        def __contains__(self, arg: str, /) -> bool: ...

        @overload
        def __contains__(self, arg: object, /) -> bool: ...

        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[str]: ...

    class ValueView:
        def __len__(self) -> int: ...

        def __iter__(self) -> Iterator[Value]: ...

    def keys(self) -> ValueUnorderedMap.KeyView:
        """Returns an iterable view of the map's keys."""

    def values(self) -> ValueUnorderedMap.ValueView:
        """Returns an iterable view of the map's values."""

    def items(self) -> ValueUnorderedMap.ItemView:
        """Returns an iterable view of the map's items."""

def compute_global_node_transform(scene: Scene, node_idx: int) -> Annotated[ArrayLike, dict(dtype='float32', shape=(4, 4), order='F')]:
    """
    Compute the global transform associated with a node.

    :param scene: The input scene.
    :param node_idx: The index of the target node.

    :returns: The global transform of the target node, which is the combination of transforms from this node all the way to the root.
    """

def mesh_to_simple_scene(mesh: lagrange.core.SurfaceMesh) -> SimpleScene3D:
    """
    Converts a single mesh into a simple scene with a single identity instance of the input mesh.

    :param mesh: Input mesh to convert.

    :return: Simple scene containing the input mesh.
    """

def meshes_to_simple_scene(meshes: SurfaceMeshList) -> SimpleScene3D:
    """
    Converts a list of meshes into a simple scene with a single identity instance of each input mesh.

    :param meshes: Input meshes to convert.

    :return: Simple scene containing the input meshes.
    """

def simple_scene_to_mesh(scene: SimpleScene3D, normalize_normals: bool = True, normalize_tangents_bitangents: bool = True, preserve_attributes: bool = True) -> lagrange.core.SurfaceMesh:
    """
    Converts a scene into a concatenated mesh with all the transforms applied.

    :param scene: Scene to convert.
    :param normalize_normals: If enabled, normals are normalized after transformation.
    :param normalize_tangents_bitangents: If enabled, tangents and bitangents are normalized after transformation.
    :param preserve_attributes: Preserve shared attributes and map them to the output mesh.

    :return: Concatenated mesh.
    """
