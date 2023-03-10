from concurrent.futures import ThreadPoolExecutor, as_completed
from time import time
import requests
from math import ceil
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import os


def slice_list(xs, parts):
    part_len = ceil(len(xs)/parts)
    return [xs[part_len*k:part_len*(k+1)] for k in range(parts)]


def sort_results(good):
    good = sorted(good, key=lambda x: int(x.split(':')[0]))
    new_good = []
    for i in good:
        month, hostname, day, country = i.split(':')
        new_good.append(f'{hostname}:{month}:{day}:{country}')
    with open('Results/all.txt', 'w', encoding='utf-8') as fp:
        fp.write("\n".join(new_good[::-1]))
    print('DONE')

    countries = {}
    for i in good:
        month, hostname, day, country = i.split(':')
        if country not in countries:
            countries[country] = []
        countries[country].append(i)

    for country, sites in countries.items():
        if country in ['UnitedStates', 'Germany', 'France', 'UnitedKingdom', 'Japan']:
            with open(f'Results/{country}.txt', 'w', encoding='utf-8') as fp:
                fp.write("\n".join(sites[::-1]))
        else:
            with open('Results/other country.txt', 'w', encoding='utf-8') as fp:
                fp.write("\n".join(sites[::-1]))


def check(hostname):
    try:
        hostname = hostname.strip()
        url = f'https://hypestat.com/info/{hostname}'
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        month = soup.find_all(text="Monthly Visits:")
        if month:
            month = month[0].parent.next_sibling.text.replace(",", "")
            month = month if month.isdigit() else 0
            day = soup.find_all(text="Daily Unique Visitors:")[0].parent.next_sibling.text
            flag = soup.find_all("dl", class_="visitors_by_country")
            if flag:
                flag = flag[0].find_all("dd")[1].text.split("  ")[0].replace(" ", "")
                flag = re.sub(r'[^a-zA-Z]+', '', flag)
            else:
                flag = ""
            text = f'{month}:{hostname}:{day}:{flag}'
            return text
    except:
        pass


def main():
    start_time = time()
    with open('sites.txt', 'r') as fp:
        sites = fp.readlines()

    n = int(input('THREADS (100-500): '))

    with ThreadPoolExecutor(max_workers=n) as executor:
        results = []
        futures = [executor.submit(check, site) for site in sites]
        for future in tqdm(as_completed(futures), total=len(sites)):
            results.append(future.result())

    good = [r for r in results if r is not None]
    sort_results(good)

    time_elapsed = time() - start_time
    time_left = (len(sites) - len(good)) * (time_elapsed / len(good)) if good else 0
    print(f'Time elapsed: {time_elapsed:.2f} s. Estimated time left: {time_left:.2f} s.')


if __name__ == '__main__':
    main()
