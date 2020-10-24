import numpy as np
import pandas as pd
import math
import json

# part_1

data = pd.read_csv('data.csv')
k = 4

users = np.delete(np.array(data), 0, axis=0).shape[0]
movies = np.delete(np.array(data), 0, axis=0).shape[1]


def count_sim(user_index, precision):
    res = {}
    tmp_data = data.drop(columns=[data.columns[0]])
    for user in range(0, users):
        sim_uv = 0
        sim_u = 0
        sim_v = 0
        if user != user_index:
            pairs = tmp_data.iloc[[user, user_index]]
            pairs = pairs.transpose()
            pairs = pairs[(pairs[user] != -1) & (pairs[user_index] != -1)]
            for _, row in pairs.iterrows():
                sim_uv += row[user] * row[user_index]
                sim_u += row[user] ** 2
                sim_v += row[user_index] ** 2
            res[user] = round(sim_uv / (math.sqrt(sim_u) * math.sqrt(sim_v)), 3)

    sim = {z: v for z, v in sorted(res.items(), key=lambda i: i[1], reverse=True)[:precision]}
    return sim


def avg_rate_for_needed_tuple(tuple, precision):
    res = {}
    tmp_data = data.drop(columns=[data.columns[0]])
    transposed_data = tmp_data.transpose()
    for user in tuple:
        movie_count = 0
        user_rate = 0
        rates = transposed_data[user]
        for rate in rates:
            if rate != -1:
                movie_count += 1
                user_rate += rate
        res[user] = round(user_rate / movie_count, precision)
    return res


def rate_the_films(user_index, precision):
    unrated_movies = []
    for movie in range(1, movies):
        if data.transpose()[user_index][movie] == -1:
            unrated_movies.append(" Movie " + str(movie))

    tuple = count_sim(user_index, precision)
    tuple_avg = avg_rate_for_needed_tuple(tuple, precision)
    avg_user = avg_rate_for_needed_tuple([user_index], precision)[user_index]
    rates = {}
    for movie in unrated_movies:
        dividend = 0
        divider = 0
        for user in tuple:
            rate = data.loc[user, movie]
            if rate == -1:
                continue
            divider += tuple[user]
            dividend += tuple[user] * (data.loc[user, movie] - tuple_avg[user])
        rates[movie] = round(avg_user + dividend / divider, 3)
    return rates


# part_2

# Идея подхода - составить новую выборку, с учетом только фильмов просмотренных дома и в выходные

context_day = pd.read_csv('context_day.csv')
context_place = pd.read_csv('context_place.csv')

weekends = [' Sat', ' Sun']
place = [' h']


def count_sim_2(user_index, precision):
    res = {}
    tmp_data = data.drop(columns=[data.columns[0]])
    tmp_days = context_day.drop(columns=[context_day.columns[0]])
    tmp_places = context_place.drop(columns=[context_place.columns[0]])
    for user in range(0, users):
        sim_uv = 0
        sim_u = 0
        sim_v = 0
        if user != user_index:
            pairs = tmp_data.iloc[[user, user_index]]
            pairs = pairs.transpose()
            pairs = pairs[(pairs[user] != -1) & (pairs[user_index] != -1)]
            for index, row in pairs.iterrows():
                if ((tmp_days[index][user] in weekends) & (tmp_places[index][user] in place)) | (
                        (tmp_days[index][user_index] in weekends) & (tmp_places[index][user_index] in place)):
                    sim_uv += row[user] * row[user_index]
                    sim_u += row[user] ** 2
                    sim_v += row[user_index] ** 2
            if sim_u == 0 & sim_v == 0:
                res[user] = 0
            else:
                res[user] = round(sim_uv / (math.sqrt(sim_u) * math.sqrt(sim_v)), 3)

    sim = {z: v for z, v in sorted(res.items(), key=lambda i: i[1], reverse=True)[:precision]}
    return sim


def avg_rate_for_needed_tuple_2(tuple, precision, user_index):
    res = {}
    tmp_data = data.drop(columns=[data.columns[0]])
    tmp_days = context_day.drop(columns=[context_day.columns[0]])
    tmp_places = context_place.drop(columns=[context_place.columns[0]])
    transposed_data = tmp_data.transpose()
    for user in tuple:
        movie_count = 0
        user_rate = 0
        rates = transposed_data[user]
        for movie in range(1, movies):
            for rate in rates:
                if (((tmp_days[" Movie " + str(movie)][user] in weekends) |
                     (tmp_days[" Movie " + str(movie)][user_index] in weekends))
                        &
                        ((tmp_places[" Movie " + str(movie)][user] in place) | (tmp_places[" Movie " + str(movie)][
                                                                                    user_index] in place))):
                    if rate != -1:
                        movie_count += 1
                        user_rate += rate
            if movie_count != 0:
                res[user] = round(user_rate / movie_count, precision)
            else:
                res[user] = 0
    return res


def rate_the_films_2(user_index, precision):
    unrated_movies = []
    for movie in range(1, movies):
        if data.transpose()[user_index][movie] == -1:
            unrated_movies.append(" Movie " + str(movie))

    tuple = count_sim_2(user_index, precision)
    tuple_avg = avg_rate_for_needed_tuple_2(tuple, precision, user_index)
    avg_user = avg_rate_for_needed_tuple_2([user_index], precision, user_index)[user_index]
    rates = {}
    for movie in unrated_movies:
        dividend = 0
        divider = 0
        for user in tuple:
            rate = data.loc[user, movie]
            if rate == -1:
                continue
            divider += tuple[user]
            dividend += tuple[user] * (data.loc[user, movie] - tuple_avg[user])
        rates[movie] = round(avg_user + dividend / divider, 3)
    return {z: v for z, v in sorted(rates.items(), key=lambda i: i[1], reverse=True)[:1]}


# формируем результат и пишем в json
result = {
    'user': 16,
    '1': rate_the_films(15, k),
    '2': rate_the_films_2(15, 4)
}
print(result)

with open('result.json', 'w') as fp:
    json.dump(result, fp, indent=4)
