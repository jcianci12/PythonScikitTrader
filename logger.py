import datetime

def logger(*args):
    now = datetime.datetime.now()
    message = ' '.join(map(str, args))
    log_message = f'{now}: {message}'
    print("logging",log_message)
    with open('log.txt', 'a') as file:
        file.write(log_message + '\n')