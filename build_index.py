# ======================== Indexer imports ========================
import lucene,sys, os, threading, time
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.index import \
    FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search.similarities import BM25Similarity



class Ticker():

    def __init__(self):
        self.tick = True

    def run(self):
        while self.tick:
            sys.stdout.write('.')
            sys.stdout.flush()
            time.sleep(1.0)


class SearchEngine():

    def __init__(self):
        wikidir = './wiki-pages-text'
        indexdir = './IndexFiles.index'
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        if not os.path.exists(indexdir):
            os.mkdir(indexdir)

        self.analyzer = LimitTokenCountAnalyzer(StandardAnalyzer(), 1048576)
        store = SimpleFSDirectory(Paths.get(indexdir))
        config = IndexWriterConfig(self.analyzer)
        config.setSimilarity(BM25Similarity())
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        writer = IndexWriter(store, config)

        self.indexer(wikidir, writer)
        ticker = Ticker()
        print('commit index')
        threading.Thread(target=ticker.run).start()
        writer.commit()
        writer.close()
        ticker.tick = False
        print('done')

    def repalcer(self, text):
        chars = '/\\`*_{}[]()>#+-.!$‘"'
        for c in chars:
            if c in text:
                text = text.replace(c, ' ')
        return text

    def indexer(self, root, writer):
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(True)
        t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
        for root, dirnames, filenames in os.walk(root):
            i = 0
            for filename in filenames:
                i += 1
                with open(os.path.join(root, filename), encoding='utf-8') as f:
                    for line in f.readlines():
                        line = line.split(' ', 2)
                        docname = line[0] + ' ' + line[1]
                        name = self.repalcer(line[0])
                        contents = line[2]
                        name_contents = name + ' ' + contents
                        doc = Document()
                        doc.add(Field('name-sid', docname, t1))
                        doc.add(Field('name', name, t1))
                        doc.add(Field('contents', contents, t1))
                        doc.add(Field('name-contents', name_contents, t1))
                        writer.addDocument(doc)
                print('File %d done indexing' % i)


if __name__ == "__main__":
    SearchEngine()
