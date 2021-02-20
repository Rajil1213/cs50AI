import nltk
import sys
import os
import string

from math import log

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """

    # get the list of files and directories in the given directory
    # and get only the files ending with .txt from there
    filenames = os.listdir(directory)
    txtfiles = [filename for filename in filenames
                if filename[-4:] == '.txt']
    
    # for each file in the list of txt files in the directory,
    # read the contents as a string 
    # and in a dictionary with the txt file name as the key
    # map it to the corresponding string extracted
    files = dict()
    for afile in txtfiles:

        path = os.path.join(directory, afile)

        with open(path, 'r') as txt:

            contents = txt.read()
            files[afile] = contents

    return files


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """

    # get the tokens of words from the document
    # and for each token, append its lowercase form to the list of words if
    # the token is not a puctuation and is not a stopword in English
    tokens = nltk.word_tokenize(document)
    words = []
    for token in tokens:

        if token not in string.punctuation and \
                token not in nltk.corpus.stopwords.words("english"):

            words.append(token.lower())

    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """

    # define two dictionary
    # one to store the idf value for each unique word across all documents
    # one to count the no. of documents in which that word appears
    idf = dict()
    count = dict()

    for filename in documents:

        # get the unique words in the file
        bag_of_words = set(documents[filename])
        for word in bag_of_words:
            
            # if the word is already present in the dictionary, increase count
            # else create new dictionary entry and initialize it to 1
            if word in count:
                count[word] += 1
            else:
                count[word] = 1

    # calculate idf for each word using formula
    num_of_documents = len(documents)
    for word in count:
        idf[word] = log(num_of_documents / count[word])

    return idf


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    
    # for each doc file calculate the corresponding tf-idf value
    tfidf = dict()
    for doc in files:

        # value is for summing up the tf-idf value for each word in query
        # for a particular document
        # also get all the words inn that document
        value = 0
        words = files[doc]
        for word in query:

            # count no. of times the word in query appears in current doc
            tf = words.count(word)

            # if count == 0, idf becomes undefined, so set idf to 0
            if tf > 0:
                idf = idfs[word]
            else:
                idf = 0
            
            # sum up the product of tf and idf for current word and current doc
            value += tf * idf

        tfidf[doc] = value 

    # rank docs according to the value of tf-idf in descending order
    ranking = [document for document, val in sorted(tfidf.items(), key=lambda item: item[1], reverse=True)]

    # get the top n documents from the ranking
    top_n = ranking[:n]
    return top_n


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """

    # Since IDF must be prioritized first and
    # 'query term density' gets second priority,
    # give a weight of 90% to query term density
    # Note: IDF has a weight of 100%

    # idf dictionary maps sentence to its score
    # score = idf + 0.9 * query_term_density

    weight = 0.9
    idf = dict()
    for sentence in sentences:
        
        # 'count' to calculate query term density
        # 'score' to calculate the overall score
        count = 0
        score = 0
        words = sentences[sentence]
        length = len(set(words))
        for word in query:

            if word not in words:
                continue
            
            # if the word in query occurs in the current sentence
            # increment count and sum up its idf value
            count += 1
            score += idfs[word]
        
        query_term_density = count / length
        score = score + weight * query_term_density
        idf[sentence] = score

    # get the ranking by sorting the idf dictionary by score
    # in descending order
    ranking = [sent for sent, wrds in sorted(idf.items(), key=lambda item: item[1], reverse=True)]            

    # get the top n sentences from the ranking
    top_n = ranking[:n]

    return top_n


if __name__ == "__main__":
    main()
