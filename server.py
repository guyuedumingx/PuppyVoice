from handler import Handler

handler = Handler()
while True:
    msg = input(">>>")    
    handler.handle(msg)