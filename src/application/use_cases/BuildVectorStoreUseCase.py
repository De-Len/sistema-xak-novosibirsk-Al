from src.core.interfaces import IFileReader, IVectorStore


class BuildVectorStoreUseCase:
    def __init__(self, file_reader: IFileReader, vector_store: IVectorStore):
        self.file_reader = file_reader
        self.vector_store = vector_store

    def execute(self, data_directory: str) -> int:
        documents = self.file_reader.read_files(data_directory)

        if not documents:
            raise ValueError(f"No documents found in {data_directory}")

        self.vector_store.add_documents(documents)
        return len(documents)