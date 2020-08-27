import re
import sys
import parser
import math


def notinlist(l, t):
    for i in l:
        if t == i:
            return False
    return True


def multiply(a, b):
    result = []
    for i in a:
        for j in b:
            t = i.copy()
            t.append(j)
            if notinlist(result, sorted(t)):
                result.append(sorted(t))
    return result


def genterms(d, m):
    xlist = ['x' + str(i) for i in range(d)]
    tlist = []
    tlist.append(['w', '1'])  # code changed here
    if m > 0:
        for i in range(d):
            tlist.append(['w' + str(i), 'x' + str(i)])
    result = [['x' + str(i)] for i in range(d)]
    for i in range(2, m + 1):
        result = multiply(result, xlist)
        for i in result:
            t = 'w'
            for j in i:
                t = t + j[1:]
            tlist.append([t, '*'.join(i)])
    return tlist


def readyxy():
    xlist = []
    ylist = []
    for line in sys.stdin:
        line = re.sub(re.compile('#.*?\n'), '', line)
        line = line.replace('\t', '')
        if len(line) != 0:
            try:
                dataline = [float(x.strip()) for x in line.split(',')]
                xlist.append(dataline[0:-1])
                ylist.append(dataline[-1])
            except ValueError:
                print('Data invalid, please check the data!')
                sys.exit()
    if len(xlist) != len(ylist):
        print('The amounts of xs and ys are not consistent, please check the data.')
        sys.exit()
    return xlist, ylist


def regression(xlist, ylist, tlist):
    # initialize w with 1
    lr = 0.005
    size_t = len(xlist)
    n = int(size_t / 10)
    # 10 fold validation
    rmse_list = []
    weight_list = []
    for i in range(10):
        xlist_test = xlist[i * n:(i + 1) * n]
        xlist_train = xlist[:i * n] + xlist[(i + 1) * n:]
        ylist_test = ylist[i * n:(i + 1) * n]
        ylist_train = ylist[:i * n] + ylist[(i + 1) * n:]
        for term in tlist:
            term[0] = 1
        # train data with training set
        size_train = len(xlist_train)
        dim = len(xlist_train[0])
        for i in range(size_train):
            xs = xlist_train[i]
            y = ylist_train[i]
            for i in range(dim):
                exec('x' + str(i) + '=' + str(xs[i]))
            y_hat = 0
            for term in tlist:
                eqs = term[1]
                eq = parser.expr(eqs).compile()
                term_x = eval(eq)  # calculate term_x
                term_result = term[0] * term_x  # calculate term_x times weight
                y_hat += term_result
            error = y - y_hat
            if error > 0:
                for term in tlist:
                    eqs = term[1]
                    eq = parser.expr(eqs).compile()
                    term_x = eval(eq)  # calculate term_x
                    term[0] += lr * term_x
            elif error < 0:
                for term in tlist:
                    eqs = term[1]
                    eq = parser.expr(eqs).compile()
                    term_x = eval(eq)  # calculate term_x
                    term[0] -= lr * term_x
            else:
                pass
        weight = [term[0] for term in tlist]
        weight_list.append(weight)
        # test data for RMSE
        size_test = len(xlist_test)
        error_square_list = []
        for i in range(size_test):
            xs = xlist_test[i]
            y = ylist_test[i]
            for i in range(dim):
                exec('x' + str(i) + '=' + str(xs[i]))
            y_hat = 0
            for term in tlist:
                eqs = term[1]
                eq = parser.expr(eqs).compile()
                term_x = eval(eq)  # calculate term_x
                term_result = term[0] * term_x  # calculate term_x times weight
                y_hat += term_result
            error_square = (y_hat - y) ** 2
            error_square_list.append(error_square)
        rmse = math.sqrt(sum(error_square_list) / (size_test - m - 1))
        rmse_list.append(rmse)
    rmse_avg = sum(rmse_list) / len(rmse_list)
    return rmse_avg, weight_list


xlist, ylist = readyxy()
dim = len(xlist[0])
threshold = 0.01  # for elbow method
prev = 0.0
m = 1
while True:
    tlist = genterms(dim, m)
    rmse, weight_list = regression(xlist, ylist, tlist)
    if m == 1:
        prev = rmse
    elif prev - rmse < threshold:
        break
    m = m * 2
m = int(m / 2)
tlist = genterms(dim, m)
rmse, weight_list = regression(xlist, ylist, tlist)
weight_result = []
for i in range(len(tlist)):
    sum_list = []
    for w in weight_list:
        sum_list.append(w[i])
    avg = sum(sum_list) / 10
    weight_result.append(avg)
weights = genterms(dim, m)
weight_sig = [w[0] for w in weights]
for i in range(len(tlist)):
    print('{}* = {:.1f}'.format(weight_sig[i], weight_result[i]))
