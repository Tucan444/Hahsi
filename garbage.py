def get_result(size):
    size += 1      # increasing to get away from 0
    x = [1 for _ in range(size)]
    for i in range(size - 1):  # getting original size
        x = [sum(x[:i+1]) for i in range(size)]
    print(x[-1])


get_result(20)
