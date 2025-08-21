# -*- coding: utf-8 -*-

"""
Configuration management with inheritance, validation, and AWS deployment.

Provides BaseConfig class for hierarchical configuration management with
shared value inheritance, environment-specific parameter generation, and
integrated deployment to AWS SSM Parameter Store and S3.
"""

try:
    import typing_extensions as T
except ImportError:  # pragma: no cover
    import typing as T
import copy
import json
import dataclasses
from functools import cached_property

from func_args.api import OPT
from s3pathlib import S3Path
from simple_aws_ssm_parameter_store.api import (
    ParameterType,
    ParameterTier,
    Parameter,
    put_parameter_if_changed,
    delete_parameter,
)
from which_env.api import validate_env_name, BaseEnvNameEnum
from configcraft.api import DEFAULTS, apply_inheritance, deep_merge
from .vendor.strutils import slugify

from .constants import ALL, AwsTagKeyEnum
from .utils import sha256_of_text
from .s3 import S3Parameter
from .env import validate_project_name, normalize_parameter_name, T_BASE_ENV


T_BASE_ENV_NAME_ENUM = T.TypeVar(
    "T_BASE_ENV_NAME_ENUM",
    bound=BaseEnvNameEnum,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_ssm.client import SSMClient
    from mypy_boto3_s3.client import S3Client


@dataclasses.dataclass(frozen=True)
class DeploymentResult:
    """
    Result of a :meth:`BaseConfig.deploy_env_parameter` operation.
    to AWS SSM Parameter Store and S3.

    :param before_param: Parameter before deployment (if exists)
    :param after_param: Parameter after deployment (if exists)
    :param s3path_latest: S3 path for the latest version (if created)
    :param s3path_versioned: S3 path for the versioned file (if created)
    """

    before_param: Parameter | None
    after_param: Parameter | None
    s3path_latest: S3Path | None
    s3path_versioned: S3Path | None

    def __post_init__(self):
        if (self.before_param is None) and (
            self.after_param is None
        ):  # pragma: no cover
            raise ValueError(
                "Either before_param (when it's an update) "
                "or after_param (when it's a create) must be set."
            )
        v = sum([(self.s3path_latest is None), (self.s3path_versioned is None)])
        if v == 1:  # pragma: no cover
            raise ValueError(
                "s3path_latest and s3path_versioned must both be set "
                "(when it's a create or update) or not set (when there is not update."
            )

    @property
    def is_ssm_deployed(self) -> bool:
        """
        Indicate if SSM parameter deployment operation happened.
        """
        return self.after_param is not None

    @property
    def is_s3_deployed(self) -> bool:
        """
        Indicate if S3 parameter deployment operation happened.
        """
        return self.s3path_latest is not None

    @property
    def parameter_name(self) -> str:
        """
        Get the SSM parameter name after deployment.
        """
        if self.after_param is None:
            return self.before_param.name
        else:
            return self.after_param.name

    @property
    def version(self) -> int:
        """
        Get the version of the SSM parameter after deployment.
        """
        if self.after_param is None:
            return self.before_param.version
        else:
            return self.after_param.version


@dataclasses.dataclass
class BaseConfig(
    T.Generic[T_BASE_ENV, T_BASE_ENV_NAME_ENUM],
):
    data: dict = dataclasses.field()
    secret_data: dict = dataclasses.field()
    EnvClass: T.Type["T_BASE_ENV"] = dataclasses.field()
    EnvNameEnumClass: T.Type["T_BASE_ENV_NAME_ENUM"] = dataclasses.field()
    version: str = dataclasses.field()

    _applied_data: dict = dataclasses.field(init=False)
    _applied_secret_data: dict = dataclasses.field(init=False)
    _merged_data: dict = dataclasses.field(init=False)

    def _validate(self):
        """
        Validate configuration structure and naming conventions.

        Ensures project and environment names follow standards and that
        the configuration structure is properly formatted.
        """
        validate_project_name(self.project_name)
        for env_name in self.data:
            if env_name != DEFAULTS:
                validate_env_name(env_name)

    def _apply_shared(self):
        """
        Process shared values and merge configuration data.

        Applies the shared value inheritance pattern and merges non-sensitive
        and sensitive configuration data into a unified structure.
        """
        self._applied_data = copy.deepcopy(self.data)
        self._applied_secret_data = copy.deepcopy(self.secret_data)
        # Apply shared value pattern ("*" and "env." prefixes)
        apply_inheritance(self._applied_data)
        apply_inheritance(self._applied_secret_data)
        # Merge non-sensitive and sensitive data
        self._merged_data = deep_merge(self._applied_data, self._applied_secret_data)

    def __user_post_init__(self):
        """
        Override this method in subclasses for custom initialization logic.

        Called after configuration processing and before the object is ready.
        """

    def __post_init__(self):
        """
        Internal post-initialization handler.

        Do not override this method. Use __user_post_init__ for custom logic.
        Handles validation, shared value processing, and user initialization.
        """
        self._validate()
        self._apply_shared()
        self.__user_post_init__()

    @cached_property
    def project_name(self) -> str:
        return self.data[DEFAULTS]["*.project_name"]

    @cached_property
    def project_name_slug(self) -> str:
        return slugify(self.project_name, delim="-")

    @cached_property
    def project_name_snake(self) -> str:
        return slugify(self.project_name, delim="_")

    @cached_property
    def parameter_name(self) -> str:
        """
        AWS SSM Parameter Store name for consolidated multi-environment configuration.

        Used for storing the complete configuration containing all environments.
        This is typically accessed by admin tools and deployment scripts.

        Pattern: "${project_name}" (no environment suffix)
        Example: "my_project"

        .. note::

            If you want to use "/path/to/parameter-name" style, you can override
            this property in your environment class to return a different value.
        """
        return normalize_parameter_name(self.project_name_snake)

    def get_env(
        self,
        env_name: T.Union[str, "T_BASE_ENV_NAME_ENUM"],
    ) -> "T_BASE_ENV":
        """
        Get environment-specific configuration as a typed dataclass instance.

        Retrieves and deserializes configuration data for the specified environment,
        applying all shared value inheritance and merging sensitive/non-sensitive data.

        :after_param env_name: Environment name (string) or enum value
        :return: Environment configuration instance with all values resolved
        :raises TypeError: If configuration data doesn't match environment schema
        """
        env_name = self.EnvNameEnumClass.ensure_str(env_name)
        data = copy.deepcopy(self._merged_data[env_name])
        data["env_name"] = env_name
        return self.EnvClass.from_dict(data)

    # --------------------------------------------------------------------------
    # Deployment
    # --------------------------------------------------------------------------
    def _get_all_parameter_data(
        self,
    ) -> tuple[str, dict[str, T.Any]]:
        parameter_name = self.parameter_name
        parameter_data = {
            "data": self.data,
            "secret_data": self.secret_data,
        }
        return parameter_name, parameter_data

    def _get_env_parameter_data(
        self,
        env_name: T.Union[str, "T_BASE_ENV_NAME_ENUM"],
    ) -> tuple[str, dict[str, T.Any]]:
        if env_name == ALL:
            return self._get_all_parameter_data()
        env_name = self.EnvNameEnumClass.ensure_str(env_name)
        env = self.get_env(env_name)
        parameter_name = env.parameter_name
        parameter_data = {
            "data": {
                DEFAULTS: {
                    k: v
                    for k, v in self.data.get(DEFAULTS, {}).items()
                    if k.startswith("*") or k.startswith(f"{env_name}.")
                },
                env_name: self.data[env_name],
            },
            "secret_data": {
                DEFAULTS: {
                    k: v
                    for k, v in self.secret_data.get(DEFAULTS, {}).items()
                    if k.startswith("*") or k.startswith(f"{env_name}.")
                },
                env_name: self.secret_data[env_name],
            },
        }
        return parameter_name, parameter_data

    def deploy_env_parameter(
        self,
        ssm_client: "SSMClient",
        s3_client: "S3Client",
        s3dir_config: S3Path,
        env_name: T.Union[str, "T_BASE_ENV_NAME_ENUM"] = ALL,
        description: str | None = OPT,
        type: ParameterType | None = OPT,
        tier: ParameterTier | None = OPT,
        key_id: str | None = OPT,
        overwrite: bool = False,
        allowed_pattern: str | None = OPT,
        tags: dict[str, str] | None = None,
        policies: str | None = OPT,
        data_type: str | None = OPT,
    ) -> DeploymentResult:
        """
        Deploy environment-specific configuration to AWS SSM Parameter Store and S3.

        Deploys configuration for a specific environment or ALL environments to both
        SSM Parameter Store (for runtime access) and S3 (for backup and versioning).
        Only creates S3 files if the SSM parameter actually changes.

        :after_param ssm_client: SSM client for parameter store operations
        :after_param s3_client: S3 client for backup storage
        :after_param s3dir_config: S3 directory for configuration backup
        :after_param env_name: Environment name or ALL for consolidated config
        :after_param tags: Additional AWS resource tags
        :return: DeploymentResult with operation details

        .. note::
            For deploying multiple environments with different AWS clients,
            call this method separately for each environment.
        """
        parameter_name, parameter_data = self._get_env_parameter_data(env_name)
        parameter_value = json.dumps(parameter_data, ensure_ascii=False)
        config_sha256 = sha256_of_text(parameter_value)
        if tags is None:
            tags = {}
        new_tags = {
            AwsTagKeyEnum.project_name.value: self.project_name,
            AwsTagKeyEnum.env_name.value: env_name,
            AwsTagKeyEnum.config_sha256.value: config_sha256,
        }
        tags.update(new_tags)
        tags.update(new_tags)
        before_param, after_param = put_parameter_if_changed(
            ssm_client=ssm_client,
            name=parameter_name,
            value=parameter_value,
            description=description,
            type=type,
            tier=tier,
            key_id=key_id,
            overwrite=overwrite,
            allowed_pattern=allowed_pattern,
            tags=tags,
            policies=policies,
            data_type=data_type,
        )
        # parameter changed
        if after_param is not None:
            s3_parameter = S3Parameter(
                s3dir_config=s3dir_config,
                parameter_name=parameter_name,
            )
            s3path_latest = s3_parameter.write(
                s3_client=s3_client,
                value=parameter_value,
                version=None,
                write_text_kwargs={"tags": tags},
            )
            s3path_versioned = s3_parameter.write(
                s3_client=s3_client,
                value=parameter_value,
                version=after_param.version,
                write_text_kwargs={"tags": tags},
            )
            return DeploymentResult(
                before_param=before_param,
                after_param=after_param,
                s3path_latest=s3path_latest,
                s3path_versioned=s3path_versioned,
            )
        # parameter not changed
        else:
            return DeploymentResult(
                before_param=before_param,
                after_param=after_param,
                s3path_latest=None,
                s3path_versioned=None,
            )

    def delete_env_parameter(
        self,
        ssm_client: "SSMClient",
        env_name: T.Union[str, "T_BASE_ENV_NAME_ENUM"] = ALL,
        s3_client: "S3Client" = None,
        include_s3: bool = False,
        s3dir_config: S3Path | None = True,
    ):
        """
        Delete environment configuration from AWS SSM Parameter Store.

        Removes the SSM parameter for the specified environment. Optionally
        deletes S3 backup files if explicitly requested. S3 deletion is
        disabled by default to preserve backup history.

        :after_param ssm_client: SSM client for parameter store operations
        :after_param env_name: Environment name or ALL for consolidated config
        :after_param s3_client: S3 client (required if include_s3=True)
        :after_param include_s3: Whether to also delete S3 backup files
        :after_param s3dir_config: S3 directory (required if include_s3=True)

        .. note::
            SSM parameter deletion removes all versions. S3 serves as backup
            and is preserved by default unless explicitly deleted.
        """
        parameter_name, _ = self._get_env_parameter_data(env_name)
        delete_parameter(
            ssm_client=ssm_client,
            name=parameter_name,
        )
        if include_s3:
            if (s3_client is None) or (s3dir_config is None):
                raise ValueError(
                    "s3_client and s3dir_config must be provided if include_s3 is True.",
                )
            s3_parameter = S3Parameter(
                s3dir_config=s3dir_config,
                parameter_name=parameter_name,
            )
            s3_parameter.delete_all(s3_client=s3_client)


T_BASE_CONFIG = T.TypeVar("T_BASE_CONFIG", bound=BaseConfig)
