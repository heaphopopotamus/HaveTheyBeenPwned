#!/usr/bin/python3
"""
Usage:
  HaveTheyBeenPwned.py -h | --help
  HaveTheyBeenPwned.py (--email_list=<email_list>)
 
Options:
  --email_list=<email_list> File with one email address per line
"""
import json
import random
import requests
import concurrent.futures

from time import sleep
from docopt import docopt


def generate_list_from_file(data_file):
    data_list = []
    with open(data_file, 'r') as my_file:
        for line in my_file:
            item = line.strip('\n').strip(' ')
            data_list.append(item)
    return data_list

def check_email(email: str) -> bool:
    try:
        print("Checking email: {}".format(email))
        check = requests.get("https://haveibeenpwned.com/api/v2/breachedaccount/" + email + "?includeUnverified=true", verify = True)
        if check.status_code == 200:
            return email
        elif check.status_code == 429:
            while check.status_code == 429:
                sleep_time = random.randint(1,10)
                check = requests.get("https://haveibeenpwned.com/api/v2/breachedaccount/" + email + "?includeUnverified=true", verify = True)
                if check.status_code == 200:
                    return email
    except:
        pass

def check_emails(email_list: list) -> list:
    results_list = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=50) as pool:
        results = {pool.submit(check_email, email): email for email in email_list}
        for future in concurrent.futures.as_completed(results):
            if future.result():
                results_list.append(future.result())
    return results_list

def main():
    opts = docopt(__doc__)
    email_list = generate_list_from_file(opts['--email_list'])
    results = check_emails(email_list)
    uniq_results = set(results)
    print(json.dumps({"pwned email accounts": list(uniq_results)}, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
