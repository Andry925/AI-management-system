import re
from collections import Counter

import nltk
import pandas as pd
from nltk.corpus import stopwords

nltk.download('stopwords')

STOPLIST = stopwords.words('english')


class Analysis:
    def __init__(self, dataset):
        self.dataframe = pd.DataFrame(dataset)
        self.all_words = []
        self.most_common_word_amount = 10
        self.total_word_count, self.average_word_note_length = self.calculate_word_analysis()
        self.common_words = self.calculate_most_common_words()

    def count_words(self, text):
        words = re.findall(r'\b\w+\b', text.lower())
        return len(words)

    def calculate_word_analysis(self):
        self.dataframe['word_count'] = self.dataframe['content'].apply(
            self.count_words)
        total_word_count = int(self.dataframe['word_count'].sum())
        average_word_note_length = float(self.dataframe['word_count'].mean())
        return total_word_count, average_word_note_length

    def calculate_most_common_words(self):
        for content in self.dataframe['content']:
            words = re.findall(r'\b\w+\b', content.lower())
            cleaned_words = self.remove_stopwords(words)
            self.all_words.extend(cleaned_words)
        word_occurness = Counter(self.all_words)
        most_common_words = [
            (word, int(count)) for word, count in word_occurness.most_common(
                self.most_common_word_amount)]
        return most_common_words

    def remove_stopwords(self, words):
        return [word for word in words if not word.lower() in STOPLIST]

    def top_3_longest_notes(self):
        top_3_notes = self.dataframe.nlargest(
            3, 'word_count')[["title", "word_count"]]
        return top_3_notes.to_dict(orient='records')

    def top_3_shortest_notes(self):
        top_3_shortest = self.dataframe.nsmallest(
            3, 'word_count')[["title", "word_count"]]
        return top_3_shortest.to_dict(orient='records')

    def to_dict(self):
        return {
            "total_word_count": self.total_word_count,
            "average_word_note_length": self.average_word_note_length,
            "common_words": self.common_words,
            "top_3_longest_notes": self.top_3_longest_notes(),
            "top_3_shortest_notes": self.top_3_shortest_notes()
        }

    def __str__(self):
        return str(self.to_dict())
