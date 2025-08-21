import base64
import io
import logging
from typing import List, Optional

from PIL import Image

from .errors import InvalidOperationError, LucidicNotInitializedError
from .image_upload import get_presigned_url, upload_image_to_s3
from .step import Step
from .event import Event

logger = logging.getLogger("Lucidic")

class Session:
    def __init__(
        self, 
        agent_id: str,
        session_id = None,
        **kwargs
    ):
        self.agent_id = agent_id
        self.session_id = session_id
        self.step_history = dict()
        self._active_step: Optional[str] = None  # Step ID, not Step object
        self.event_history = dict()
        self.latest_event = None
        self.is_finished = False
        self.is_successful = None
        self.is_successful_reason = None
        self.session_eval = None
        self.session_eval_reason = None
        self.has_gif = None
        
    @property   
    def active_step(self) -> Optional[Step]:
        """Get the active step object"""
        if self._active_step and self._active_step in self.step_history:
            return self.step_history[self._active_step]
        return None
    
    def update_session(
        self, 
        **kwargs
    ) -> None:
        from .client import Client
        request_data = {
            "session_id": self.session_id,
            "is_finished": kwargs.get("is_finished", None),
            "task": kwargs.get("task", None),
            "is_successful": kwargs.get("is_successful", None),
            "is_successful_reason": Client().mask(kwargs.get("is_successful_reason", None)),
            "session_eval": kwargs.get("session_eval", None),
            "session_eval_reason": Client().mask(kwargs.get("session_eval_reason", None)),
            "tags": kwargs.get("tags", None)
        }

        # auto end any unfinished steps
        if kwargs.get("is_finished", None) is True:
            for step_id, step in self.step_history.items():
                if not step.is_finished:
                    self.update_step(step_id=step_id, is_finished=True)

        Client().make_request('updatesession', 'PUT', request_data)

    def create_step(self, **kwargs) -> str:
        if not self.session_id:
            raise LucidicNotInitializedError()
        step = Step(session_id=self.session_id, **kwargs)
        self.step_history[step.step_id] = step
        self._active_step = step.step_id
        return step.step_id

    def update_step(self, **kwargs) -> None:
        if 'step_id' in kwargs and kwargs['step_id'] is not None:
            if kwargs['step_id'] not in self.step_history:
                raise InvalidOperationError("Step ID not found in session history")
            self.step_history[kwargs['step_id']].update_step(**kwargs)
        else:
            if not self._active_step:
                raise InvalidOperationError("No active step to update")
            self.step_history[self._active_step].update_step(**kwargs)


    def create_event(self, **kwargs):
        # Get step_id from kwargs or active step
        if 'step_id' in kwargs and kwargs['step_id'] is not None:
            step_id = kwargs['step_id']
        elif self._active_step:
            step_id = self._active_step
        else:
            step_id = None
        kwargs.pop('step_id', None)
        event = Event(
            session_id=self.session_id,
            step_id=step_id,
            **kwargs
        )
        self.event_history[event.event_id] = event
        self._active_event = event
        return event.event_id

    def update_event(self, **kwargs):
        if 'event_id' in kwargs and kwargs['event_id'] is not None:
            if kwargs['event_id'] not in self.event_history:
                raise InvalidOperationError("Event ID not found in session history")
            self.event_history[kwargs['event_id']].update_event(**kwargs)
        else:
            if not self._active_event:
                raise InvalidOperationError("No active event to update")
            self._active_event.update_event(**kwargs)

            