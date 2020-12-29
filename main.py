# KnockOut Machine
# Heiner Buescher, 28.12.2020
import csv
import locale


# TODO add calculation
def calculateTime():
    return None


def updateScores(inputName, newTime):
    locale.setlocale(locale.LC_ALL, '')
    DELIMITER = ';' if locale.localeconv()['decimal_point'] == ',' else ','
    row = [inputName, newTime + "s"]

    with open('timeList.csv', 'a', newline='') as timeFile:
        writer = csv.writer(timeFile, delimiter=DELIMITER)
        writer.writerow(row)


def main():
    newTime = input("Bitte Zeit eingeben: ")
    inputName = str(input("Bitte Namen eingeben: "))

    updateScores(inputName, newTime)


main()
