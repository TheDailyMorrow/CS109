import csv
import numpy as np
from cpi import inflate, update
# import pandas as pd
# from datetime import date
# import matplotlib.pyplot as plt
# import random
# import statistics


def adjust_for_inflation(number, date):
    # cpi.inflate(past money, year) = current money
    year = date[-4:]
    if '-' in year:
        year = date[:4]
    year = int(year)
    if year < 1913:
        year = 1913
    return inflate(number, year)


def extract_fin_data(data_set):
    # row 19732 is jank, 2 other rows
    filename = 'financial_data.csv'

    with open(filename, newline='') as csvfile:
        datafile = csv.reader(csvfile, delimiter=' ', quotechar='|')
        next(csvfile)

        # index = 0
        # max_size = 500  # len(datafile)

        for row in datafile:
            values = row[0].split(',')

            budget = 0
            revenue = 0
            runtime = 0
            vote_average = 0
            vote_count = 0
            release_date = 0
            popularity = 0
            id_num = 0
            date = False

            if len(values[5]) > 0:  # check for a date
                date = True
                release_date = values[5]
            if len(values[0]) > 0:
                budget = int(values[0])
                if date:
                    budget = adjust_for_inflation(budget, release_date)
                if budget > 440000000:
                    budget = 0
            if len(values[1]) > 0:
                revenue = int(values[1])
                if date:
                    revenue = adjust_for_inflation(revenue, release_date)
                if revenue > 3800000000:
                    revenue = 0
            if len(values[2]) > 0:
                runtime = int(values[2])
            if len(values[3]) > 0:
                vote_average = float(values[3])
            if len(values[4]) > 0:
                vote_count = int(values[4])
            if len(values[6]) > 0:
                popularity = float(values[6])
            if len(values[7]) > 0:
                id_num = int(values[7])

            data_set[id_num] = [budget, revenue, runtime, vote_average, vote_count, release_date, popularity]

            # index += 1
            # if index > max_size - 1:
            #     break


def make_groups(data_set, index):
    # break it up into 5 percentiles
    rating_index = 3
    groups = []
    for movie_key in data_set:
        data_point = data_set[movie_key][index]
        rating = data_set[movie_key][rating_index]

        if data_point == 0 or rating == 0:
            continue

        if index == 5:
            if '-' in data_point:
                temp_split = data_point.split('-')
                year = temp_split[0]
                month = temp_split[1]
                day = temp_split[2]
            else:
                temp_split = data_point.split('/')
                year = temp_split[2]
                month = temp_split[0]
                day = temp_split[1]

            if len(month) < 2:
                month = '0' + month
            if len(day) < 2:
                day = '0' + day
            data_point = int(year + month + day)

        groups.append([data_point, rating])

    groups.sort()
    group_size = int(len(groups)/5)
    group1 = groups[:group_size]
    group2 = groups[group_size:2*group_size]
    group3 = groups[2*group_size:3*group_size]
    group4 = groups[3*group_size:4*group_size]
    group5 = groups[4*group_size:]

    print(group1[0][0])
    print(group1[len(group1) - 1][0])
    print(group2[0][0])
    print(group2[len(group2) - 1][0])
    print(group3[0][0])
    print(group3[len(group3) - 1][0])
    print(group4[0][0])
    print(group4[len(group4) - 1][0])
    print(group5[0][0])
    print(group5[len(group5) - 1][0])
    print("--------------------")

    return group1, group2, group3, group4, group5


def calcMean(data):
    return sum(data)/len(data)


def bootstrap(pop1, pop2):
    # Run a bootstrap experiment
    n_trials = 10000
    size1 = len(pop1)
    size2 = len(pop2)
    ratings1 = []
    ratings2 = []

    for i in range(size1):
        ratings1.append(pop1[i][1])
    for i in range(size2):
        ratings2.append(pop2[i][1])

    countDiffGreaterThanObserved = 0
    avg1 = calcMean(ratings1)
    avg2 = calcMean(ratings2)
    data_diff = abs(avg1 - avg2)
    print(avg1)
    print(avg2)
    print('Difference in means:')
    print(data_diff)
    # make the universal population
    totalPop = list.copy(ratings1)
    totalPop.extend(ratings2)

    # print('starting bootstrap')
    for i in range(n_trials):
        sample1 = np.random.choice(totalPop, size1, replace=True)
        sample2 = np.random.choice(totalPop, size2, replace=True)
        mean1 = calcMean(sample1)
        mean2 = calcMean(sample2)
        diff = abs(mean1 - mean2)

        # count how many times the statistic is more extreme
        if diff >= data_diff:
            countDiffGreaterThanObserved += 1

    # compute the p-value
    p = float(countDiffGreaterThanObserved) / n_trials
    print('P-value:')
    print(p)
    print("--------------------")


def calc_statistical_diff(data_set, index, run):

    if run:
        if index == 0:
            print("Budget data")
        elif index == 1:
            print("Revenue data")
        elif index == 2:
            print("Runtime data")
        elif index == 5:
            print("Release Year Data")

        group1, group2, group3, group4, group5 = make_groups(data_set, index)
        bootstrap(group1, group2)
        bootstrap(group2, group3)
        bootstrap(group3, group4)
        bootstrap(group4, group5)

    return 0


def main():
    # created data_set will have movie_id as key and [rating, budget, box office] as value
    update()
    data_set = {}
    extract_fin_data(data_set)
    print('data formatted...')

    calc_statistical_diff(data_set, 0, False)  # Budget
    calc_statistical_diff(data_set, 1, False)  # Revenue
    calc_statistical_diff(data_set, 2, False)  # Runtime
    calc_statistical_diff(data_set, 5, True)  # Release Year

    return 0


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
