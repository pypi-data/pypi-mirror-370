from typing import Any, List, Dict, Text, Optional, Tuple, Union, Awaitable

class PublisherSettings():
    def __init__(self,
                 environment:str,
                 stream_name:str
                ) -> None:
        self.stream_name:str = f"{environment}:{stream_name}"
