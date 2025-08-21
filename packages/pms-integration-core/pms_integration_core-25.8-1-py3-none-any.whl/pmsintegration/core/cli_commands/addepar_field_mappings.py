from collections.abc import Callable
from datetime import datetime

import yaml

from pmsintegration.core.app import AppContext
from pmsintegration.platform import utils


def run(output: str, write_log: Callable[..., None]):
    app_ctx = AppContext.global_context()
    env_name = app_ctx.env_name()
    file_output = output.format(env_name=env_name, conf_root=app_ctx.env.conf_root)
    attributes = app_ctx.addepar.get_attributes()
    data = {
        "__note__": "WARNING: AUTO GENERATED FILE by running command:"
                    " pmsint core generate-addepar-field-mappings"
                    " Don't edit manually.",
        "__when__": datetime.now().isoformat(),
        "__author__": utils.current_username(),
        "__addepar__": app_ctx.addepar._config.endpoint,  # noqa
        "__name__": "addepar_fields_mapping",
        "__order__": 20
    }

    def _id_to_field_name(attr_id: str):
        return attr_id.removeprefix("_custom_").rsplit("_", 1)[0]

    data["addepar_custom_fields"] = {  # Let's keep the sorted on keys to avoid git-diff noise in re-run
        _id_to_field_name(attr.id): attr.model_dump(exclude_unset=True, exclude_none=True)
        for attr in sorted(attributes, key=lambda a: a.id) if attr.id.startswith("_custom_")
    }

    yaml_data = yaml.safe_dump(data, sort_keys=False)

    utils.write_text_to(file_output, yaml_data)

    write_log(f"Configuration file written successfully: {file_output}")
