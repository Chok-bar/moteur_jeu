from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Role(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    Wolf: _ClassVar[Role]
    Villager: _ClassVar[Role]
Wolf: Role
Villager: Role

class GammeListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GameListReply(_message.Message):
    __slots__ = ("status", "id_games")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ID_GAMES_FIELD_NUMBER: _ClassVar[int]
    status: bool
    id_games: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, status: bool = ..., id_games: _Optional[_Iterable[int]] = ...) -> None: ...

class GameSubscribeRequest(_message.Message):
    __slots__ = ("player", "id_game")
    PLAYER_FIELD_NUMBER: _ClassVar[int]
    ID_GAME_FIELD_NUMBER: _ClassVar[int]
    player: str
    id_game: int
    def __init__(self, player: _Optional[str] = ..., id_game: _Optional[int] = ...) -> None: ...

class GameSubscribeReply(_message.Message):
    __slots__ = ("status", "role", "id_player")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    ID_PLAYER_FIELD_NUMBER: _ClassVar[int]
    status: bool
    role: Role
    id_player: int
    def __init__(self, status: bool = ..., role: _Optional[_Union[Role, str]] = ..., id_player: _Optional[int] = ...) -> None: ...

class GetGameStatusRequest(_message.Message):
    __slots__ = ("id_player", "id_game")
    ID_PLAYER_FIELD_NUMBER: _ClassVar[int]
    ID_GAME_FIELD_NUMBER: _ClassVar[int]
    id_player: int
    id_game: int
    def __init__(self, id_player: _Optional[int] = ..., id_game: _Optional[int] = ...) -> None: ...

class GetGameStatusReply(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class Game(_message.Message):
    __slots__ = ("id_game", "id_player", "started", "round_in_progress")
    ID_GAME_FIELD_NUMBER: _ClassVar[int]
    ID_PLAYER_FIELD_NUMBER: _ClassVar[int]
    STARTED_FIELD_NUMBER: _ClassVar[int]
    ROUND_IN_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    id_game: int
    id_player: int
    started: bool
    round_in_progress: int
    def __init__(self, id_game: _Optional[int] = ..., id_player: _Optional[int] = ..., started: bool = ..., round_in_progress: _Optional[int] = ...) -> None: ...

class Move(_message.Message):
    __slots__ = ("next_position",)
    NEXT_POSITION_FIELD_NUMBER: _ClassVar[int]
    next_position: Position
    def __init__(self, next_position: _Optional[_Union[Position, _Mapping]] = ...) -> None: ...

class Position(_message.Message):
    __slots__ = ("row", "col")
    ROW_FIELD_NUMBER: _ClassVar[int]
    COL_FIELD_NUMBER: _ClassVar[int]
    row: int
    col: int
    def __init__(self, row: _Optional[int] = ..., col: _Optional[int] = ...) -> None: ...

class GetGameboardStatusRequest(_message.Message):
    __slots__ = ("id_party", "id_player")
    ID_PARTY_FIELD_NUMBER: _ClassVar[int]
    ID_PLAYER_FIELD_NUMBER: _ClassVar[int]
    id_party: int
    id_player: int
    def __init__(self, id_party: _Optional[int] = ..., id_player: _Optional[int] = ...) -> None: ...

class GetGameboardStatusReply(_message.Message):
    __slots__ = ("status", "visible_cells")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_CELLS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    visible_cells: str
    def __init__(self, status: bool = ..., visible_cells: _Optional[str] = ...) -> None: ...

class MoveRequest(_message.Message):
    __slots__ = ("id_party", "id_player", "move")
    ID_PARTY_FIELD_NUMBER: _ClassVar[int]
    ID_PLAYER_FIELD_NUMBER: _ClassVar[int]
    MOVE_FIELD_NUMBER: _ClassVar[int]
    id_party: int
    id_player: int
    move: str
    def __init__(self, id_party: _Optional[int] = ..., id_player: _Optional[int] = ..., move: _Optional[str] = ...) -> None: ...

class MoveResponse(_message.Message):
    __slots__ = ("status", "round_in_progress", "move")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ROUND_IN_PROGRESS_FIELD_NUMBER: _ClassVar[int]
    MOVE_FIELD_NUMBER: _ClassVar[int]
    status: bool
    round_in_progress: int
    move: Move
    def __init__(self, status: bool = ..., round_in_progress: _Optional[int] = ..., move: _Optional[_Union[Move, _Mapping]] = ...) -> None: ...
