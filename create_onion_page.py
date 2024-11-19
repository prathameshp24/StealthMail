#!/usr/bin/env python
from stem.control import Controller
import stem
from stem.process import launch_tor_with_config
import os
from flask import Flask
import logging
from generate_qr import generate_qr
import keys_manager

path = os.path.dirname(os.path.realpath(__file__)) + "/"
dir_path = path + "files/keys/"
SOCKS_PORT = 9050
CONTROL_PORT = 9051

server = Flask('Onymochat Webpage Server', template_folder='templates')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

html_file = open(path + "onion_webpage/index.html")
html_file_read = html_file.read()

def print_lines(line):
    if 'Bootstrapped' in line:
        print(line)

@server.route('/')
def index():
    return html_file_read

def stop():
    raise Exception("Program Closed")

def create_onion_page():
    tor_path_file = open(path + "files/others/tor_path_file.txt", "r+")
    tor_path = str(tor_path_file.read())

    print('Launching Tor...')

    tor = None

    try:
        tor = launch_tor_with_config(tor_cmd=tor_path, init_msg_handler=print_lines,
                                     config={'SocksPort': str(SOCKS_PORT), 'ControlPort': str(CONTROL_PORT)})
        print("Launched Tor successfully!")
    except OSError as exc:
        if (str(exc)).find("Maybe it's not in your PATH") != -1:
            print("'tor' isn't available on your system. Maybe it's not in your PATH."
                  "\nPlease check the Tor project documentation to know how to do it. Or just search it online!"
                  "\nTry to configure Onymochat with Tor from the main menu (if you haven't already)"
                  "\nClosing...")
            stop()
        elif ("doesn't exist" in str(exc)) | \
                ("isn't available on your system" in str(exc)) | \
                ("not the tor executable" in str(exc)):
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
    onion_page_name = "temporary_page"
    try:
        onion_page_private_key, onion_page_name = keys_manager.save_open_keys(filename="onion_page_private_keys.txt",
                                                                              do_what="deploy",
                                                                              key_type="private key",
                                                                              name_type="onion page",
                                                                              extra_stmt=" (leave empty to create one)")
    except Exception as e:
        using_saved_keys = False
        if str(e) != "Use private key without saving.":
            print("Some error occurred. " + str(e))
        onion_page_private_key = str(input("\nEnter the private key for your onion page (leave empty to create one):"
                                           "\n"))

    if onion_page_private_key == "":
        onion_page_private_key = None

    print('\nInitiating/resuming a hidden service (V3 Onion Service). Please wait...')

    try:
        if onion_page_private_key:
            hidden_service = controller.create_ephemeral_hidden_service(
                {80: 5000},
                await_publication=True,
                key_type='ED25519-V3',
                key_content=onion_page_private_key,
                detached=True
            )
        else:
            hidden_service = controller.create_ephemeral_hidden_service(
                {80: 5000},
                await_publication=True,
                key_content='ED25519-V3',
                detached=True
            )
    except stem.ProtocolError as exc:
        if (str(exc)).find("ADD_ONION response didn't have an OK status") != -1:
            print(exc)
            print("Try closing/killing Tor first, then try again later."
                  "\n- For Windows:"
                  "\n\t- Press ctrl + alt + delete and open Task Manager. Select Tor and click on End Task."
                  "\n- For Linux: "
                  "\n\t- $sudo killall tor")
            stop()
        else:
            print("Some error occurred. Error: " + str(exc))
            stop()

    onion_domain = str(hidden_service.service_id) + '.onion'

    print("")
    print('Successfully initialized a hidden service!')
    print('\nOnion URL of Your Webpage: ' + onion_domain)

    if not onion_page_private_key:
        onion_page_private_key = str(hidden_service.private_key)
        print('\nOnion Page Private Key: ' + onion_page_private_key)
        if using_saved_keys:
            with open(dir_path + "onion_page_private_keys.txt", "a+") as file_object:
                file_object.seek(0)
                data = file_object.read(100)
                file_object.write(onion_page_private_key)
        generate_qr(onion_page_private_key, "onion_page_private_key_" + onion_page_name)
        onion_page_url = str(hidden_service.service_id) + ".onion"
        generate_qr(onion_page_url, "onion_page_url_" + onion_page_name)
    else:
        print('\nOnion Page Private Key: ' + onion_page_private_key)

    print('\nSave your private key in a safe place for future use.'
          '\nUsing the private key you can create the .onion web-page with the same URL in future.'
          '\nCAUTION: '
          'If you lose the private key, you will never be able to create the .onion web-page with the same URL again!'
          '\nCAUTION: Do not share your private key with anyone. '
          'Otherwise they too will be able to create the .onion web-page with the same URL as yours!'
          '\n')
    print("The images of the QR codes for your onion page's private key and url are saved in the location " +
          path + "files/qr_codes/")
    print("You can take a print of the images as a backup for future use. Scanning the QR with any QR code scanner "
          "reveals the content.\n")
    print('Server: PRESS CTRL+C TO CLOSE THE SERVER.'
          '\n\nNot closing the server properly might raise other problems in future.'
          '\nYou might have to press CTRL+C several times in order to close the server.\n')

    server.run()

    print('Exiting...')
    print('Webserver Closed.')
    controller.remove_ephemeral_hidden_service(hidden_service.service_id)
    print('Removed hidden service from controller.')
    if tor:
        tor.terminate()
        print('Closed Tor.')
    print('Goodbye!')
