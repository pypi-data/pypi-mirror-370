# Copyright 2023-2024 Luminary Cloud, Inc. All Rights Reserved.
from enum import IntEnum
from .._proto.upload import upload_pb2 as uploadpb


class MeshType(IntEnum):
    """
    Represents the file format for a mesh file.

    Attributes
    ----------
    UNSPECIFIED
        Null value
    ANSYS
        ANSYS mesh file (.ansys)
    CGNS
        CFD General Notation System (.cgns)
    OPENFOAM
        OpenFOAM mesh
    """

    UNSPECIFIED = uploadpb.MESH_TYPE_UNSPECIFIED
    ANSYS = uploadpb.MESH_TYPE_ANSYS
    CGNS = uploadpb.MESH_TYPE_CGNS
    OPENFOAM = uploadpb.MESH_TYPE_OPENFOAM
