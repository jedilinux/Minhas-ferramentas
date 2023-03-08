# @Autor: Diego Rodrigues Pereira
import json
import requests
from multiprocessing.dummy import Pool as ThreadPool

class WPEnum:
    
    def __init__(self, url, item_type):
        self.url = url
        self.item_type = item_type
        if Config.get('vuln-plugin') or Config.get('vuln-theme'):
            path = f"{ROOT_PATH}/base/data/{self.item_type[:-1]}-vuln.json"
            with open(path) as f:
                self.item_list = [list(item.keys())[0] for item in json.load(f)]
        else:
            path = f"{ROOT_PATH}/base/data/list-{self.item_type}.txt"
            with open(path) as f:
                self.item_list = [line.strip() for line in f]
        self.total = len(self.item_list)

    def enumerate(self):
        if Config.get('thread'):
            threads = Config.get('thread')
        else:
            threads = 10
        item_chunks = [self.item_list[i:i+threads] for i in range(0, len(self.item_list), threads)]
        pool = ThreadPool(threads)
        urls = [f"{self.url}/wp-content/{self.item_type}/{item}" for item in self.item_list]
        responses = pool.map(requests.get, urls)
        pool.close()
        pool.join()
        found_items = []
        for i in range(len(responses)):
            resp = responses[i]
            item_name = self.item_list[i]
            if "200 OK" in resp.text or "301 Moved" in resp.text:
                found_items.append(item_name)
                print("")
                print(f"[!] Found {item_name} {self.item_type[:-1]}")
                print(f"[*]     URL: http://wordpress.org/extend/{self.item_type}/{item_name}/")
                print(f"[*]     SVN: http://{self.item_type}.svn.wordpress.org/{item_name}/")
        return found_items