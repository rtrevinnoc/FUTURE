import pandas as pd
import numpy as np
from collections import defaultdict
import re


def preprocess_string(str_arg):
    cleaned_str = re.sub(
        "[^a-z\s]+", " ", str_arg,
        flags=re.IGNORECASE)  # every char except alphabets is replaced
    cleaned_str = re.sub(
        "(\s+)", " ",
        cleaned_str)  # multiple spaces are replaced by single space
    cleaned_str = cleaned_str.lower(
    )  # converting the cleaned string to lower case

    return cleaned_str


class QueryClassifier:
    def __init__(self, unique_classes):

        self.classes = unique_classes  # Constructor is sinply passed with unique number of classes of the training set

    def addToBow(self, example, dict_index):
        """
            Parameters:
            1. example
            2. dict_index - implies to which BoW category this example belongs to
            What the function does?
            -----------------------
            It simply splits the example on the basis of space as a tokenizer and adds every tokenized word to
            its corresponding dictionary/BoW
            Returns:
            ---------
            Nothing

       """

        if isinstance(example, np.ndarray):
            example = example[0]

        for token_word in example.split(
        ):  # for every word in preprocessed example

            self.bow_dicts[dict_index][
                token_word] += 1  # increment in its count

    def train(self, dataset, labels):
        """
            Parameters:
            1. dataset - shape = (m X d)
            2. labels - shape = (m,)
            What the function does?
            -----------------------
            This is the training function which will train the Naive Bayes Model i.e compute a BoW for each
            category/class.
            Returns:
            ---------
            Nothing

        """

        self.examples = dataset
        self.labels = labels
        self.bow_dicts = np.array(
            [defaultdict(lambda: 0) for index in range(self.classes.shape[0])])

        # only convert to numpy arrays if initially not passed as numpy arrays - else its a useless recomputation

        if not isinstance(self.examples, np.ndarray):
            self.examples = np.array(self.examples)
        if not isinstance(self.labels, np.ndarray):
            self.labels = np.array(self.labels)

        # constructing BoW for each category
        for cat_index, cat in enumerate(self.classes):

            all_cat_examples = self.examples[
                self.labels == cat]  # filter all examples of category == cat

            # get examples preprocessed

            cleaned_examples = [
                preprocess_string(cat_example)
                for cat_example in all_cat_examples
            ]

            cleaned_examples = pd.DataFrame(data=cleaned_examples)

            # now costruct BoW of this particular category
            np.apply_along_axis(self.addToBow, 1, cleaned_examples, cat_index)

        ###################################################################################################
        """
            Although we are done with the training of Naive Bayes Model BUT!!!!!!
            ------------------------------------------------------------------------------------
            Remember The Test Time Forumla ? : {for each word w [ count(w|c)+1 ] / [ count(c) + |V| + 1 ] } * p(c)
            ------------------------------------------------------------------------------------

            We are done with constructing of BoW for each category. But we need to precompute a few
            other calculations at training time too:
            1. prior probability of each class - p(c)
            2. vocabulary |V|
            3. denominator value of each class - [ count(c) + |V| + 1 ]

            Reason for doing this precomputing calculations stuff ???
            ---------------------
            We can do all these 3 calculations at test time too BUT doing so means to re-compute these
            again and again every time the test function will be called - this would significantly
            increase the computation time especially when we have a lot of test examples to classify!!!).
            And moreover, it doensot make sense to repeatedly compute the same thing -
            why do extra computations ???
            So we will precompute all of them & use them during test time to speed up predictions.

        """

        ###################################################################################################

        prob_classes = np.empty(self.classes.shape[0])
        all_words = []
        cat_word_counts = np.empty(self.classes.shape[0])
        for cat_index, cat in enumerate(self.classes):

            # Calculating prior probability p(c) for each class
            prob_classes[cat_index] = np.sum(self.labels == cat) / float(
                self.labels.shape[0])

            # Calculating total counts of all the words of each class
            count = list(self.bow_dicts[cat_index].values())
            cat_word_counts[cat_index] = (
                np.sum(np.array(list(self.bow_dicts[cat_index].values()))) + 1
            )  # |v| is remaining to be added

            # get all words of this category
            all_words += self.bow_dicts[cat_index].keys()

        # combine all words of every category & make them unique to get vocabulary -V- of entire training set

        self.vocab = np.unique(np.array(all_words))
        self.vocab_length = self.vocab.shape[0]

        # computing denominator value
        denoms = np.array([
            cat_word_counts[cat_index] + self.vocab_length + 1
            for cat_index, cat in enumerate(self.classes)
        ])
        """
            Now that we have everything precomputed as well, its better to organize everything in a tuple
            rather than to have a separate list for every thing.

            Every element of self.cats_info has a tuple of values
            Each tuple has a dict at index 0, prior probability at index 1, denominator value at index 2
        """

        self.cats_info = [(self.bow_dicts[cat_index], prob_classes[cat_index],
                           denoms[cat_index])
                          for cat_index, cat in enumerate(self.classes)]
        self.cats_info = np.array(self.cats_info)

    def getExampleProb(self, test_example):
        """
            Parameters:
            -----------
            1. a single test example
            What the function does?
            -----------------------
            Function that estimates posterior probability of the given test example
            Returns:
            ---------
            probability of test example in ALL CLASSES
        """

        likelihood_prob = np.zeros(
            self.classes.shape[0])  # to store probability w.r.t each class

        # finding probability w.r.t each class of the given test example
        for cat_index, cat in enumerate(self.classes):

            for (test_token) in (test_example.split(
            )):  # split the test example and get p of each test word

                ####################################################################################

                # This loop computes : for each word w [ count(w|c)+1 ] / [ count(c) + |V| + 1 ]

                ####################################################################################

                # get total count of this test token from it's respective training dict to get numerator value
                test_token_counts = self.cats_info[cat_index][0].get(
                    test_token, 0) + 1

                # now get likelihood of this test_token word
                test_token_prob = test_token_counts / float(
                    self.cats_info[cat_index][2])

                # remember why taking log? To prevent underflow!
                likelihood_prob[cat_index] += np.log(test_token_prob)

        # we have likelihood estimate of the given example against every class but we need posterior probility
        post_prob = np.empty(self.classes.shape[0])
        for cat_index, cat in enumerate(self.classes):
            post_prob[cat_index] = likelihood_prob[cat_index] + np.log(
                self.cats_info[cat_index][1])

        return post_prob

    def test(self, example):
        """
            Parameters:
            -----------
            1. A complete test set of shape (m,)

            What the function does?
            -----------------------
            Determines probability of each test example against all classes and predicts the label
            against which the class probability is maximum
            Returns:
            ---------
            Predictions of test examples - A single prediction against every test example
        """

        cleaned_example = preprocess_string(example)

        # simply get the posterior probability of every example
        post_prob = self.getExampleProb(
            cleaned_example)  # get prob of this example for both classes

        # simply pick the max value and map against self.classes!
        return int(self.classes[np.argmax(post_prob)])
