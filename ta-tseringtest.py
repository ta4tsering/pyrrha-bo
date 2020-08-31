from pybo import WordTokenizer
tokenizer = WordTokenizer()

user_input = input("Enter the plain text\n")

tokens = tokenizer.tokenize(user_input)
for _ in range (len(tokens)):
    tokens[_]
