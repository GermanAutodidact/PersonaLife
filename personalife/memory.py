"""Optional long-term providers. None owns PersonaLife's canonical timeline."""
import json
import os
import tempfile
from pathlib import Path
from typing import Protocol
from .ledger import encode

class MemoryProvider(Protocol):
    def put(self, namespace: str, record: dict): ...
    def search(self, namespace: str, query: str='') -> list[dict]: ...

class JsonMemoryProvider:
    """Atomic JSON records, one file per namespace/event. Concurrent identical writes are safe."""
    def __init__(self,directory):self.directory=Path(directory)
    def _directory(self,namespace):
        import hashlib
        return self.directory/hashlib.sha256(namespace.encode()).hexdigest()
    def put(self,namespace,record):
        import hashlib
        directory=self._directory(namespace);directory.mkdir(parents=True,exist_ok=True)
        path=directory/(hashlib.sha256(record['id'].encode()).hexdigest()+'.json')
        content=encode(record)
        if path.exists():
            if path.read_text(encoding='utf-8')!=content:raise ValueError('Memory ID collision')
            return
        fd,temp=tempfile.mkstemp(dir=directory)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(content);f.flush();os.fsync(f.fileno())
            # Atomic exclusive publish, preserving immutable IDs under concurrent writers.
            try:os.link(temp,path)
            except FileExistsError:
                if path.read_text(encoding='utf-8')!=content:raise ValueError('Memory ID collision')
        finally:os.unlink(temp)
    def search(self,namespace,query=''):
        records=[json.loads(p.read_text(encoding='utf-8')) for p in self._directory(namespace).glob('*.json')]
        return sorted([r for r in records if query.casefold() in r['content'].casefold()],key=lambda r:r['created_at'],reverse=True)

class AiMemoryProvider:
    """Verified against AiMemory SQLiteMemoryStore.import_records/search (0.1.0)."""
    def __init__(self,database):
        from aimemory.database import SQLiteMemoryStore
        self.store=SQLiteMemoryStore(database)
    def put(self,namespace,record):
        from aimemory.models import MemoryRecord
        return self.store.import_records(namespace,[MemoryRecord.from_dict(record)])
    def search(self,namespace,query=''):
        return [r.to_dict() for r in self.store.search(namespace,query)]
    def close(self):self.store.db.close()

class Mem0Provider:
    """Opt-in client injection; caller configures storage, embeddings and credentials."""
    def __init__(self,client):self.client=client
    def put(self,namespace,record):
        return self.client.add(record['content'],user_id=namespace,
            metadata={**record['metadata'],'personalife_event_id':record['id']},infer=False)
    def search(self,namespace,query=''):
        result=self.client.search(query,user_id=namespace,limit=10)
        return result.get('results',[]) if isinstance(result,dict) else result

class LettaProvider:
    """Explicit bridge contract; no dependency on retired Letta V1 endpoints.

    Inject put_memory(namespace, record) and search_memory(namespace, query)
    bound to the maintained Letta integration used by your host.
    """
    def __init__(self,put_memory,search_memory):self._put=put_memory;self._search=search_memory
    def put(self,namespace,record):return self._put(namespace,record)
    def search(self,namespace,query=''):return self._search(namespace,query)
