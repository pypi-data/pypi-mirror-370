# Correct execution with heavy computation

def compute_heavy():
    data = [i*i for i in range(3)]
    summ = 0
    print("Performing sum")
    for i in data:
        print("Adding")
        summ += i
    return summ

x = compute_heavy()
print(x)
