from aiohttp import ClientSession, FormData
from typing import Any, Optional, Dict, Union
import aiofiles
import re
import os


class Network:
    def __init__(self, token: str) -> None:
        self.token: str = token
        self.session: Optional[ClientSession] = None
        self.api: str = f"https://botapi.rubika.ir/v3/{self.token}/"
        

    async def request(self, method: str, json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        async with ClientSession() as session:
            async with session.post(self.api + method, json=json) as response:
                response.raise_for_status()
                data: dict = await response.json()
                return data.get("data")

    async def request_bytes_file(self, url: str) -> bytes:
        async with ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.read()

    async def request_upload_file(self, upload_url: str, file: Union[str], name: str) -> str:
        if isinstance(file, str) and re.match(r"^https?://", file):
            file = await self.request_bytes_file(file)
        elif isinstance(file, str) and os.path.isfile(file):
            async with aiofiles.open(file, "rb") as f:
                file = await f.read()

        form = FormData()
        form.add_field("file", file, filename=name, content_type="application/octet-stream")
        async with ClientSession() as session:
            async with session.post(upload_url, data=form) as response:
                response.raise_for_status()
                data = await response.json()
                return data["data"]["file_id"]

    async def request_download_file(self, url: str, name: str) -> dict[str, Union[str, bool]]:
        file = await self.request_bytes_file(url)
        async with aiofiles.open(name, "wb") as f:
            await f.write(file)
            return {"status": True, "file": name}