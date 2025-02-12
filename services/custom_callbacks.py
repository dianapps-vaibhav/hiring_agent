from langchain_community.callbacks import StreamlitCallbackHandler
from typing import Any

class CustomStreamlitCallbackHandler(StreamlitCallbackHandler):
    def __init__(self, parent_container):
        # Call the parent constructor with the parent_container
        super().__init__(parent_container=parent_container)
        self._accumulated_text = ""
        
    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # Append the new token to the accumulated text
        self._accumulated_text += token
        # Update only the dedicated placeholder (this will only update the assistant's new message area)
        self.parent_container.markdown(self._accumulated_text)
