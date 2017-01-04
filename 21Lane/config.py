#!/usr/bin/python3 

import json 

CONFIG_FILE = "config.json"

class Settings:
    configDic = {
        "publicName": "Unnamed user",
        "port": 2121,
        "sharedDir": "",
        "downloadDir": "",
        "speedLimit": 2,
        "exchangeURL": ""
    }

    def update(self, publicName, port, sharedDir, downloadDir, speedLimit, exchangeURL):
        self.configDic["publicName"] = publicName 
        self.configDic["port"] = port 
        self.configDic["sharedDir"] = sharedDir
        self.configDic["downloadDir"] = downloadDir 
        self.configDic["speedLimit"] = speedLimit
        self.configDic["exchangeURL"] = exchangeURL
        self.dump()

    def dump(self):
        with open(CONFIG_FILE, 'w') as file:
            file.write(json.dumps(self.configDic))

    def load(self):
        data = {}
        try:
            with open(CONFIG_FILE) as file:
                data = json.loads(file.read())
        except Exception as e:
            pass 
        if data.keys() == self.configDic.keys():
            self.configDic = data 
            return True 
        return False 

