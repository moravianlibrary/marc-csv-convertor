# -*- coding: UTF-8 -*-
"""
Obsahuje třídu pro předzpracování vstupních dat.

:author:     Martin Dočekal
:contact:    xdocek09@stud.fit.vubtr.cz

"""

import logging



class Preprocessing(object):
    """
    Třída pro předzpracování vstupních dat.
    """

    posSigns = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Z", "X"]

    def __init__(self, stop_words, values, tagger, taggerPOS, logAfterLines=100):
        self.values = values
        self.stop_words = stop_words
        self.tagger = tagger
        self.taggerPOS = taggerPOS
        self.logAfterLines = logAfterLines
        self.lemPosExt = Lemmatizer(self.tagger, self.taggerPOS)

    def setParams(self, stop_words=[], values=None, tagger=None, taggerPOS=None, logAfterLines=None):

        if len(stop_words) > 0:
            self.is_stop_words = stop_words
        if values is not None:
            self.values = values
        if tagger is not None:
            self.tagger = tagger
        if taggerPOS is not None:
            self.taggerPOS = taggerPOS
        if logAfterLines is not None:
            self.logAfterLines = logAfterLines

    def start(self):
        logging.info("začátek předzpracování")
        lemmatized_subfields = []

        words_to_remove = self.stop_words

        words_remover = RemoveWords(words_to_remove)

        for line in self.values:
            line = line.rstrip('\n')

            line = self.lemPosExt.lemmatize(line)

            if isinstance(line, list):
                line = " ".join(line)

            line = (" ".join(words_remover.removeWords(line))).lower()

            lemmatized_subfields.append(" ".join(words_remover.removeWords(line)))

        return lemmatized_subfields


class RemoveWords(object):
    """
    Třída pro odstranění slov s definovnými parametry. Stop slova nebo na základě počtu znaků.
    """

    def __init__(self, removeStopWords=[], minWordLength=None, maxWordLength=None):
        self.removeStopWords = removeStopWords
        self.minWordLength = minWordLength
        self.maxWordLength = maxWordLength

    def removeWords(self, txt):

        if isinstance(txt, list):
            words = txt
        else:
            words = txt.split()

        if self.removeStopWords == [] and self.minWordLength is None and self.maxWordLength is None:
            return words

        notRemovedWords = []
        for x in words:
            if (self.removeStopWords and x in self.removeStopWords) or \
                    (self.minWordLength and len(x) < self.minWordLength) or \
                    (self.maxWordLength and len(x) > self.maxWordLength):
                continue

            notRemovedWords.append(x)

        return notRemovedWords


class Lemmatizer(object):
    """
    Třída pro lemmatizaci slov a extrakci vybraných slovních druhů. Používá nástroj morphodita.

    Značky slovních druhů:
        N - 1
        A - 2
        P - 3
        C - 4
        V - 5
        D - 6
        R - 7
        J - 8
        T - 9
        I - 10
        Z - Symboly
        X - Neznámé
    """
    __POSTranslaterNum = {
        1: "N",
        2: "A",
        3: "P",
        4: "C",
        5: "V",
        6: "D",
        7: "R",
        8: "J",
        9: "T",
        10: "I"
    }

    def __init__(self, tagger, taggerPOS):
        """
        Konstrukce objektu.
        
        :param tagger: Cesta k souboru pro tagger morphodity.
        :param taggerPOS: Cesta k souboru pro tagger morphodity. Který bude použit pro extrakci slovních druhů.
        :raises LemmatizerTaggerException: Když není definovaný tokenizer pro dodaný model.
        """
        self.tagger = Tagger.load(tagger)
        if self.tagger is None:
            raise LemmatizerTaggerException("Chybný TAGGER.")
        self.tokenizer = self.tagger.newTokenizer()
        if self.tokenizer is None:
            raise LemmatizerTaggerException("Není definovaný tokenizer pro dodaný model.")

        self.taggerPOS = Tagger.load(tagger)
        if self.taggerPOS is None:
            raise LemmatizerTaggerException("Chybný TAGGER.")
        self.tokenizerPOS = self.tagger.newTokenizer()
        if self.tokenizerPOS is None:
            raise LemmatizerTaggerException("Není definovaný tokenizer pro dodaný model.")

        self.forms = Forms()
        self.tokens = TokenRanges()
        self.lemmas = TaggedLemmas()
        self.converter = TagsetConverter.newPdtToConll2009Converter()

    def lemmatize(self, text):
        """
        Vrací lemmatizovanou formu slov.
        
        :param text: Text pro zpracování.
        :returns:  list -- obsahující lemmatizovaná slova
        """
        self.tokenizer.setText(text)
        words = []
        while self.tokenizer.nextSentence(self.forms, self.tokens):
            self.tagger.tag(self.forms, self.lemmas)
            for i in range(len(self.lemmas)):
                lemma = self.lemmas[i]
                self.converter.convert(lemma)
                words.append(lemma.lemma)

        return words