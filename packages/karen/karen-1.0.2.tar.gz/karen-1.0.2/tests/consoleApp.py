from karen.evaluate import evaluate
from karen.getCombo import *

while True:

    inputString = input(">> ") + " " # space added so that commands with no arguments are easily handled
    while len(inputString) > 0 and inputString[0] in " !":
        inputString = inputString[1:]

    if len(inputString) > 4 and inputString[:5] == "help ":
        print("!eval [combo]: evaluates the given combo")
        print("!exit : closes the terminal")

    elif len(inputString) > 4 and inputString[:5] == "eval ":
        print(evaluate(inputString[5:], simpleMode=True))

    elif len(inputString) > 5 and inputString[:6] == "evala ":
        print(evaluate(inputString[6:]))

    elif len(inputString) > 5 and inputString[:6] == "evaln ":
        print(evaluate(inputString[6:], printWarnings=False))

    elif len(inputString) > 5 and inputString[:6] == "combo ":
        print(getCombo(inputString[6:], simpleMode=True))

    elif len(inputString) > 5 and inputString[:7] == "combos ":
        print(listCombos())

    elif len(inputString) > 4 and inputString[:5] == "exit ":
        break

    else:
        print("Command not recognised, use '!help' to see a list of commands")