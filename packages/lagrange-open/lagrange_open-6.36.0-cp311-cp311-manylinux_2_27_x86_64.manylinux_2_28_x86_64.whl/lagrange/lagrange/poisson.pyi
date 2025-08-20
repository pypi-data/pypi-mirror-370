from typing import Annotated

from numpy.typing import ArrayLike

import lagrange


def mesh_from_oriented_points(points: Annotated[ArrayLike, dict(dtype='float64', order='C', device='cpu')], normals: Annotated[ArrayLike, dict(dtype='float64', order='C', device='cpu')], octree_depth: int = 0, samples_per_node: float = 1.5, interpolation_weight: float = 2.0, use_normal_length_as_confidence: bool = False, use_dirichlet_boundary: bool = False, colors: Annotated[ArrayLike, dict(order='C', device='cpu')] | None = None, output_vertex_depth_attribute_name: str = '', verbose: bool = False) -> lagrange.core.SurfaceMesh:
    """
    Creates a triangle mesh from an oriented point cloud using Poisson surface reconstruction.

    :param points: Input point cloud positions (N x 3 matrix).
    :param normals: Input point cloud normals (N x 3 matrix).
    :param samples_per_node: Number of samples per node.
    :param octree_depth: Maximum octree depth. (If the value is zero then log base 4 of the point count is used.)
    :param interpolation_weight: Point interpolation weight (lambda).
    :param use_normal_length_as_confidence: Use normal length as confidence.
    :param use_dirichlet_boundary: Use Dirichlet boundary conditions.
    :param colors: Optional color attribute to interpolate (N x K matrix).
    :param output_vertex_depth_attribute_name: Output density attribute name. We use a point's target octree depth as a measure of the sampling density. A lower number means a low sampling density, and can be used to prune low-confidence regions as a post-process.
    :param verbose: Output logging information (directly printed to standard output).
    """
