

PENDINGORDER = False
def setpending(value):
    print("setting pending order to ",value)
    global PENDINGORDER
    PENDINGORDER = value

def getpending():
    global PENDINGORDER
    print("returning pending order ",PENDINGORDER)
    return PENDINGORDER