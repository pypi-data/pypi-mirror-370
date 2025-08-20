"""Define how :class:`.Envelope3D` should be configured."""

from lightwin.beam_calculation.envelope_3d.util import ENVELOPE3D_METHODS
from lightwin.config.key_val_conf_spec import KeyValConfSpec
from lightwin.util.typing import EXPORT_PHASES

ENVELOPE3D_CONFIG = (
    KeyValConfSpec(
        key="export_phase",
        types=(str,),
        description=(
            "The type of phases that should be exported in the final DAT "
            "file. Note that ``'as_in_original_dat'`` is not implemented "
            "yet, but ``'as_in_settings'`` should behave the same way, "
            "provided that you alter no FieldMap.CavitySettings.reference "
            "attribute."
        ),
        default_value="as_in_settings",
        allowed_values=EXPORT_PHASES,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="flag_cython",
        types=(bool,),
        description=(
            "Not implemented yet. If we should use the Cython implementation "
            "(faster)."
        ),
        default_value=False,
        is_mandatory=False,
        allowed_values=(False,),
        warning_message="Not implemented yet, will ignore this key.",
    ),
    KeyValConfSpec(
        key="flag_phi_abs",
        types=(bool,),
        description=(
            "If the field maps phases should be absolute (no implicit "
            "rephasing after a failure)."
        ),
        default_value=True,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="method",
        types=(str,),
        description="Integration method.",
        default_value="RK4",
        allowed_values=ENVELOPE3D_METHODS,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="n_steps_per_cell",
        types=(int,),
        description=(
            "Number of integrating steps per cavity cell. Recommended value "
            "is 40."
        ),
        default_value=40,
        is_mandatory=False,
    ),
    KeyValConfSpec(
        key="tool",
        types=(str,),
        description="Name of the tool.",
        default_value="Envelope3D",
        allowed_values=(
            "Envelope3D",
            "envelope3d",
            "Envelope_3D",
            "envelope_3d",
        ),
    ),
)

ENVELOPE3D_MONKEY_PATCHES = {}
