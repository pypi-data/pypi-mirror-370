from collections.abc import Sequence
import enum
from typing import Optional

import lagrange


class FaceVaryingInterpolation(enum.Enum):
    """Face-varying interpolation rule"""

    Smooth = 0

    CornersOnly = 1

    CornersPlus1 = 2

    CornersPlus2 = 3

    Boundaries = 4

    All = 5

class InterpolatedAttributesSelection(enum.Enum):
    """Selection tag for interpolated attributes"""

    All = 0

    Empty = 1

    Selected = 2

class SchemeType(enum.Enum):
    """Subdivision scheme type"""

    Bilinear = 0

    CatmullClark = 1

    Loop = 2

class VertexBoundaryInterpolation(enum.Enum):
    """Vertex boundary interpolation rule"""

    NoInterpolation = 0

    EdgeOnly = 1

    EdgeAndCorner = 2

def subdivide_mesh(mesh: lagrange.core.SurfaceMesh, num_levels: int, scheme: Optional[SchemeType] = None, adaptive: bool = False, max_edge_length: Optional[float] = None, vertex_boundary_interpolation: VertexBoundaryInterpolation = VertexBoundaryInterpolation.EdgeOnly, face_varying_interpolation: FaceVaryingInterpolation = FaceVaryingInterpolation.Smooth, use_limit_surface: bool = False, interpolated_attributes_selection: InterpolatedAttributesSelection = InterpolatedAttributesSelection.All, interpolated_smooth_attributes: Optional[Sequence[int]] = None, interpolated_linear_attributes: Optional[Sequence[int]] = None, edge_sharpness_attr: Optional[int] = None, vertex_sharpness_attr: Optional[int] = None, face_hole_attr: Optional[int] = None, output_limit_normals: Optional[str] = None, output_limit_tangents: Optional[str] = None, output_limit_bitangents: Optional[str] = None) -> lagrange.core.SurfaceMesh:
    """
    Evaluates the subdivision surface of a polygonal mesh.

    :param mesh:                  The source mesh.
    :param num_levels:            The number of levels of subdivision to apply.
    :param scheme:                The subdivision scheme to use.
    :param adaptive:              Whether to use adaptive subdivision.
    :param max_edge_length:       The maximum edge length for adaptive subdivision.
    :param vertex_boundary_interpolation:  Vertex boundary interpolation rule.
    :param face_varying_interpolation:     Face-varying interpolation rule.
    :param use_limit_surface:      Interpolate all data to the limit surface.
    :param edge_sharpness_attr:    Per-edge scalar attribute denoting edge sharpness. Sharpness values must be in [0, 1] (0 means smooth, 1 means sharp).
    :param vertex_sharpness_attr:  Per-vertex scalar attribute denoting vertex sharpness (e.g. for boundary corners). Sharpness values must be in [0, 1] (0 means smooth, 1 means sharp).
    :param face_hole_attr:         Per-face integer attribute denoting face holes. A non-zero value means the facet is a hole. If a face is tagged as a hole, the limit surface will not be generated for that face.
    :param output_limit_normals:   Output name for a newly computed per-vertex attribute containing the normals to the limit surface. Skipped if left empty.
    :param output_limit_tangents:  Output name for a newly computed per-vertex attribute containing the tangents (first derivatives) to the limit surface. Skipped if left empty.
    :param output_limit_bitangents: Output name for a newly computed per-vertex attribute containing the bitangents (second derivative) to the limit surface. Skipped if left empty.

    :return: The subdivided mesh.
    """
