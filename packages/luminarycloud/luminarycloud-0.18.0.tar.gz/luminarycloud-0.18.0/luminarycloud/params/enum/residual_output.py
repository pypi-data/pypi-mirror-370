from enum import IntEnum as _IntEnum

from luminarycloud._proto.output import output_pb2 as _outputpb
from luminarycloud._proto.quantity import quantity_pb2 as _quantitypb


class ResidualNormalization(_IntEnum):
    """
    Residual normalization type.

    Attributes
    ----------
    ABSOLUTE

    RELATIVE

    MAX

    MIN

    """

    ABSOLUTE = _outputpb.RESIDUAL_ABSOLUTE
    RELATIVE = _outputpb.RESIDUAL_RELATIVE
    MAX = _outputpb.RESIDUAL_MAX
    MIN = _outputpb.RESIDUAL_MIN


class ResidualQuantity(_IntEnum):
    """
    Residual normalization type.

    Attributes
    ----------
    DENSITY
        Mass
    X_MOMENTUM
        X-Momentum
    Y_MOMENTUM
        Y-Momentum
    Z_MOMENTUM
        Z-Momentum
    ENERGY
        Energy
    SA_VARIABLE
        Spalart-Allmaras Variable
    TKE
        Turbulent Kinetic Energy
    OMEGA
        Specific Dissipation Rate
    GAMMA
        Turbulence Intermittency
    RE_THETA
        Momentum-Thickness Reynolds Number
    N_TILDE
        Amplification Factor
    """

    DENSITY = _quantitypb.RESIDUAL_DENSITY
    X_MOMENTUM = _quantitypb.RESIDUAL_X_MOMENTUM
    Y_MOMENTUM = _quantitypb.RESIDUAL_Y_MOMENTUM
    Z_MOMENTUM = _quantitypb.RESIDUAL_Z_MOMENTUM
    ENERGY = _quantitypb.RESIDUAL_ENERGY
    SA_VARIABLE = _quantitypb.RESIDUAL_SA_VARIABLE
    TKE = _quantitypb.RESIDUAL_TKE
    OMEGA = _quantitypb.RESIDUAL_OMEGA
    GAMMA = _quantitypb.RESIDUAL_GAMMA
    RE_THETA = _quantitypb.RESIDUAL_RE_THETA
    N_TILDE = _quantitypb.RESIDUAL_N_TILDE
