# Created by rec0gn1ze 7/3/2020

import requests as req
import threading
import json
import time

# To obtain VK API access token visit https://vkhost.github.io
# IMPORTANT: I am not the owner of this site and i am NOT responsible for the service

# How to use:
# python3 vkdump.py

# If API says that requests per seconds is too high, try to edit values of g_Delay

g_AccessToken = None
g_SimpleMode  = False
g_Delay       = 1.5
# Optimal for asyncronus: 1.5 - 2.5
# Optimal for syncronus: 0.2 - 0.75
# Value in seconds

FILE_NAME = 'data.txt'
STEP = 1000 # Not recomended to change this value

def log(msg: str, inputMode = False):
    if not inputMode:
        print(f"[*] - {msg}")
    else:
        return input(f"[*] {msg}")
def warn(msg: str, inputMode = False):
    if not inputMode:
        print(f"[W] - {msg}")
    else:
        return input(f"[W] {msg}")
def error(msg: str):
    print(f"[!] - {msg}")

def api(method: str, params: dict) -> int:
    try:
        if g_AccessToken == None:
            error("Access token was not assigned!")
            return

        # Join params
        _params = {"v": 5.52, "access_token": str(g_AccessToken)}
        for key, val in params.items():
            _params[key] = val

        # Generate url
        _url = f"https://api.vk.com/method/{method}"
        r = req.get(_url, _params)
        json = r.json()
        try:
            _error = json['error']
            error(f"Code: {_error['error_code']} Error: {_error['error_msg']}")
            return None
        except KeyError:
            pass
        return json
    except Exception as e:
        error(f"{e}")

def switch_bool(v : str) -> bool:
    v = v.lower()
    if v == '' or v =='y':
        return True
    else:
        return False

def parse(d: dict, key: str):
    if d == None or key == None or key == '':
        return None
    try:
        return d[key]
    except KeyError:
        return None

def verify_phone(raw: str)-> str:
    if len(raw) < 8:
        return False

    # return if no numbers
    if  "1" not in raw \
    and "2" not in raw \
    and "3" not in raw \
    and "4" not in raw \
    and "5" not in raw \
    and "6" not in raw \
    and "7" not in raw \
    and "8" not in raw \
    and "9" not in raw \
    and "0" not in raw:
        return None

    phone = ""
    for sym in raw:
        if sym in ['+', '-' , '(', ')', ' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
            if sym in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                phone += sym
        else:
            return None
    return phone

def loop_group_members(group: str):
    with open(FILE_NAME, 'a', encoding='utf-8') as f:
        count = api("groups.getById", {"group_ids": group, "fields": "members_count"})
        i = 0
        while count == None:
            count = api("groups.getById", {"group_ids": group, "fields": "members_count"})
            i += 1
            if i > 100:
                break
            else:
                time.sleep(0.2)
        if count == None:
            error(f"Error occured in group: {group}")
            return

        count = count['response'][0]['members_count']
        i = 0
        while i < count:
            time.sleep(g_Delay)
            raw = api("groups.getMembers", {"group_id": group, "offset": i, "count": STEP, "fields": "contacts,sex,country,city,id"})
            if raw == None:
                continue

            users = raw['response']['items']
            for user in users:
                is_closed  = parse(user, "is_closed")
                if is_closed:
                    continue

                user_id         = parse(user, "id")
                first_name      = parse(user, "first_name")
                last_name       = parse(user, "last_name")
                sex             = parse(user, "sex")
                if sex == 1:
                    sex = "Female"
                else:
                    sex = "Male"

                city = parse(user, 'city')
                if city != None:
                    city = city['title']
                    if city == 'None':
                        city = "Undefined"

                country = parse(user, 'country')
                if country != None:
                    country = country['title']
                    if country == 'None':
                        country = "Undefined"

                mobile_phone = parse(user, 'mobile_phone')
                if mobile_phone == None or mobile_phone == '' or mobile_phone == ' ':
                    continue

                phone = verify_phone(mobile_phone)
                if not phone:
                    continue

                log(f"Group: {group} Id: {user_id} Fist name: {first_name} Last name: {last_name} Gender: {sex} City: {city} County: {country} Phone: {phone}")
                if not g_SimpleMode:
                    f.write(f"Group: {group} URL=\"https://vk.com/id{user_id}\" Fistname=\"{first_name}\" Lastname=\"{last_name}\" Gender=\"{sex}\" City=\"{city}\" County=\"{country}\" Phone=\"{phone}\"\n")
                else:
                    f.write(str(phone) + '\n')

            time.sleep(g_Delay)
            i += STEP
    f.close()


def main():
    global g_AccessToken
    global g_SimpleMode
    global g_Delay

    g_AccessToken = log("Access token: ", inputMode=True)
    raw = log("Public VK group ids or short names, separate with ',': ", inputMode=True)
    raw.replace(' ', '')
    groups = raw.split(',')
    if "," in groups:
        error("Invalid input, try again")
        return

    g_SimpleMode = switch_bool(log("Use simple mode? (y or n): ", inputMode=True))

    use_threading = switch_bool(log("Use multiple threads? (y or n): ", inputMode=True))
    if len(groups) <= 32 and use_threading:
        threads = []
        for group in groups:
            threads.append( threading.Thread(target=loop_group_members, args=(group,)))

        for thread in threads:
            thread.start()
            time.sleep(0.75)
    else:
        for group in groups:
            loop_group_members(group)

if __name__ == "__main__":
    main()
