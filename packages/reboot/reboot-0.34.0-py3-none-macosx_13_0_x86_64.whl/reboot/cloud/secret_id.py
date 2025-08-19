from dataclasses import dataclass
from reboot.naming import (
    SecretName,
    SpaceId,
    SpaceName,
    UserId,
    get_encoded_secret_name,
    get_namespace_for_space,
    get_space_id,
)
from typing_extensions import Self


@dataclass(frozen=True)
class SecretId:
    # TODO: In the future, apps will run (and store secrets) in a namespace identified by
    # their `OrgId` and `SpaceId`. But since we only have a `SpaceId` so far, the
    # organization is represented by the `UserId`. It's also possible that when the
    # organization is introduced it will be incorporated into the `SpaceId`.
    user_id: UserId
    space_id: SpaceId
    secret_name: SecretName

    def __post_init__(self) -> None:
        if any(
            '/' in v for v in [self.user_id, self.space_id, self.secret_name]
        ):
            raise Exception(
                "Secret identifiers may not contain slashes. "
                f"Got: {self.user_id=}, {self.space_id=}, {self.secret_name=}."
            )

    @classmethod
    def from_parts(
        cls, *, user_id: UserId, space_name: SpaceName, secret_name: SecretName
    ) -> Self:
        if space_name != user_id:
            # TODO: See TODO on the `user_id` attribute.
            raise Exception(
                f"Expected space name to match user id: got {space_name=}, {user_id=}."
            )
        return cls(
            user_id=user_id,
            space_id=get_space_id("/".join((user_id, space_name))),
            secret_name=secret_name
        )

    @classmethod
    def decode(cls, id_: str) -> Self:
        components = id_.split("/")
        if len(components) != 3:
            # TODO: Declare exception types?
            raise Exception(
                f"Expected a three part secret ID, separated by slashes. Got: {id_}"
            )
        return cls(*components)

    def encode(self) -> str:
        return "/".join((self.user_id, self.space_id, self.secret_name))

    @property
    def namespace(self) -> str:
        return get_namespace_for_space(self.space_id)

    @property
    def k8s_secret_name(self) -> str:
        """The secret_name, encoded for safe storage in Kubernetes.

        `get_encoded_secret_name` hashes the name, but we additionally prefix to rule
        out collisions with internal secrets: in particular, the API keys written for
        ApplicationDeployments.
        """
        return f"user-secret-{get_encoded_secret_name(self.secret_name)}"
