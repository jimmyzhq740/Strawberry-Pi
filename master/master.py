"""Master inteface to control and view all the Pi's
"""

from __future__ import print_function

import requests
import argparse
import dweepy
import webbrowser
import shutil
import os
import random
import time
import asyncio
import aiohttp

from utils import get_name, get_thing, get_ip
from multiprocessing import current_process
from flask import Flask, render_template, jsonify, Response,stream_with_context

app = Flask(__name__)

SECRET = ""
PIS = {}

def api_root(ip):
    """return a URL
    """
    return "http://%s:5000" % ip

def get_addresses(secret):
    """
    Retrieves a list of IP addresses, pings them to check their availability
    and removes any that are unresponsive
    """

    secret = get_thing(secret)

    ips = []

    try:
        d = dweepy.get_latest_dweet_for(secret)
        ips = d[0]['content']['ips']
        print(ips)
    except Exception as e:
        print(e)

    gc = ips[:]

    rv = {}

    for ip in ips:
        url = api_root(ip) + "/ping"

        try:
            r = requests.get(url, timeout=2)
            j = r.json()

            if 'uuid' not in j:
                gc.remove(ip)

            rv[j['uuid']] = ip
        except:
            gc.remove(ip)

    dweepy.dweet_for(secret, {'ips': gc})

    return rv

def post_ip(secret):
    """to post the IP address of the master to the dweepy.io service.
    """
    secret = get_thing(secret)
    ip = get_ip()

    while True:
        try:
            print("Posting", ip)
            dweepy.dweet_for(secret, {'master_ip': ip})
            #This line posts the IP address to dweepy.io using the secret.
            # The dweepy.dweet_for function sends a “dweet” (a message) containing
            # the IP address under the key 'master_ip'.
            break
        except Exception as e:
            print(e)

        print("Reposting!")
        time.sleep(random.randint(3, 40))

#done
#Define endpoint /ip/<ip> for master server
@app.route("/ip/<ip>")
def register_ip(ip):
    """ When the clients runs is_update_loop() func, it request to the master's server
    via requests.get("http://%s:5555/ip/%s" % (master_ip, get_ip())). This will trigger
    the endpoint ip/<ip> on master server. This corresponding function will trigger each client
    server endpoint /ping which fetches the uuid of raspebrry pi. Then this register_ip func
    return creates a dictionary pair (in PIS, shown below) based on uuid and ip of that client:
    PIS = {
    "0xd83add36663d": "192.168.1.101"
    }
    """
    url = api_root(ip) + "/ping"

    try:
        r = requests.get(url, timeout=2)
        j = r.json()

        if 'uuid' not in j:
            return "Nope"

        PIS[j['uuid']] = ip
    except:
        pass

    return "OK"

#Done
@app.route("/api/refresh")
def refresh_device_list():
    global SECRET
    global PIS

    print (PIS)
    grr = PIS.copy()

    for uuid, ip in PIS.items():
        url = api_root(ip) + "/ping"

        try:
            r = requests.get(url, timeout=2)
            j = r.json()
            print (j)
        except:
            del grr[uuid]

    PIS = grr

    return device_list()

@app.route("/api/pis")
def device_list():
    return jsonify([{
        "uuid": uuid,
        "ip": ip,
        "name": get_name(uuid)
    } for uuid, ip in PIS.items()])

@app.route("/api/reboot/all")
def reboot_devices():
    errors = []

    for uuid, ip in PIS.items():
        try:
            requests.get(api_root(ip) + '/reboot')
        except Exception as e:
            print(e)
            errors.append(get_name(uuid))

    return jsonify({
        'errors': errors,
    })

@app.route("/api/<uuid>/reboot")
def reboot_device(uuid):
    ip = PIS.get(uuid, "")

    try:
        requests.get(api_root(ip) + '/reboot')
        return jsonify({
            'success': True,
        })
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': 'error',
        })

#Done
@app.route("/api/<uuid>/video_feed")
def video_device(uuid):
    ip = PIS.get(uuid, "")
    print ('hello')
    print ('http://127.0.0.1:5555'+'/api/'+uuid+'/video_feed')
    print ('http://127.0.0.1:5555'+'/api/'+uuid+'/stopcamera')
    try:
        video_url = api_root(ip)+'/video_feed'
        r = requests.get(video_url, stream=True)
        # Stream the response
        def generate():
            for chunk in r.iter_content(chunk_size=1024):
                yield chunk
        # Ensure the headers are set for streaming
        return Response(stream_with_context(generate()), content_type=r.headers['Content-Type'])
    except Exception as e:
        print(e)
        return jsonify({
            'success': False,
            'error': 'error',
        })

