from abc import ABC, abstractmethod


class RetrieverResponse:

    def __init__(self, documents):
        self.documents = documents

    def get_content_list(self):
        return [doc.page_content for doc in self.documents]

    def get_content_string(self, delimiter: str):
        contents = self.get_content_list()
        return delimiter.join(contents)


class Retriever(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def get_relevant_data(self, query: str) -> RetrieverResponse:
        pass

    @abstractmethod
    def describe(self):
        pass

    def __str__(self):
        return self.describe()