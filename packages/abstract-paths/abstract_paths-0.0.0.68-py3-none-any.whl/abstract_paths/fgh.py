from abstract_utilities import *
texts = "/home/computron/signal-chats/joe/chat.md"

content = read_from_file(texts)
for cont in content.split('\n'):
    input(cont)
