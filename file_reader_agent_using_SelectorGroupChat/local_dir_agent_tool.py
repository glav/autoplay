import os

async def get_local_disk_files() -> str:
    # get dir contents
    files = os.listdir('/')
    context = ""
    for file in files:
        context += f"FilePath: {file}\n"
    return context
