import numpy as np
import pandas as pd

import os

from sklearn.preprocessing import RobustScaler

CONTROL_REAL = {'etilEnipS', 'frimija26', 'LACHATATATA', 'Cocochamelle', 'Ryujin', 'D0ntCryBB', 'BTCto1M',
                'Cesar Polska', 'rorro29', 'Hari86'}
CONTROL_BOTS = {'kelly59242'}
# , 'Juju75002', 'renaud220', 'Zizou2885', 'patouf97320', 'Titeuf0713', 'titi84330', 'volpi84120'}
RESULT_DIR = 'results'
FN_POP, FN_BEST = 'population.npy', 'best_individual.npy'

scaler = RobustScaler()

data = pd.read_csv('player_processed.csv', index_col=0).dropna(how="all").fillna(0)
scaled = scaler.fit_transform(data)
scaled[scaled > 10] = 10
scaled[scaled < -10] = -10

data_scaled = pd.DataFrame(scaled,
                           columns=data.columns,
                           index=data.index)

real_data = data_scaled.loc[CONTROL_REAL, :]
bot_data = data_scaled.loc[CONTROL_BOTS, :]


def fitness(chrom):
    real_sel = real_data.loc[:, chrom]
    bot = bot_data.loc[:, chrom]
    measures = list()

    for _, real in real_sel.iterrows():
        mh = np.linalg.norm(bot - real)
        measures.append(mh)
    fit_len = np.sum(chrom) / 2
    fit_val = np.mean(measures)

    return fit_val - fit_len


def selection(fitness, size=10):
    '''Stochastic universal sampling
    f = np.sum(fitness)
    n = fitness.shape[0] + 1
    p = f / n

    start = np.random.uniform(low=0, high=p)
    pointers = [start + i * p for i in range(n - 1)]

    keep = list()
    for point in pointers:
        i = 0
        while np.sum(fitness[:i]) < point:
            i += 1
        keep.append(i % (n - 1))

    half = n // 2
    return keep[:half], keep[half:]
    '''

    '''Tournament selection'''
    keep = []
    ml = len(fitness)

    while len(keep) < ml:
        tournament = np.random.choice(range(ml), replace=False, size=size)
        keep.append(tournament[np.argmax(fitness[tournament])])

    half = ml // 2
    return keep[:half], keep[half:]


def cross(left, right):
    '''2 point Crossover'''
    r = np.random.randint(low=1, high=len(left), size=2)
    r.sort()
    r1, r2 = r

    new_left = np.zeros_like(left)
    new_right = np.zeros_like(right)

    new_left[:r1] = left[:r1]
    new_right[:r1] = right[:r1]
    new_left[r1:r2] = right[r1:r2]
    new_right[r1:r2] = left[r1:r2]
    new_left[r2:] = left[r2:]
    new_right[r2:] = right[r2:]

    return new_left, new_right


def mutate(chrom):
    '''Bit flip mutation'''
    p = 1/len(chrom)
    mut_vec = np.random.choice(a=[False, True], size=len(chrom), p=[1 - p, p])
    new_chrom = np.zeros_like(chrom)

    new_chrom[mut_vec] = ~chrom[mut_vec]
    new_chrom[~mut_vec] = chrom[~mut_vec]

    return new_chrom


load = True

c_len = len(data_scaled.columns)
pop_size = 500
epochs = 100
pop = np.random.choice(a=[False, True], size=(pop_size, c_len))
tmp_pop = np.random.choice(a=[False, True], size=(pop_size, c_len))
fit = np.zeros(shape=pop_size)
best = (np.zeros(shape=c_len), -1)

if load:
    best = np.load(os.path.join(RESULT_DIR, FN_BEST), allow_pickle=True)
    #pop = np.load(os.path.join(RESULT_DIR, FN_POP), allow_pickle=True)


for i in range(epochs):
    if i > 0:
        pop[np.argmin(fit)] = best[0]
    for i_fit, individual in enumerate(pop):
        fit[i_fit] = fitness(individual)
    left_idx, right_idx = selection(fit)
    for idx, (l_i, r_i) in enumerate(zip(left_idx, right_idx)):
        tmp_pop[idx], tmp_pop[idx + len(left_idx)] = cross(pop[l_i], pop[r_i])
    for idx, chrom in enumerate(tmp_pop):
        pop[idx] = mutate(chrom)
    new_best = (pop[np.argmax(fit)], np.max(fit))
    if new_best[1] > best[1]:
        best = new_best
    print('[Epoch: {}] - Best fit: {:.4f}\t Average pop fit: {:.4f}\t Solution length: {}'.format(i+1,
                                                                                                  best[1],
                                                                                                  np.mean(fit),
                                                                                                  np.sum(best[0])))
    np.save(os.path.join(RESULT_DIR, FN_POP), pop)
    np.save(os.path.join(RESULT_DIR, FN_BEST), best)
