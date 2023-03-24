import argparse, sys
import requests
import json

#Reading config file
with open('../config.json', 'r') as f:
    config = json.load(f)

#Utils
def makeUrl(host, port, endpoint, params=False):
    baseurl = "http://{}:{}/".format(host, port)
    return "{}{}?{}".format(baseurl, endpoint, params) if params else "{}{}".format(baseurl, endpoint)


def remove_queue(queue_id):
    print("|||||Removing from queue...")
    params_radarr = {
        "apikey" : config['radarr']['api_key'],
        "removeFromClient" : False,
        "blocklist" : False
    }                        
    delete_url_radarr = makeUrl(config['radarr']['host'],
                                    config['radarr']['port'],
                                    'api/v3/queue/{}'.format(queue_id))
    delete_result = requests.delete(delete_url_radarr, data=json.dumps(params_radarr))
    print(delete_result)
    print("Delete done")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()

    parser.add_argument('--m', help='method')
    parser.add_argument('--p', help='params')

    args=parser.parse_args()

    method = args.m if args.m != None else "error"
    params = args.p.split(',') if args.p != None else None

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print(dt_string)
    print("Running {} with {} params".format(method, params))
    r = False
    if params != None:
        r = getattr(sys.modules[__name__], method)(*params)
    else:
        call = getattr(sys.modules[__name__], method)
        r = call()

    print(r)
