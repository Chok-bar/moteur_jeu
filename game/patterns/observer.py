from typing import List, Dict, Any, Callable
import datetime

class Observer:
    """Interface for all observers that want to be notified of game events."""
    def update(self, game_id: int, event_type: str, data: Dict[str, Any]) -> None:
        """Receive update notification with event data."""
        pass

class Subject:
    """Base class for all subjects that can notify observers."""
    def __init__(self):
        self._observers: List[Observer] = []
    
    def attach(self, observer: Observer) -> None:
        """Attach an observer to this subject."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """Detach an observer from this subject."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, game_id: int, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all observers about an event."""
        for observer in self._observers:
            observer.update(game_id, event_type, data)

class GameEventManager(Subject):
    """Manages game events and notifies observers."""
    def __init__(self):
        super().__init__()
        
    def player_joined(self, game_id: int, player_id: int, player_name: str) -> None:
        """Notify when a player joins a game."""
        self.notify(game_id, 'player_joined', {
            'player_id': player_id, 
            'player_name': player_name,
            'timestamp': datetime.datetime.now()
        })
    
    def player_moved(self, game_id: int, player_id: int, 
                    old_position: tuple, new_position: tuple) -> None:
        """Notify when a player makes a move."""
        self.notify(game_id, 'player_moved', {
            'player_id': player_id,
            'old_position': old_position,
            'new_position': new_position,
            'timestamp': datetime.datetime.now()
        })
    
    def player_died(self, game_id: int, player_id: int) -> None:
        """Notify when a player dies."""
        self.notify(game_id, 'player_died', {
            'player_id': player_id,
            'timestamp': datetime.datetime.now()
        })
    
    def game_ended(self, game_id: int, winner: str) -> None:
        """Notify when a game ends."""
        self.notify(game_id, 'game_ended', {
            'winner': winner,
            'timestamp': datetime.datetime.now()
        })

class LoggingObserver(Observer):
    """Observer that logs game events."""
    def __init__(self, logger):
        self.logger = logger
    
    def update(self, game_id: int, event_type: str, data: Dict[str, Any]) -> None:
        self.logger.info(f"Game {game_id} event: {event_type} - {data}")