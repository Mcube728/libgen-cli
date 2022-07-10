import time
def load():
    '''
    A very simple loading animation. 
    Credit: https://stackoverflow.com/questions/7039114/waiting-animation-in-command-prompt-python
    '''
    animation = "|/-\\"
    idx = 0
    while True:
        print(' ',animation[idx % len(animation)], end="\r")
        idx += 1
        time.sleep(0.1)

load()