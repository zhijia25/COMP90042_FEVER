import os
import pickle
from loading import Loader


class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, label=None):
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.label = label


class Inputing(object):
    def __init__(self):
        self.pickledir = './pickles'
        self.loader = Loader()

    def input_train(self):
        pickle_file_dir = os.path.join(self.pickledir, 'train.txt')
        if not os.path.exists(pickle_file_dir):
            df = self.loader.train_loader()
            with open(pickle_file_dir, 'wb') as f:
                pickle.dump(df, f)

        else:
            with open(pickle_file_dir, 'rb') as f:
                df = pickle.load(f)
        print(df)
        print(df.columns)
        input_examples = df.apply(lambda x: InputExample(guid=x['index'],
                                                         text_a=x['claim'],
                                                         text_b=x['evidence'],
                                                         label=x['label']), axis=1)
        return input_examples


    def input_dev(self):
        pickle_file_dir = os.path.join(self.pickledir, 'dev.txt')
        if not os.path.exists(pickle_file_dir):
            df = self.loader.dev_loader()
            with open(pickle_file_dir, 'wb') as f:
                pickle.dump(df, f)

        else:
            with open(pickle_file_dir, 'rb') as f:
                df = pickle.load(f)
        input_examples = df.apply(lambda x: InputExample(guid=x['index'],
                                                         text_a=x['claim'],
                                                         text_b=x['evidence'],
                                                         label=x['label']), axis=1)
        return input_examples

    def input_test(self):
        pickle_file_dir = os.path.join(self.pickledir, 'test.txt')
        if not os.path.exists(pickle_file_dir):
            df = self.loader.test_loader()
            with open(pickle_file_dir, 'wb') as f:
                pickle.dump(df, f)
        else:
            with open(pickle_file_dir, 'rb') as f:
                df = pickle.load(f)
            input_examples = df.apply(lambda x: InputExample(guid=x['index'],
                                                             text_a=x['claim'],
                                                             text_b=x['evidence'],
                                                             label='NOT ENOUGH INFO'), axis=1)
            return input_examples

inputformatting = Inputing()
#inputformatting.input_train()
#inputformatting.input_dev()
inputformatting.input_test()
