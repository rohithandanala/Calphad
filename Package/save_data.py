import csv

def save_data(data):
    with open('my_cs.csv','w',newline='') as f:
        a = csv.writer(f)
        d = data.parameters
        type(d)
        for i in d:
            for j in d[i]:
                x = []
                x.append(i)
                for l in j:
                    x.append(l)
                a.writerow(x)
                