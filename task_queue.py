"""
Простая(тупая) FIFO-очередь задач
"""
__author__ = 'a.medvedev'

tasks_a = []


def add_task(task):
    tasks_a.append(task)


def loop():
    while True:
        task = tasks_a.pop(0)
        if task is not None:
            task()


def main():
    pass


if __name__ == '__main__':
    main()