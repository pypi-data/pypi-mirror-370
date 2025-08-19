# Copyright 2023-2025 Luminary Cloud, Inc. All Rights Reserved.
import logging as _logging

from ._version import __version__

from . import (
    _patch as _patch,
    enum as enum,
    exceptions as exceptions,
    meshing as meshing,
    outputs as outputs,
    params as params,
    types as types,
    vis as vis,
)

from ._client import (
    Client as Client,
    get_default_client as get_default_client,
    set_default_client as set_default_client,
)
from .geometry import (
    get_geometry as get_geometry,
    Geometry as Geometry,
)
from .geometry_version import (
    GeometryVersion as GeometryVersion,
)
from .mesh import (
    get_mesh as get_mesh,
    get_mesh_metadata as get_mesh_metadata,
    Mesh as Mesh,
)
from .project import (
    create_project as create_project,
    add_named_variables_from_csv as add_named_variables_from_csv,
    get_project as get_project,
    list_projects as list_projects,
    iterate_projects as iterate_projects,
    Project as Project,
)
from .simulation import (
    get_simulation as get_simulation,
    Simulation as Simulation,
)
from .simulation_template import (
    get_simulation_template as get_simulation_template,
    SimulationTemplate as SimulationTemplate,
)
from .simulation_param import (
    SimulationParam as SimulationParam,
    EntityIdentifier as EntityIdentifier,
)
from .solution import (
    Solution as Solution,
)
from .reference_values import (
    ReferenceValues as ReferenceValues,
)
from .volume_selection import (
    VolumeSelection as VolumeSelection,
)
from .named_variable_set import (
    NamedVariableSet as NamedVariableSet,
)

# Log SDK version number
logger = _logging.getLogger("luminarycloud")
logger.debug(f"Imported Luminary Cloud SDK v{__version__}")


def use_itar_environment() -> None:
    """
    Configures the SDK to make API calls to the Luminary Cloud ITAR Environment,
    rather than the Standard Environment.

    This function only needs to be called once in your script, before making any
    API calls.

    Examples
    --------

    >>> import luminarycloud as lc
    >>> lc.use_itar_environment()
    >>> lc.list_projects() # lists projects in the user's ITAR environment
    """
    set_default_client(
        Client(
            target="apis-itar.luminarycloud.com",
            # below params are kwargs to Auth0Client constructor
            domain="luminarycloud-itar-prod.us.auth0.com",
            client_id="gkW9O4wZWnTHOXhiejHOKDO4cuPF3S0y",
            audience="https://api-itar-prod.luminarycloud.com",
        )
    )
    logger.info("using Luminary Cloud ITAR Environment")


def use_standard_environment() -> None:
    """
    Configures the SDK to make API calls to the Luminary Cloud Standard Environment,
    rather than the ITAR Environment.

    This function only needs to be called once in your script, before making any
    API calls.

    Examples
    --------

    >>> import luminarycloud as lc
    >>> lc.use_standard_environment()
    >>> lc.list_projects() # lists projects in the user's Standard environment
    """
    set_default_client(Client())
    logger.info("using Luminary Cloud Standard Environment")
