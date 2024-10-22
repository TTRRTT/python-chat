# It is a messy server (do better next time)

import os
import readline
from datetime import datetime
from _thread import *
import socket
from requests import get

hostname = socket.gethostname()
hostaddr, port = socket.gethostbyname(hostname), 6113

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((hostaddr, port))
server.listen(100)

try:
    public_ip = get('https://api.ipify.org').text
except:
    public_ip = '<connection error>'

help_text = ('\033[92mAwailable commands:\033[0m\n'
        '!h or !help - print this message\n'
        '!q or !quit - disconnect and leave chat\n'
        '!s or !sync - syncronize chat history with server\n'
        '!ls or !list - view list of all connected chaters\n'
        '!p <name>#<tag> - text personal message to user \'<name>#<tag>\'\n'
        '\033[92mAlso, you can use your terminal shortcuts:\033[0m\n'
        'Arrows up/down - navigate through input history\n'
        'Ctrl-W - delete one word before\n'
        'Ctrl-U - delete all before cursor\n'
        'Ctrl-K - delete all after cursor\n'
        '(and etc: https://linuxhandbook.com/linux-shortcuts/)\n')
hello_text = '\033[92mWelcome to chat!\033[92m\n' + help_text

clients = []
history_file_name = 'chat.hist'
history_file = open(history_file_name, 'w')
history_file.close()

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def print_server_info():
    print('Private IP:', hostaddr)
    print('Port:', port)
    print('Hostname:', hostname)
    print('Public IP:', public_ip, '\n')

def get_time():
    return '\033[92m[' + datetime.now().strftime('%H:%M:%S') + ']\033[0m'

def get_client_by_name(name):
    for client in clients:
        if client[-1] == name:
            return client
    return None

def remove_client(client):
    if client in clients:
        clients.remove(client)
        message = get_time() + ' \033[95mSystem: client ' + client[-1] + ' disconnected\033[0m' 
        print(message)
        broadcast(message, None)
    else:
        print(get_time(), 'Client', client[-1], 'already removed')

def send_history_to(client):
    data = '\033[92mChat history restored (last 50 messages).\033[0m'
    client[0][0].send(data.encode())

    with open(history_file_name) as file:
        for line in (file.readlines()[-50:]):
            if not line.isspace():
                client[0][0].send(line.encode())

def shutdown_server():
    print('\n' + get_time(), 'Shutting down server...')

    print(get_time(), 'Disconnecting clients')
    for client in clients:
        try:
            client[0][0].close()
        except:
            print('Client', client[-1], 'already disconnected')
    print(get_time(), 'All clients disconnected')

    server.close()
    print('\n' + get_time(), 'Server shuted down')

def handle_client(client):
    send_history_to(client)
    client[0][0].send('\n'.encode())
    client[0][0].send(hello_text.encode())

    while True:
        try:
            message = client[0][0].recv(2048).decode()
            if message:
                if message == '!h' or message == '!help':
                    client[0][0].send((get_time() + ' ' + help_text).encode())
                    print(get_time(),
                        'Help was asked by', client[-1])
                elif message == '!ls' or message == '!list':
                    message = 'List of all chaters:\n'
                    for i, cl in enumerate(clients):
                        message += str(i + 1) + '. ' + cl[-1] + '\n'
                    client[0][0].send(
                        (get_time() + ' ' + message).rstrip().encode())
                    print(get_time(),
                        'List of chaters was asked by', client[-1])
                elif message == '!s' or message == '!sync':
                    send_history_to(client)
                    print(get_time(),
                        'Syncronization was asked by', client[-1])
                elif message.startswith('!p'):
                    parts = message[3:].partition(' ')
                    to_user = parts[0]
                    message = f'{get_time()} \033[96m{client[-1]} (PM): {parts[2]}\033[0m'
                    cl = get_client_by_name(to_user)
                    if cl == None:
                        client[0][0].send((get_time() +
                            ' \033[96mCan not find user \'' +
                            to_user + '\'. Message not sent.\033[0m').encode())
                    else:
                        cl[0][0].send(message.encode())
                    print(message)
                else:
                    message = get_time() + ' ' + client[-1] + ': ' + message
                    print(message)
                    with open(history_file_name, 'a') as file:
                        file.write(message + '\n')
                    broadcast(message, client)
            else:
                remove_client(client)
                break
        except Exception as e:
            print(e)
            remove_client(client)
            continue

def accept_client(conn, addr):
    name = conn.recv(1024).decode()
    clients.append(((conn, addr), name,
        name + '#' + addr[0].rsplit('.', 1)[-1]))
    message = get_time() + ' \033[95mSystem: client ' + clients[-1][-1] + ' connected\033[0m'
    print(message)
    broadcast(message, None)

def broadcast(message, from_client):
    for cl in clients:
        if cl != from_client:
            try:
                cl[0][0].send(message.encode())
            except:
                remove_client(cl)

def accept_and_handle_client(client):
    accept_client(client[0], client[1])
    handle_client(clients[-1])

def handle_accepts():
    while True:
        client = server.accept()
        start_new_thread(accept_and_handle_client, (client,))

def handle_input():
    user_input = ''
    while user_input != 'quit':
        try:
            user_input = input()
        except (KeyboardInterrupt, EOFError):
            break

clear_screen()
print_server_info()
print('(Press Ctrl-C or type \'quit\' to shutdown server)')
print(get_time(), 'Server is up (100 connections max)\n')

start_new_thread(handle_accepts, ())
handle_input()

shutdown_server()
