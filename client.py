# It is a messy client (do better next time)

import os
import sys
import readline
import socket
from _thread import *

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 6113

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

clear_screen()
if len(sys.argv) > 1:
    hostname = sys.argv[1]
else:
    hostname = input('Please, input local address or hostname: ')

# I should check this on server too, but eh...
def ask_for_name_if_needed(name):
    while not name.replace('_', '').isalnum() or len(name) > 15:
        print('Name can contain only letters, digits, symbol \'_\' ' +
            'and cannot be longer than 15 characters')
        name = input('Please, try again: ')
    return name

if len(sys.argv) > 2:
    name = sys.argv[2]
    name = ask_for_name_if_needed(name)
else:
    name = input('Please, input your name: ')
    name = ask_for_name_if_needed(name)

try:
    client.connect((hostname, port))
except:
    print('Can not connect!')
    exit()

client.send(name.encode())
respond = client.recv(1024)
print(respond.decode())

def handle_server_messages():
    while True:
        try:
            message = client.recv(1024).decode()
            if message:
                print(message.rstrip())
            else:
                print('Can not reach server. Please, quit')
                break
        except Exception as ex:
            print('Can not reach server. Please, quit')
            break

start_new_thread(handle_server_messages, ())

user_input = ' '
while user_input != '!quit' and user_input != '!q':
    try:
        if user_input != '' and not user_input.isspace():
            if user_input == '!s' or user_input == '!sync':
                clear_screen()
            client.send(user_input.encode())
        user_input = input()
    except (KeyboardInterrupt, EOFError, BrokenPipeError):
        break

client.close()
print('Thank you for chatting!')
