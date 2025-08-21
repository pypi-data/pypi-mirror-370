from typing import Type


from ....dialogue.replicas.base import Replica


class ReplicaClassAccessDeny(Exception):
    user_id: int
    replica_class: Type[Replica]

    def __init__(
        self,
        user_id: int,
        replica_class: Type[Replica],
    ):
        self.user_id = user_id
        self.replica_class = replica_class

    def __str__(self) -> str:
        return f"Access to replica `{self.replica_class}` was deny for user `{self.user_id}`"
