import numpy as np
from itertools import combinations


class Import:
    """
    Imports data from various sources.
    Currently, just tab-delimited files are supported
    """

    def __init__(self, file, ftype):
        self.data = None
        self.data_modified = None
        self.data_slow = None
        self.prefixed_data = None
        self.file = file
        if ftype == "TAB":
            self.import_tab_file(self.file)

    def import_tab_file(self, tabfile):
        self.data = np.genfromtxt(tabfile, dtype=str, delimiter='\t')

    def append_feature(self, feature, value):
        return 'G' + feature + '_' + value

    def process_data_1(self):
        append_feature_v = np.vectorize(self.append_feature, otypes=[str])
        self.data_modified = np.empty(self.data.shape, dtype='str')

        for col in self.data.shape[1]:
            self.data_modified[:, col] = append_feature_v(col,self.data[:, col])

        return self.data_modified

    def process_data_2(self):
        """ Slow due to using loops """
        self.data_slow = np.empty(self.data.shape, dtype='str')

        for row in range(self.data.shape[0]):
            for col in range(self.data.shape[1] - 1):
                prefix = 'G' + str(col + 1) + '_'
                self.data_slow[row][col] = prefix + str(self.data[row][col])
                # print('r:',row,' c:',col,' prefix:',prefix,' ds:',self.data_slow[row][col])

        return self.data_slow

    def process_data_3(self):
        rows = self.data.shape[0]
        cols = self.data.shape[1]
        prefix_row = ['G' + str(i) + '_' for i in range(1, cols)]
        prefix_row.append('')
        prefix_array = np.tile(prefix_row, (rows, 1))
        self.prefixed_data = np.core.defchararray.add(prefix_array, self.data)
        return self.prefixed_data


class FrequentItemsets:
    """
    Takes dataset and support as input and returns
    itemsets satisfying those criterion
    """

    def __init__(self, dataset, support):
        self.data = dataset
        self.support = support
        self.min_support_count = int(self.support * len(self.data) / 100)

    def frequent_1_itemsets(self):
        # Get unique items in the data with their frequency
        one_itemsets = np.unique(self.data, False, False, True, None)
        # Convert the unique items into dict, with value as frequency
        one_itemsets_dict = dict(zip(one_itemsets[0], one_itemsets[1]))
        # Use Comprehensions to get items with support about min value
        frequent_one_itemsets = {k: v for k, v in one_itemsets_dict.items() if v >= self.min_support_count}

        return list(frequent_one_itemsets.keys())

    def combinations(self, itemset_list, k):
        """
        Generates Combinations of k+1 itemsets
        Returns a list of sets
        """
        candidate_itemsets = []

        for candidate in combinations(itemset_list, k + 1):
            candidate_itemsets.append(set(candidate))

        return candidate_itemsets

    def get_itemset_support(self, itemset, data):
        """ Compute support for single k-itemset """
        support = 0
        for row in range(data.shape[0]):    # try to vectorize
            if itemset.issubset(data[row]):
                support = support + 1
        return support

    def compute_support(self, itemsets):
        """
        Compute support for all itemsets with same k value.
        Returns dict of itemset and support as key and value
        """
        support = []
        for itemset in itemsets:
            s = self.get_itemset_support(itemset, self.data)
            support.append(s)
        # itemsets has set which cannot be used as keys, find a way through
        itemsets_dict = dict(zip(itemsets, support))
        return itemsets_dict


    def get_frequent_itemsets(self):
        k = 1
        fi = self.frequent_1_itemsets()

        print('Support is set to be ' + str(self.support) + '%')
        while len(fi) != 0:
            self.logging(k, len(fi))

            # generate combinations
            itemsets = self.combinations(fi, k)
            k = k + 1

            # pruning step, IMPLEMENT LATER
            # remove item-sets whose subsets are not frequent

            # get their support values
            itemsets_with_support = self.compute_support(itemsets)

            # get their frequent itemsets
            fi = {k: v for k, v in itemsets_with_support.items() if v >= self.min_support_count}
        return

    def logging(self, k, count):
        print('Number of length-' + str(k) + ' frequent itemsets: ' + str(count))


def main():
    importObject = Import(r'../data/associationruletestdata.txt', 'TAB')
    prefixed_data = importObject.process_data_3()

    support_percentage = [30, 40, 50, 60, 70]
    for support in support_percentage:
        fi = FrequentItemsets(prefixed_data, support)
        fi.get_frequent_itemsets()


if __name__ == "__main__":
    main()
