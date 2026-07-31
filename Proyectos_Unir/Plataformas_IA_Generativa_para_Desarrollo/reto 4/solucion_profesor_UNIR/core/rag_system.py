"""Sistema RAG: carga de documentos, embeddings, vector store y retrieval."""

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class RAGSystem:
    """Gestiona los embeddings y la recuperacion de fragmentos relevantes.

    Flujo: carga los .md de la carpeta de documentos, los trocea en fragmentos,
    los vectoriza con OpenAIEmbeddings (text-embedding-3-small) y los guarda en
    un InMemoryVectorStore para busquedas por similitud.
    """

    def __init__(self, documents_dir: str = "documents") -> None:
        self.documents_dir = Path(documents_dir)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = InMemoryVectorStore(self.embeddings)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=120,
        )

    def load_documents(self) -> int:
        """Carga, trocea y vectoriza los documentos markdown.

        Devuelve el numero de fragmentos indexados.
        """
        md_files = sorted(self.documents_dir.glob("*.md"))
        if not md_files:
            raise FileNotFoundError(
                f"No hay documentos .md en {self.documents_dir.resolve()}"
            )

        documents = [
            Document(
                page_content=path.read_text(encoding="utf-8"),
                metadata={"source": path.name},
            )
            for path in md_files
        ]
        chunks = self.splitter.split_documents(documents)
        self.vector_store.add_documents(chunks)
        return len(chunks)

    def retrieve(self, query: str, k: int = 4) -> list[Document]:
        """Devuelve los k fragmentos mas relevantes para la consulta."""
        return self.vector_store.similarity_search(query, k=k)

    def retrieve_context(self, query: str, k: int = 4) -> str:
        """Devuelve los fragmentos relevantes formateados para el prompt."""
        chunks = self.retrieve(query, k=k)
        return "\n\n---\n\n".join(
            f"[{chunk.metadata.get('source', 'desconocido')}]\n{chunk.page_content}"
            for chunk in chunks
        )
