import os.path
from functools import lru_cache

SOURCE_FILE_PATH: str = "{conf_root}/addepar-fields-mapping-{env_name}.yml"


@lru_cache
def aliases():
    from pmsintegration.platform.config import YamlPropertySource
    from pmsintegration.platform.globals import env
    file = SOURCE_FILE_PATH.format(conf_root=env.conf_root, env_name=env.env_name)
    return YamlPropertySource(file, os.path.basename(file), 20)


@lru_cache
def alias(field_name: str) -> str:
    source = aliases()
    key = f"addepar_custom_fields.{field_name}.id"
    mapped = source.get(key)
    if mapped is None:
        props = source.properties
        cleansed = key.lower().replace("_", "")
        for _name, _mapped in props.items():
            cleansed_n = _name.lower().replace("_", "")
            if cleansed == cleansed_n:
                mapped = _mapped
                break
    return mapped
