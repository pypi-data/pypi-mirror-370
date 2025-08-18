class ChatBase:
    """
    Base class for chat models.
    """
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(model='{self.model_name}')"
        
    def build_extra_payload(self, **kwargs) -> dict:
        """
        Build extra payload for the request.
        """
        playload_extra = dict()
        if len(kwargs) > 0:
            for key, value in kwargs.items():
                if key not in self.payload_keys.keys():
                    raise ValueError(f"Invalid key: {key}")
                
                if not isinstance(kwargs[key], self.payload_keys[key]):
                    value = self.payload_keys[key](value)
                
                playload_extra[key] = value
        
        return playload_extra