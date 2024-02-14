import math


numbers = [767, 1517, 763, 763, 763, 779, 788, 785]
filteredNumbers = []



def countStDev(numbers):
    avg = math.fsum(numbers) / len(numbers)
    squareSum = 0

    # count square sum
    for number in numbers:
        squareSum = squareSum + abs(number - avg)**2

    var = (1/len(numbers)) * squareSum # count var

    standardDeviation = math.sqrt(var) # count st. deviation


    return standardDeviation, avg


# count first st. dev
standardDeviation, avg = countStDev(numbers)

# filter numbers
for number in numbers:
    if abs(avg - number) < standardDeviation:
        filteredNumbers.append(number)


# count second st. dev from filtered numbers
filteredStandardDeviation, filteredAvg = countStDev(filteredNumbers)


print(filteredNumbers)
print(f"Standard deviation 1: {standardDeviation}, avg: {avg}, filtered: {filteredStandardDeviation}, {filteredAvg}")