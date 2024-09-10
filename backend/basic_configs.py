from typing import List

# file upload cache path
CACHE_PATH: str = "./cache_folder"

# RAG
# text spliter
CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 100
SEPARATORS: List[str] = ["\n\n", "\n", ".", ";", ",", " ", "。", "；", "，", "！"]