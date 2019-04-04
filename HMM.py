import numpy as np
import random
import string

#Dictionaries used to generate the first three words:
firstWords = {}
secondWords = {}
thirdWords = {}

#Transition Markov Chains:
firstOrder = {}
secondOrder = {}
thirdOrder = {}

NUMBER_OF_LINES = 30
MAX_NUMBER_OF_WORDS_PER_LINE = 15
end = "tokEND"

def tokenize(row):
    #cutting into words and removing punctuation
    tokens = row.rstrip().lower()
    tokens = tokens.translate(str.maketrans('','', string.punctuation)).split()
    return tokens

def updateValueInDict(dict, key):
    dict[key] = firstWords.get(key, 0) + 1

def insertValue(dict, key, value):
    if key not in dict:
        dict[key] = []
    dict[key].append(value)

def normalize(dict, sum):
    for key in dict.keys():
        dict[key] /= sum

def listToDict(dict, word):
    list = dict[word]
    subDict = {}
    listLength = len(list)
    for num in list:
        updateValueInDict(subDict, num)
    normalize(subDict, listLength)
    return subDict


def readFromFile():
    ##read lines from file
    file = open("shakespeare-plays/alllines.txt")
    rows = file.read().splitlines() #split the lines at line boundaries returns a list of lines
    return rows


def train(rows):
    print("Prithee waiteth while our alg'rithm is being train'd on thy dataset...")
    for i in range(0,len(rows)):
        original = rows[i]
        tokens = tokenize(original)
        amountOfTokens = len(tokens)

        for i in range(0, amountOfTokens):
            token = tokens[i]
            if i == 0:
                #We map the words that occur at the beginning of each line to
                # the amount of times they occur in the text (as initial words)
                updateValueInDict(firstWords, token)

            else:
                if i == 1:
                    #Inserting into dictionary of second words.
                    insertValue(secondWords, tokens[i - 1], token)
                    #Inserting into first order Markov chain.
                    insertValue(firstOrder, tokens[i - 1], token)
                elif i == 2:
                    #Inserting into dictionary of third words.
                    insertValue(thirdWords, (tokens[i - 2], tokens[i - 1]), token)
                    #Inserting into first order Markov chain.
                    insertValue(firstOrder, tokens[i - 1], token)
                    #Inserting into second order Markov chain.
                    insertValue(secondOrder, (tokens[i - 2], tokens[i - 1]), token)
                else:
                    #Inserting into first order Markov chain.
                    insertValue(firstOrder, tokens[i - 1], token)
                    #Inserting into second order Markov chain.
                    insertValue(secondOrder, (tokens[i - 2], tokens[i - 1]), token)
                    #Inserting into third order Markov chain.
                    insertValue(thirdOrder, (tokens[i - 3], tokens[i - 2], tokens[i - 1]), token)

                if i == amountOfTokens - 1 and amountOfTokens > 1:
                    #Inserting into first order Markov chain.
                    insertValue(firstOrder, token, end)
                    #Inserting into second order Markov chain.
                    insertValue(secondOrder, (tokens[i - 1], token), end)
                    #Inserting into third order Markov chain.
                    insertValue(thirdOrder, (tokens[i - 2], tokens[i - 1], token), end)

    #We normalize the dictionary of first words.
    firstWordsSum = sum(firstWords.values())
    normalize(firstWords, firstWordsSum)

    #We normalize the dictionary of second words.
    for word in secondWords.keys():
        secondWords[word] = listToDict(secondWords, word)

    #We normalize the dictionary of third words.
    for word in thirdWords.keys():
        thirdWords[word] = listToDict(thirdWords, word)

    #We normalize the dict corresponding to the first order Markov chain.
    for word in firstOrder.keys():
        firstOrder[word] = listToDict(firstOrder, word)

    #We normalize the dict corresponding to the second order Markov chain.
    for word in secondOrder.keys():
        secondOrder[word] = listToDict(secondOrder, word)

    #We normalize the dict corresponding to the third order Markov chain.
    for word in thirdOrder.keys():
        thirdOrder[word] = listToDict(thirdOrder, word)


