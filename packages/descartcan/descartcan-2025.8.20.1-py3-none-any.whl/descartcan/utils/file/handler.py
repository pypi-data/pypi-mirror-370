import aiofiles


class AsyncFileHandler:
    def __init__(self, file_path):
        self.file_path = file_path

    async def read_file(self, binary=False):
        mode = "rb" if binary else "r"
        async with aiofiles.open(self.file_path, mode=mode) as file:
            content = await file.read()
            return content

    async def write_file(self, content, binary=False):
        mode = "wb" if binary else "w"
        async with aiofiles.open(self.file_path, mode=mode) as file:
            await file.write(content)

    async def append_file(self, content, binary=False):
        mode = "ab" if binary else "a"
        async with aiofiles.open(self.file_path, mode=mode) as file:
            await file.write(content)
