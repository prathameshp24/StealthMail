#!/usr/bin/env python
import sys
import stem
import os
from stem.control import Controller
from stem.process import launch_tor_with_config
from generate_qr import generate_qr
from flask import Flask, request
import datetime
import urllib.parse
import logging
import keys_manager

sys.tracebacklimit = 0
path = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path = path + "files/keys/"
SOCKS_PORT = 9050
CONTROL_PORT = 9051
user_sep = '#USERNAME#'
msg_sep = '#MESSAGE#'
line_sep = '#NEW_LINE#'
messages = []
server = Flask('StealthMail Chat Server')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def print_lines(line):
    if 'Bootstrapped' in line:
        print(line)

@server.route('/')
def index():
    return line_sep.join(messages)

@server.route('/send')
def query_example():
    encrypted_text = request.args.get('encrypted_text')
    unique_key = request.args.get('unique_key')
    unique_key = urllib.parse.unquote(unique_key)
    encrypted_text = urllib.parse.unquote(encrypted_text)
    messages.append(msg_sep.join([unique_key, encrypted_text]))
    return line_sep.join(messages)

def stop():
    raise Exception("Program Closed")

def create_hidden_service_and_server():
    tor_path_file = open(path + "files/others/tor_path_file.txt", "r+")
    tor_path = str(tor_path_file.read())

    print('Launching Tor...')

    tor = None

    try:
        tor = launch_tor_with_config(tor_cmd=tor_path, init_msg_handler=print_lines,
                                     config={'SocksPort': str(SOCKS_PORT), 'ControlPort': str(CONTROL_PORT)})
        print("Launched Tor successfully!")
    except OSError as exc:
        if "Maybe it's not in your PATH" in str(exc):
            print("'tor' isn't available on your system. Maybe it's not in your PATH."
                  "\nPlease check the Tor project documentation to know how to do it. Or just search it online!"
                  "\nTry to configure Onymochat with Tor from the main menu (if you haven't already)"
                  "\nClosing...")
            stop()
        elif "doesn't exist" in str(exc) or \
             "isn't available on your system" in str(exc) or \
             "not the tor executable" in str(exc):
            print("Error in Tor Path. Please reconfigure Onymochat with Tor from the main menu."
                  "\nClosing...")
            stop()
        else:
            print("%s"
                  "\n\nTor might be already running. "
                  "\nIf the program fails, try the following:"
                  "\n- For Windows:"
                  "\n\t- Check the path to tor.exe. Make sure tor.exe resides in the Tor installation folder "
                  "with a directory structure similar to: Tor Browser\\Browser\\TorBrowser\\Tor\\tor.exe"
                  "\n\t- Try killing all previous instances of Tor using Task Manager. "
                  "Press ctrl + alt + delete and open Task Manager. Select Tor and click on End Task."
                  "\n- For Linux: Kill all previous instances of Tor and initiate Tor again."
                  "\n\t- $sudo killall tor"
                  "\n- Check which ports are already in use."
                  "\n\t- Windows: netstat -ano -p tcp"
                  "\n\t- Linux: sudo netstat --all --listening --numeric --tcp"
                  "\n" % exc)
    except Exception as exc:
        print(exc)

    try:
        controller = Controller.from_port()
    except stem.SocketError as exc:
        print("Unable to connect to tor on port " + str(SOCKS_PORT) + ": %s" % exc)
        tor.terminate()  
        stop()

    controller.authenticate()
    print('Controller authenticated & connected to port ' + str(controller.get_socks_listeners()[0][1]))

    hidden_services = controller.list_ephemeral_hidden_services()
    if len(hidden_services) > 0:
        print('Closing %d pre-existing hidden service(s):' % len(hidden_services))

    for hidden_service_id in hidden_services:
        controller.remove_hidden_service(hidden_service_id)
        print('- Closed a hidden service with ID %s', hidden_service_id)

    using_saved_keys = True
    server_name = "temporary_page"
    try:
        hidden_service_private_key, server_name = keys_manager.save_open_keys(filename="hidden_service_private_keys.txt",
                                                                              do_what="deploy",
                                                                              key_type="private key",
                                                                              name_type="hidden service and server",
                                                                              extra_stmt=" (leave empty to create one)")
    except Exception as e:
        using_saved_keys = False
        if str(e) != "Use private key without saving.":
            print("Some error occurred. " + str(e))
        hidden_service_private_key = str(input("\nInput private key for your hidden service "
                                               "(leave empty to create one): "))

    if hidden_service_private_key == "":
        hidden_service_private_key = None

    print('\nInitiating/resuming a hidden service (V3 Onion Service). Please wait...')

    try:
        if hidden_service_private_key:
            hidden_service = controller.create_ephemeral_hidden_service(
                {80: 6969},
                await_publication=True,
                key_type='ED25519-V3',
                key_content=hidden_service_private_key,
                detached=True
            )
        else:
            hidden_service = controller.create_ephemeral_hidden_service(
                {80: 6969},
                await_publication=True,
                key_content='ED25519-V3',
                detached=True
            )
    except stem.ProtocolError as exc:
        if "ADD_ONION response didn't have an OK status" in str(exc):
            if "Failed to decode RSA key" in str(exc):
                print("Error in decoding RSA key. The pre-saved/entered private key might be corrupted. "
                      "\nTry generating a hidden service with a different private key or by generating a new one.")
            else:
                print(exc)
                print("Try closing/killing Tor first, then try again later."
                      "\n- For Windows:"
                      "\n\t- Press ctrl + alt + delete and open Task Manager. Select Tor and click on End Task."
                      "\n- For Linux: "
                      "\n\t- $sudo killall tor")
            stop()
        else:
            print(exc)
            print("If you can't understand and fix this error, try reinstalling Onymochat.")
            stop()

    print('\nSuccessfully initialized a hidden service!')
    print('\nHidden Service Public Key: ' + str(hidden_service.service_id))

    if not hidden_service_private_key:
        hidden_service_private_key = str(hidden_service.private_key)
        print('\nHidden Service Private Key: ' + hidden_service_private_key)
        if using_saved_keys:
            with open(dir_path + "hidden_service_private_keys.txt", "a+") as file_object:
                file_object.seek(0)
                data = file_object.read(100)
                file_object.write(hidden_service_private_key)
        generate_qr(hidden_service_private_key, "hidden_service_private_key_" + server_name)
        hidden_service_public_key = str(hidden_service.service_id) + ".onion"
        generate_qr(hidden_service_public_key, "hidden_service_public_key_" + server_name)
    else:
        print('\nHidden Service Private Key: ' + hidden_service_private_key)

    print("\nShare the hidden service public key key with the persons you want to chat with.")
    print("You can use the same hidden service (same public key) to chat with multiple person(s) but this comes with "
          "the risk of sharing the same key with everyone, and someone might use them later to spam you.")
    print("Save the private keys of each hidden service somewhere. Use them later to resume those hidden services.")
    print('CAUTION: '
          'If you lose the private key, you will never be able to generate a hidden service with the same ID again!'
          '\nCAUTION: Do not share your private key with anyone. '
          'Otherwise they too will be able to create a hidden service with the same ID as yours!'
          '\n')
    print("The images of the QR codes for your hidden service's private key and public key are "
          "saved in the location " + path + "files/qr_codes/")
    print("You can take a print of the images as a backup for future use. Scanning the QR with any QR code scanner "
          "reveals the content.\n")
    print('Server: PRESS CTRL+C TO CLOSE THE SERVER.'
          '\n\nNot closing the server properly might raise other problems in future.'
          '\nYou might have to press CTRL+C several times in order to close the server.'
          '\nClosing the server will delete all of the existing chat history permanently.\n')

    server.run(port=6969)

    print('Exiting...')
    print('Server Closed.')
    controller.reset_conf()
    print('Controller reset.')
    controller.remove_ephemeral_hidden_service(hidden_service.service_id)
    print('Removed hidden service from controller.')
    if tor:
        tor.terminate()
        print('Closed Tor.')
    print('Goodbye!')
