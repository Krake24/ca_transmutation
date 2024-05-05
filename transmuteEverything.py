#!/bin/env python3
import requests
import pwinput
import json


f = open("transmute.conf.json", "r")
config = json.loads(f.read())

session_token = pwinput.pwinput(prompt='Please enter your CA session token: ', mask='*')
total_gold=0
total_items=0

def transmute(type, filter):
    total_items=0
    total_gold=0
    print()
    print(f"Searching {type} to transmute")

    body = '{"collectionTypes":"'+type+'"}'
    previous_cursor = None

    while True:
        response = requests.post(f"https://champions.io/api/inventory/{session_token}", data=body)
        response_json = response.json()
        cursor=response_json["cursor"]
        if previous_cursor and previous_cursor != cursor:
            break
        previous_cursor=cursor
        body='{"cursor":"'+cursor+'","collectionTypes":"'+type+'"}'
        for item in response_json['items']:
            if item['canBeTransmuted']:
                transmute=True
                if filter:
                    transmute=False
                    for trait in filter:
                        for attribute in item['attributes']:
                            if attribute["traitType"] == trait:
                                if attribute["value"] in filter[trait]:
                                    transmute=True
                if transmute:
                    token_id = item['tokenId']
                    gold = item['transmutationCost']
                    print(f"transmuting {token_id} for {gold} gold")
                    # continue
                    data='{"nFTType": "'+type+'", "tokenId": "'+ token_id +'"}"'
                    requests.post(f"https://champions.io/api/transmutation/transmute/{session_token}", data=data)
                    total_gold += gold
                    total_items+=1
        if not cursor:
            break    
    print(f"transmuted {total_items} {type} items for a total of {total_gold} gold")
    return total_gold, total_items

for type in config:
    gold, items = transmute(type, config[type])
    total_gold += gold
    total_items += items

print()
print("*** SUMMARY ***")
print(f"transmuted {total_items} items for a total of {total_gold} gold")
print()
input("Press Enter to continue...")