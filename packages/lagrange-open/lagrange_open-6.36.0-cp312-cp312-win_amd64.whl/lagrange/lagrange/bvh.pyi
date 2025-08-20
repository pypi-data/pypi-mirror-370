import lagrange


def weld_vertices(mesh: lagrange.core.SurfaceMesh, radius: float = 9.999999974752427e-07, boundary_only: bool = False) -> None:
    """
    Weld nearby vertices together of a surface mesh.

    :param mesh: The target surface mesh to be welded in place.
    :param radius: The maximum distance between vertices to be considered for welding. Default is 1e-6.
    :param boundary_only: If true, only boundary vertices will be considered for welding. Defaults to False.

    .. warning:: This method may introduce non-manifoldness and degeneracy in the mesh.
    """