def getRandomValueFromDict(dict, key):
    #When this function is called with "firstWords", we simply return a random
    # value from the dictionary.
    if dict == firstWords:
        return random.choice(list(set(dict)))
    else:
        if key in dict:
            #SubDict represents the dictionary within dict that corresponds to
            # the passed in word(s)
            subDict = dict[key]

            #If the length of the sub dictionary is 1, that means our algorithm
            # has only identified one word that follows the word (or pair or
            # triple). Hence, if we return that value we will be creating a
            # string of 2-4 words that surely existed in the training set. Since
            # we want to avoid repeating long strings of text from the training
            # set, we will attempt to reduce the amount of times we return
            # such a "unique" value by looking in other dictionaries that
            # are less likely to only lead to one option (if possible).
            if len(subDict) > 1:
                return random.choice(list(set(subDict)))
            else:
                #If our original dictionary was "thirdOrder" we try
                # "secondOrder" and possibly "firstOrder".
                if dict == thirdOrder:
                    #We try to use the last two words instead of the last three
                    # to see if we can obtain more than one option.
                    attempt1 = getRandomValueFromDict(secondOrder, (key[1],key[2]))
                    if attempt1 == end:
                        #We try to use the last word instead of the last two to
                        # see if we can obtain more than one option.
                        attempt2 = getRandomValueFromDict(firstOrder, key[1])
                        if attempt2 == end:
                            #If both attempts are unsuccessful, we return the
                            # only option obtained from "thirdOrder".
                            return random.choice(list(set(subDict)))
                        else:
                            #If the first attempt failed but the second one
                            # succeeded, we return what we obtained from
                            # that second attempt.
                            return attempt2
                    else:
                        #If the first attempt succeeded, we return what we
                        # obtained from that attempt.
                        return attempt1

                #If our original dictionary was "secondOrder", we try
                # "firstOrder".
                elif dict == secondOrder:
                    #We try to use the lsat word instead of the last two words
                    # to see if we can obtain more than one option.
                    attempt = getRandomValueFromDict(firstOrder, key[1])
                    if attempt == end:
                        #If the attempt was unsuccessful, we return the only
                        # option obtained from "secondOrder".
                        return random.choice(list(set(subDict)))
                    else:
                        #If the attempt succeeded, we return what we obtained
                        # from that attempt.
                        return attempt

                #If our original dictionary was "thirdWords", we try
                # "secondWords".
                elif dict == thirdWords:
                    #We try to use the lsat word instead of the last two words
                    # to see if we can obtain more than one option.
                    attempt = getRandomValueFromDict(secondWords, key[1])
                    if attempt == end:
                        #If the attempt was unsuccessful, we return the only
                        # option obtained from "thirdWords".
                        return random.choice(list(set(subDict)))
                    else:
                        #If the attempt succeeded, we return what we obtained
                        # from that attempt.
                        return attempt


                else:
                    return random.choice(list(set(subDict)))

        #If we can't find the value in the dictionary, we return the end token.
        else:
            return end


def generateLine():
    line = []

    #The first word is a random word from the set of first words obtained from
    # the training set.
    first = getRandomValueFromDict(firstWords,"")
    line.append(first)

    #We attempt to predict the second word based on the first word.
    second = getRandomValueFromDict(secondWords, first)
    third = end

    if not second == end:
        line.append(second)
        #We attempt to predict the third word based on the first two words.
        third = getRandomValueFromDict(thirdWords, (first, second))
        if not third == end:
            line.append(third)
        else:
            #If the first attempt was unsuccessful, we attempt to predict the
            # third word based only on the second word.
            third = getRandomValueFromDict(secondWords, second)
            if not third == end:
                line.append(third)
            else:
                third = end
    else:
        second = end

    #If we have successfully predicted the last two words, we continue predicting the next words.
    if (not third == end and not second == end):
        next = ""
        #We will continue generating new words until we reach a dead end or until we reach the maximum number of words per line.
        while(not next == end and len(line) <= MAX_NUMBER_OF_WORDS_PER_LINE):
            #We attempt to predict the next word based on the the previous three words.
            next = getRandomValueFromDict(thirdOrder,(first, second, third))
            if not next == end:
                line.append(next)
                first = second
                second = third
                third = next
            else:
                #If the first attempt was unsuccessful, we attempt to predict the next word based only on the previous two words.
                next = getRandomValueFromDict(secondOrder, (second, third))
                if not next == end:
                    line.append(next)
                    first = second
                    second = third
                    third = next
                else:
                    #If the first and second attempts were unsuccessful, we attempt to predict the next word based only on the previous word.
                    next = getRandomValueFromDict(firstOrder, third)
                    if not next == end:
                        line.append(next)
                        first = second
                        second = third
                        third = next
                    else:
                        #If all three attempts were unsuccessful, we give up.
                        next = end

    return line

def main():
    data = readFromFile()
    train(data)
    play = []
    print("Alloweth me to gen'rate a playeth f'r thee, mine own lief sir 'r mistress...")
    for i in range(0, NUMBER_OF_LINES):
        line = generateLine()
        play.append(' '.join(line))

    print("Those gents calleth not me shakespeare f'r nothing:\n")
    i = 1
    for line in play:
        print('\t',i, ": ", line,'\n')
        i += 1

if __name__== "__main__":
  main()
