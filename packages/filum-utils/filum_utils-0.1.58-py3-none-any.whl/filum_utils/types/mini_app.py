from typing import TypedDict, Union, Dict, Any

class UpdateInstalledMiniApp(TypedDict, total=False):
    name: Union[str, None]
    identifier: Union[str, None]
    data: Union[Dict[str, Any], None]
