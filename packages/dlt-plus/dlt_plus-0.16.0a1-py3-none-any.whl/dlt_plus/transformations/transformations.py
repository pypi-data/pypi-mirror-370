from dlt_plus.transformations.config import TransformationConfig, set_defaults_and_validate
from dlt_plus.transformations.base_transformation import Transformation


def create_transformation(config: TransformationConfig) -> Transformation:
    config = set_defaults_and_validate(config)

    if config.get("engine") == "dbt":
        # only load dbt extras if we need them
        from dlt_plus.transformations.dbt import DbtTransformation

        return DbtTransformation(config)
    elif config.get("engine") == "arrow":
        # only load arrow extras if we need them
        from dlt_plus.transformations.dataframes import DataframeTransformation

        return DataframeTransformation(config)
    else:
        raise ValueError(f"Unsupported engine: {config.get('engine')}")
