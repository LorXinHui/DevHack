import random

def grade():
    marks = random.randint(0, 100)

    if 80 <= marks <= 100:
        return 'A'
    elif 70 <= marks <= 79:
        return 'B'
    elif 60 <= marks <= 69:
        return 'C'
    elif 50 <= marks <= 59:
        return 'D'
    else:
        return 'E'
    