#Done
@app.route("/api/<uuid>/increaselens")
def increaselens(uuid):
    ip = PIS.get(uuid, "")
    if not ip:
        return jsonify({'error': 'Invalid UUID'}), 404

    try:
        increaselens_url = api_root(ip) + '/increaselens'
        r = requests.get(increaselens_url)
        return jsonify({
            'success': True,
        })
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

#Done
@app.route("/api/<uuid>/decreaselens")
def decreaselens(uuid):
    ip = PIS.get(uuid, "")
    if not ip:
        return jsonify({'error': 'Invalid UUID'}), 404

    try:
        decreaselens_url = api_root(ip) + '/decreaselens'
        r = requests.get(decreaselens_url)
        return jsonify({
            'success': True,
        })
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

#Done
@app.route("/api/<uuid>/increaseexposuretime")
def increaseExposureTime(uuid):
    ip = PIS.get(uuid, "")
    if not ip:
        return jsonify({'error': 'Invalid UUID'}), 404

    try:
        increaseexposuretime_url = api_root(ip) + '/increaseexposuretime'
        r = requests.get(increaseexposuretime_url)
        return jsonify({
            'success': True,
        })
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

#Done
@app.route("/api/<uuid>/decreaseexposuretime")
def decreaseExposureTime(uuid):
    ip = PIS.get(uuid, "")
    if not ip:
        return jsonify({'error': 'Invalid UUID'}), 404

    try:
        decreaseexposuretime_url = api_root(ip) + '/decreaseexposuretime'
        r = requests.get(decreaseexposuretime_url)
        return jsonify({
            'success': True,
        })
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

@app.route("/api/<uuid>/stopcamera")
def stopCamera(uuid):
    ip = PIS.get(uuid, "")
    if not ip:
        return jsonify({'error': 'Invalid UUID'}), 404

    try:
       stopcamera_url = api_root(ip) + '/stopcamera'
       r=requests.get(stopcamera_url)
       return jsonify({
           'success':True
       })
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'message': str(e)}), 500

async def trigger_client(uuid, ip):
    url= api_root(ip)
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{url}/start_capture") as response:
                return {uuid: await response.json()}
        except Exception as e:
            return {uuid: str(e)}

async def trigger_all_clients():
    tasks = [trigger_client(uuid, url) for uuid, url in PIS.items()]
    return await asyncio.gather(*tasks)

@app.route('/api/trigger_capture')
def trigger_capture():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    responses = loop.run_until_complete(trigger_all_clients())
    return jsonify(responses), 200

#http://127.0.0.1:5555//api/trigger_capture

def fn(uuid):
    return "%s-%s.264" % (get_name(uuid), uuid)

@app.route("/api/download")
def download_files():
    errors = []

    if os.path.exists("temp"):
        shutil.rmtree("temp")

    os.mkdir("temp")

    if not os.path.exists("captures"):
        os.mkdir("captures")

    d = 'captures'
    dirs = sorted([
        int(o)
        for o in os.listdir(d)
        if os.path.isdir(os.path.join(d,o))
    ])

    current = str(dirs[-1] + 1) if len(dirs) != 0 else str(1)

    os.mkdir(os.path.join('captures', current))

    for uuid, ip in PIS.items():
        try:
            r = requests.get(api_root(ip) + '/download', allow_redirects=True)

            with open(os.path.join('temp', fn(uuid)), 'wb') as f:
                f.write(r.content)

            shutil.copyfile(
                os.path.join('temp', fn(uuid)),
                os.path.join('captures', current, fn(uuid))
            )

        except Exception as e:
            print(e)
            errors.append(uuid)

    return jsonify({
        'save_number': current,
        'errors': errors,
    })

#Done
@app.route("/")
def index():
    return render_template("app.html")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PiShot master commander.")

    parser.add_argument(
        "--secret",
        help="A long unique string that's consistent across all Pi's",
        action="store",
        dest="secret",
        type=str,
        required=True,
    )

    parser.add_argument(
        "--list",
        help="Just list all the available Pi's instead of running the server.",
        action="store_true",
        dest="list",
    )

    parser.add_argument(
        "--silent",
        help="Does not open a new chrome window on every restart.",
        action="store_true",
        dest="silent",
    )

    args = parser.parse_args()

    if args.list:
        print("Getting all Pi's ...")

        pis = get_addresses(args.secret)
        for ip in pis.values():
            print(ip)

        print("Found %i Pi's." % len(pis))
    else:
        post_ip(args.secret)
        SECRET = args.secret

        if not args.silent:
            webbrowser.open("http://localhost:5555")

        app.run(
            host = "0.0.0.0",
            port = 5555,
            debug = args.silent,
        )