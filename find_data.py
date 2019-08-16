import lucene
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher, BooleanClause, BooleanQuery
from org.apache.lucene.index import DirectoryReader
from org.apache.pylucene.queryparser.classic import PythonMultiFieldQueryParser
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

class Searcher():

    def __init__(self):
        indexdir = './IndexFiles.index'
        lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        search_dir = SimpleFSDirectory(Paths.get(indexdir))
        self.searcher = IndexSearcher(DirectoryReader.open(search_dir))
        self.searcher.setSimilarity(BM25Similarity())
        self.analyzer = LimitTokenCountAnalyzer(StandardAnalyzer(), 1048576)
        self.lemmatizer = nltk.stem.WordNetLemmatizer()

    def nltk2wn_tag(self,nltk_tag):
        if nltk_tag.startswith('J'):
            return wordnet.ADJ
        elif nltk_tag.startswith('V'):
            return wordnet.VERB
        elif nltk_tag.startswith('N'):
            return wordnet.NOUN
        elif nltk_tag.startswith('R'):
            return wordnet.ADV
        else:
            return None

    def lemmatize_sentence(self, sentence):
        nltk_tagged = nltk.pos_tag(nltk.word_tokenize(sentence))
        wn_tagged = map(lambda x: (x[0], self.nltk2wn_tag(x[1])), nltk_tagged)
        res_words = []
        for word, tag in wn_tagged:
            if tag is None:
                res_words.append(word)
            else:
                res_words.append(self.lemmatizer.lemmatize(word, tag))
        return " ".join(res_words)

    def repalcer(self, text):
        chars = '/\\`*_{}[]()>#+-.!$‘"'
        for c in chars:
            if c in text:
                text = text.replace(c, ' ')
        return text

    # def search(self, query, topk=20):
    #     print(query)
    #     query = self.repalcer(query)
    #     query = PythonMultiFieldQueryParser.escape(query)
    #     qp = PythonMultiFieldQueryParser(['name', 'contents'], self.analyzer)
    #     query = qp.parse(query, ['name', 'contents'],
    #                      [BooleanClause.Occur.MUST, BooleanClause.Occur.MUST], self.analyzer)
    #     print(query)
    #     scores = self.searcher.search(query, topk).scoreDocs
    #     docnames = []
    #     doccontents = []
    #     for score in scores:
    #         doc = self.searcher.doc(score.doc)
    #         docnames.append(doc.get('docname'))
    #         doccontents.append(doc.get('contents'))
    #     return docnames, doccontents

    def retrieve(self, term, sid):
        query = term + ' ' + str(sid)
        query = self.repalcer(query)
        query = QueryParser.escape(query)
        query = QueryParser('name-sid', self.analyzer).parse(query)
        score = self.searcher.search(query, 1).scoreDocs
        doc = self.searcher.doc(score[0].doc)
        return doc.get('name-sid'), doc.get('contents')

    def search_scores(self, query, topk=10):
        query = self.repalcer(query)
        query = QueryParser.escape(query)
        query1 = QueryParser('name', self.analyzer).parse(query)
        query2 = QueryParser('name-contents', self.analyzer).parse(query)
        # print(query2)
        scores1 = self.searcher.search(query1, 30).scoreDocs
        scores2 = self.searcher.search(query2, 30).scoreDocs
        name1 = []
        name2 = []
        for score1 in scores1:
            doc1 = self.searcher.doc(score1.doc)
            t = doc1.get('name')
            if t not in name1:
                name1.append(t)
            if len(name1) > 1:
                break
        # print(name1)
        name2.append(name1[0])
        docnames = []
        doccontents = []
        s = []
        maxscore = scores2[0].score
        t_doc = self.searcher.doc(scores2[0].doc)
        for score2 in scores2:
            doc2 = self.searcher.doc(score2.doc)
            tname = doc2.get('name')
            # print(tname)
            # print(tname,name1)
            if score2.score == maxscore:
                docnames.append(doc2.get('name-sid'))
                doccontents.append(doc2.get('contents'))
                s.append(score2.score)
                # print(docnames)
            elif tname in name1 and score2.score > maxscore - 5:
                docnames.append(doc2.get('name-sid'))
                doccontents.append(doc2.get('contents'))
                s.append(score2.score)
                # print(docnames)
            # print(score2.score)
            # print(maxscore)
            if len(docnames) > 2:
                break
        if len(docnames) == 1 and scores1[0].score > maxscore-10:
            docnames.append(self.searcher.doc(scores1[0].doc).get('name-sid'))
            doccontents.append(self.searcher.doc(scores1[0].doc).get('contents'))
            s.append(scores1[0].score)
        assert len(docnames) != 0
        return docnames, doccontents, s


    def search(self, query, topk=10):
        query = self.repalcer(query)
        #query = self.lemmatize_sentence(query)
        #query = QueryParser.escape(query)
        query1 = QueryParser('name', self.analyzer).parse(query)
        query2 = QueryParser('name-contents', self.analyzer).parse(query)
        # print(query2)
        scores1 = self.searcher.search(query1, 30).scoreDocs
        scores2 = self.searcher.search(query2, 50).scoreDocs
        name1 = []
        name2 = []
        for score1 in scores1:
            doc1 = self.searcher.doc(score1.doc)
            t = doc1.get('name')
            if t not in name1:
                name1.append(t)
            if len(name1)>1:
                break
        # print(name1)
        name2.append(name1[0])
        docnames=[]
        doccontents=[]

        maxscore = scores2[0].score
        t_doc = self.searcher.doc(scores2[0].doc)
        for score2 in scores2:
            doc2 = self.searcher.doc(score2.doc)
            tname = doc2.get('name')
            # print(tname)
            if tname in name1:
                docnames.append(doc2.get('name-sid'))
                doccontents.append(doc2.get('contents'))
                break
            #     print(score2.score)
            # print(score2.score)
            # print(maxscore)
        if len(docnames)==0:
            docnames.append(self.searcher.doc(scores1[0].doc).get('name-sid'))
            doccontents.append(self.searcher.doc(scores1[0].doc).get('contents'))
        return docnames[0], doccontents[0]


# a = Searcher()
# c = "Aleister Crowley was born on June 12, 1875."
# d = a.search(c)
# print(d)
# b = a.search_scores(c)
# print(b)