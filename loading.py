import os,sys
import pandas as pd
import unicodedata
from datetime import datetime
import json
import lucene
from find_data import Searcher


class Loader(object):

    def __init__(self):
        self.datadir = './data'
        self.search_engine = Searcher()

    def train_loader(self, max_sample=float('inf')):
        dir = os.path.join(self.datadir, 'train.json')
        with open(dir) as f:
            data = json.loads(f.read())
            sup_examples, ref_examples, nei_examples = [], [], []
            c = 0
            dl = list(data.items())
            for i, d in dl:
                try:
                    if d['label'] == 'SUPPORTS':
                        for e in d['evidence']:
                            if len(sup_examples) < max_sample:
                                _, content= self._retrieve(e)
                                sup_examples.append([c, i, d['claim'], content.strip(), d['label']])
                                #_, content, score = self._retrieve(e)
                                #sup_examples.append([c, i, d['claim'], content.strip(), int(score),d['label']])
                                c += 1
                                if c % 50 == 0:
                                    print('%d examples loaded' % c)
                    elif d['label'] == 'REFUTES':
                        for e in d['evidence']:
                            if len(ref_examples) < max_sample:
                                _, content = self._retrieve(e)
                                ref_examples.append([c, i, d['claim'], content.strip(), d['label']])
                                #_, content,score = self._retrieve(e)
                                #ref_examples.append([c, i, d['claim'], content.strip(), int(score), d['label']])
                                c += 1
                                if c % 50 == 0:
                                    print('%d examples loaded' % c)
                    else:
                        if len(nei_examples) < max_sample:
                            _, content = self._search(d['claim'])
                            nei_examples.append([c, i, d['claim'], content.strip(), d['label']])
                            c += 1
                            if c % 50 == 0:
                                print('%d examples loaded' % c)
                    #print('%d examples loaded' % c)
                    if len(sup_examples) == max_sample and len(ref_examples) == max_sample \
                            and len(nei_examples) == max_sample:
                        break
                except Exception:
                    continue
        samples = sup_examples + ref_examples + nei_examples
        print(samples)
        df = pd.DataFrame(samples, columns=['index', 'id', 'claim', 'evidence', 'label'])
        #df = pd.DataFrame(samples, columns=['index', 'id', 'claim', 'evidence', 'score', 'label'])

        return df.sample(frac=1).reset_index(drop=True)

    def dev_loader(self, max_sample=float('inf')):
        dir = os.path.join(self.datadir, 'devset.json')
        with open(dir) as f:
            data = json.loads(f.read())
            sup_examples, ref_examples, nei_examples = [], [], []
            c = 0
            dl = list(data.items())
            for i, d in dl:
                try:
                    if d['label'] == 'SUPPORTS':
                        for e in d['evidence']:
                            if len(sup_examples) < max_sample:
                                _, content= self._retrieve(e)
                                sup_examples.append([c, i, d['claim'], content.strip(), d['label']])
                                #_, content, score = self._retrieve(e)
                                #sup_examples.append([c, i, d['claim'], content.strip(), int(score),d['label']])
                                c += 1
                                if c % 50 == 0:
                                    print('%d examples loaded' % c)
                    elif d['label'] == 'REFUTES':
                        for e in d['evidence']:
                            if len(ref_examples) < max_sample:
                                _, content = self._retrieve(e)
                                ref_examples.append([c, i, d['claim'], content.strip(), d['label']])
                                #_, content,score = self._retrieve(e)
                                #ref_examples.append([c, i, d['claim'], content.strip(), int(score), d['label']])
                                c += 1
                                if c % 50 == 0:
                                    print('%d examples loaded' % c)
                    else:
                        if len(nei_examples) < max_sample:
                            _, content = self._search(d['claim'])
                            nei_examples.append([c, i, d['claim'], content.strip(), d['label']])
                            c += 1
                            if c % 50 == 0:
                                print('%d examples loaded' % c)
                    #print('%d examples loaded' % c)
                    if len(sup_examples) == max_sample and len(ref_examples) == max_sample \
                            and len(nei_examples) == max_sample:
                        break
                except Exception:
                    continue
        samples = sup_examples + ref_examples + nei_examples
        print(samples)
        df = pd.DataFrame(samples, columns=['index', 'id', 'claim', 'evidence', 'label'])

        return df.sample(frac=1).reset_index(drop=True)

    def test_loader(self):
        dir = os.path.join(self.datadir, 'test-unlabelled.json')
        with open(dir) as f:
            data = json.loads(f.read())
            examples = []
            c = 0
            cc = 0
            dl = list(data.items())
            for i, d in dl:
                docnames, contents, scores = self._search_score(d['claim'])
                assert len(docnames)>0
                for j in range(len(docnames)):
                    examples.append([c, i, d['claim'], docnames[j], scores[j], contents[j].strip()])
                    c += 1
                cc += 1
                if cc % 50 == 0:
                    print('%d of %d examples loaded' % (cc, len(dl)))
        print(cc)
        print(len(examples))
        return pd.DataFrame(examples, columns=['index', 'id', 'claim', 'docname', 'score', 'evidence'])

    def _retrieve(self, e):

        term, sid = e[0], e[1]
        return self.search_engine.retrieve(term, sid)

    def _search(self, q):

        return self.search_engine.search(q, 10)

    def _search_score(self, q):

        return self.search_engine.search_scores(q, 10)

