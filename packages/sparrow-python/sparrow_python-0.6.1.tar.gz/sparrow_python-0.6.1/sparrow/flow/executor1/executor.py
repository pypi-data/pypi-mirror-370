from sparrow.path.core import add_env_path
add_env_path('../../..')

from v_search.indexer import NativeStore
from jina import Executor, requests, DocumentArray, Document

engine = NativeStore(load_from_local=True)


class VectorSearchExecutor(Executor):
    @requests(on='/add')
    async def add(self, docs: DocumentArray, **kwargs):
        async def _add():
            d = docs[0]
            words = [i.text for i in d.matches]
            return engine.add_to_sub_da(words, da_name=d.tags['da_name'], deduplicate=True, verbose=True, save=True)

        return await _add()

    # @requests(on='/query')
    # def query(self, docs: DocumentArray, **kwargs):
    #     doc = docs[0]
    #     da = engine.query(doc.text, doc.tags['n_limit'])
    #     return da

    @requests(on='/match')
    def match(self, docs: DocumentArray, **kwargs):
        doc = docs[0]
        d = engine.match_to_da(doc.text, da_name=doc.tags['da_name'], n_limit=doc.tags['n_limit'])
        for i in d.matches:
            i.embedding = None
        docs[0].matches = d.matches

    @requests(on='/update')
    async def update(self, docs: DocumentArray, **kwargs):
        async def _update():
            d = docs[0]
            words = [i.text for i in d.matches]
            return engine.update_to_sub_da(words, name=d.tags['da_name'])

        return await _update()

    @requests(on='/delete')
    async def delete(self, docs: DocumentArray, **kwargs):
        async def _delete():
            d = docs[0]
            words = [i.text for i in d.matches]
            return engine.delete_from_sub_da(words, name=d.tags['da_name'])

        return await _delete()
