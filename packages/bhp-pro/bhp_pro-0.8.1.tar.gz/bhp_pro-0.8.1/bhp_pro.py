# -*- coding: utf-8 -*-
# This file is part of BUGHUNTERS PRO
# written by @ssskingsss12
# BUGHUNTERS PRO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.






























































































































































































































































































































































import os
import sys
import subprocess
import time

REQUIRED_MODULES = [
    'multithreading', 'loguru', 'tqdm', 'bs4', 'pyfiglet', 'requests',
    'ipcalc', 'six', 'ping3', 'aiohttp', 'InquirerPy', 'termcolor',
    'tldextract', 'websocket-client', 'dnspython', 'bugscan-x',
    'inquirer', 'cryptography', 'queue', 'colorama', 'pyyaml',
]

SYSTEM_PACKAGES = [
    "rust", "binutils", "clang", "openssl", "openssl-tool", "make", "dnsutils"
]

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def install_python_module(module_name):
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            module_name, "--break-system-packages"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def install_system_package(package_name, package_manager):
    try:
        subprocess.run([package_manager, "install", "-y", package_name],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def update_system(package_manager):
    try:
        print(f"{CYAN}[+] Updating system...{RESET}")
        subprocess.run([package_manager, "update", "-y"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([package_manager, "upgrade", "-y"],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"{GREEN}[✓] System updated successfully\n{RESET}")
        return True
    except subprocess.CalledProcessError:
        print(f"{RED}[✗] Failed to update system\n{RESET}")
        return False

def simple_progress(current, total, prefix=''):
    bar_length = 40
    filled = int(bar_length * current / total)
    bar = '#' * filled + '-' * (bar_length - filled)
    percent = (current / total) * 100
    print(f"\r{prefix} [{bar}] {percent:5.1f}%", end='', flush=True)

def clear_tldextract_cache():
    """Remove the python-tldextract cache directory."""
    cache_path = os.path.expanduser('~/.cache/python-tldextract')
    try:
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
            print(f"Successfully removed: {cache_path}")
        else:
            print(f"Cache directory not found: {cache_path}")
    except Exception as e:
        print(f"Error removing cache: {e}")
clear_tldextract_cache()
clear_screen()

def install_dependencies():
    clear_screen()
    print(f"""
    =========================================
    {GREEN}AUTOMATED PACKAGE AND MODULE INSTALLATION{RESET}
    =========================================

    First-time install takes 10-15 mins on 4GB RAM
    Please keep wake lock on to speed up this process
    """)

    choice = input(
        f"{RED}First Time Running? {YELLOW}Install packages and modules? "
        f"({GREEN}yes{RESET}/{RED}no{RESET}): ").lower().strip()

    if choice not in ['yes', 'y']:
        print(f"\n{YELLOW}Skipping installation...{RESET}")
        time.sleep(1)
        clear_screen()
        print(f"{CYAN}Launching BUGHUNTERS PRO...{RESET}")
        return

    if os.name != 'nt':
        package_manager = input(f"{CYAN}Enter your package manager (apt/pkg/etc): {RESET}").strip()
        if update_system(package_manager):
            print(f"{CYAN}Installing system packages...{RESET}")
            for i, package in enumerate(SYSTEM_PACKAGES, 1):
                success = install_system_package(package, package_manager)
                simple_progress(i, len(SYSTEM_PACKAGES), "System")
                print(f" {GREEN if success else RED}{'✓' if success else '✗'} {package}{RESET}")

    print(f"\n{CYAN}Installing Python modules...{RESET}")
    for i, module in enumerate(REQUIRED_MODULES, 1):
        simple_progress(i, len(REQUIRED_MODULES), {module})
        try:
            __import__(module)
            print(f" {YELLOW}- Already installed: {module}{RESET}")
        except ImportError:
            print(f" {CYAN}Installing: {module}{RESET}", end='', flush=True)
            success = install_python_module(module)
            print(f" {GREEN if success else RED}{'✓' if success else '✗'}{RESET}")


    print(f"\n\n{GREEN}✅ Installation complete!{RESET}\n")
    time.sleep(1)
    clear_screen()
    print(f"{CYAN}Launching BUGHUNTERS PRO...{RESET}")
    time.sleep(1)
install_dependencies()


def setup_ctrlc_handler(back_function):
    """Sets up Ctrl+C handler to call the specified back function"""
    def handler(signum, frame):
        print("\nReturning to previous menu...")
        back_function()
#=============================  Imports  ========================#

import argparse
import asyncio
import base64
import json
import pathlib
import queue
import random
import re
import socket
import ssl
import threading
from datetime import datetime, timedelta
from urllib.parse import urlparse
from requests.exceptions import RequestException
from urllib3.exceptions import LocationParseError, ProxyError

# Third-party imports
import dns
import dns.resolver
import ipaddress
import multithreading
import pyfiglet
import requests
import tldextract
import urllib3
from bs4 import BeautifulSoup, BeautifulSoup as bsoup
from colorama import init, Fore
from InquirerPy import inquirer
from tqdm import tqdm
import shutil
import inquirer
import dns.resolver
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import ipaddress
import time
import requests
import signal
import atexit
import urllib3
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.reversename
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from queue import Queue
init(autoreset=True)
import dns.resolver
import dns.rdatatype
import ipaddress
import queue
import urllib.parse
import yaml
from urllib.parse import urlparse, parse_qs
from tempfile import NamedTemporaryFile
from colorama import Style 
import tempfile

# Colors
CYAN = '\033[96m'
FAIL = '\033[91m'
ENDC = '\033[0m'
UNDERLINE = '\033[4m'
WARNING = '\033[93m'
YELLOW = '\033[33m'
PURPLE = '\033[35m'
ORANGE = '\033[38;5;208m'
BRIGHT_ORANGE ='\033[38;5;202m'
MAGENTA = '\033[38;5;201m'
OLIVE = '\033[38;5;142m'
LIME = '\033[38;5;10m'
BLUE = '\033[38;5;21m'
PINK = '\033[38;5;219m'
RED = '\033[38;5;196m'
GREEN = '\033[38;5;46m'
WHITE = '\033[38;5;15m'
BLACK = '\033[38;5;0m'
GREY = '\033[38;5;8m'
BOLD = '\033[1m'
ITALIC = '\033[3m'
UNDERLINE = '\033[4m'
BLINK = '\033[5m'
INVERTED = '\033[7m'
HIDDEN = '\033[8m'
BOLD_CYAN = '\033[1;36m'
BOLD_RED = '\033[1;31m'
BOLD_GREEN = '\033[1;32m'
BOLD_YELLOW = '\033[1;33m'
BOLD_BLUE = '\033[1;34m'
BOLD_MAGENTA = '\033[1;35m'
BOLD_WHITE = '\033[1;37m'
BOLD_BLACK = '\033[1;30m'
BOLD_GREY = '\033[1;90m'
BOLD_ORANGE = '\033[1;38;5;208m'
BOLD_OLIVE = '\033[1;38;5;142m'
BOLD_LIME = '\033[1;38;5;10m'
BOLD_PINK = '\033[1;38;5;219m'
BOLD_BRIGHT_ORANGE = '\033[1;38;5;202m'
BOLD_BRIGHT_YELLOW = '\033[1;38;5;226m'
BOLD_BRIGHT_GREEN = '\033[1;38;5;46m'
BOLD_BRIGHT_BLUE = '\033[1;38;5;21m'
BOLD_BRIGHT_MAGENTA = '\033[1;38;5;201m'
BOLD_BRIGHT_CYAN = '\033[1;38;5;51m'
BOLD_BRIGHT_RED = '\033[1;38;5;196m'
BOLD_BRIGHT_WHITE = '\033[1;38;5;15m'
BOLD_BRIGHT_BLACK = '\033[1;38;5;0m'
BOLD_BRIGHT_GREY = '\033[1;38;5;8m'
BOLD_BRIGHT_ORANGE = '\033[1;38;5;208m'
BOLD_BRIGHT_OLIVE = '\033[1;38;5;142m'
BOLD_BRIGHT_LIME = '\033[1;38;5;10m'
BOLD_BRIGHT_PINK = '\033[1;38;5;219m'
BOLD_BRIGHT_PURPLE = '\033[1;38;5;201m'
BOLD_BRIGHT_ORANGE = '\033[1;38;5;202m'

# Fuck Globals
progress_counter = 0
total_tasks = 0

#=========================== Utility functions ====================================#
def generate_ascii_banner(text1, text2, font="ansi_shadow", shift=3):

    text1_art = pyfiglet.figlet_format(text1, font=font)
    text2_art = pyfiglet.figlet_format(text2, font=font)
    
    shifted_text1 = "\n".join([" " * shift + line for line in text1_art.split("\n")])
    shifted_text2 = "\n".join([" " * shift + line if i != 0 else line for i, line in enumerate(text2_art.split("\n"))])
    
    randomshit("\n" + shifted_text1 + shifted_text2)

def randomshit(text):
    color_list = [
        CYAN,
        FAIL,
        WARNING,
        YELLOW,
        PURPLE,
        ORANGE,
        BRIGHT_ORANGE,
        MAGENTA,
        OLIVE,
        LIME,
        BLUE,
        PINK,
        RED,
        GREEN,
        WHITE,
        GREY,
        BOLD_CYAN,
        BOLD_RED,
        BOLD_GREEN,
        BOLD_YELLOW,
        BOLD_BLUE,
        BOLD_MAGENTA,
        BOLD_WHITE,
        BOLD_GREY,
        BOLD_ORANGE,
        BOLD_OLIVE,
        BOLD_LIME,
        BOLD_PINK,
        BOLD_BRIGHT_ORANGE,
        BOLD_BRIGHT_YELLOW,
        BOLD_BRIGHT_GREEN,
        BOLD_BRIGHT_BLUE,
        BOLD_BRIGHT_MAGENTA,
        BOLD_BRIGHT_CYAN,
        BOLD_BRIGHT_RED,
        BOLD_BRIGHT_GREY,
        BOLD_BRIGHT_OLIVE,
        BOLD_BRIGHT_LIME,
        BOLD_BRIGHT_PINK,
        BOLD_BRIGHT_PURPLE
    ]

    chosen_color = random.choice(color_list)

    for char in text:
        sys.stdout.write(f"{chosen_color}{char}{ENDC}")
        sys.stdout.flush()

#========================== Info Gathering Menu ======================================#
def Info_gathering_menu():

    while True:
        clear_screen()
        banner()
        print(MAGENTA +"======================================="+ ENDC)
        print(MAGENTA +"          Info Gathering Menu          "+ ENDC)    
        print(MAGENTA +"======================================="+ ENDC)

        print("1.  SUBDOmain FINDER    2. urlscan.io") 
        print("3.  REVULTRA            4. DR ACCESS")
        print("5.  HOST CHECKER        6. Free Proxies")
        print("7.  TLS checker         8. BGSLEUTH")
        print("9.  CDN FINDER         10. Host Proxy Checker")
        print("11. Web Crawler        12. Dossier")
        print("13. BUCKET             14. HACKER TARGET")
        print("15. Url Redirect       16. Twisted")
        print("17. CDN FINDER2 HTTP INJECTOR")             
        print("18. HOST CHECKER V2    19. Stat")


        print("Hit enter to return to the main menu",'\n')
        choice = input("Enter your choice: ")

        if choice == '':
            randomshit("Returning to BUGHUNTERS PRO...")
            time.sleep(1)
            return

        elif choice == '1':
            clear_screen()
            subdomain_finder()

        elif choice == '2':
            clear_screen()
            url_io()

        elif choice == '3':
            clear_screen()
            rev_ultra()

        elif choice == '4':
            clear_screen()
            dr_access()

        elif choice == '5':
            clear_screen()
            host_checker()

        elif choice == '6':
            clear_screen()
            free_proxies()

        elif choice == '7':
            clear_screen()
            tls_checker()

        elif choice == '8':
            clear_screen()
            bg_sluth()

        elif choice == '9':
            clear_screen()
            cdn_finder()

        elif choice == '10':
            clear_screen()
            host_proxy_checker()

        elif choice == '11':
            clear_screen()
            web_crawler()

        elif choice == '12':
            clear_screen()
            dossier()

        elif choice == '13':
            clear_screen()
            bucket()

        elif choice == "14":
            clear_screen()
            hacker_target()

        elif choice == '15':
            clear_screen()
            url_redirect()

        elif choice == '16':
            clear_screen()
            twisted()

        elif choice == '17':
            clear_screen()
            cdn_finder2()

        elif choice == '18':
            clear_screen()
            hostchecker_v2()

        elif choice == '19':
            clear_screen()
            stat()

        else:
            print("Invalid option. Please try again.")

            time.sleep(2)
            continue
        
        randomshit("\nTask Completed Press Enter to Continue ")
        input()

#========================== Info Gathering Scripts ===================================#
#=====SUBFINDER=====#
def subdomain_finder():

    generate_ascii_banner("SUBDOmain", "FINDER")

    def scan_date(domain, formatted_date, domains, ips, progress_bar):
        url = f"https://subdomainfinder.c99.nl/scans/{formatted_date}/{domain}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                tr_elements = soup.find_all("tr", {"onclick": "markChecked(this)"})

                if tr_elements:
                    unique_domains = set()
                    unique_ips = set()
                    for tr in tr_elements:
                        td_elements = tr.find_all("td")
                        for td in td_elements:
                            link = td.find("a", class_="link")
                            if link:
                                href_link = link["href"]
                                href_link = href_link.lstrip('/').replace('geoip/', '')
                                unique_domains.add(href_link)
                            
                            ip = td.find("a", class_="ip")
                            if ip:
                                href_ip = ip.text.strip()
                                href_ip = href_ip.lstrip('geoip/')
                                unique_ips.add(href_ip)
                    
                    domains.update(unique_domains)
                    ips.update(unique_ips)

        except (ConnectionResetError, requests.exceptions.ConnectionError):
            print("ConnectionResetError occurred. Retrying in 2 seconds...")
            time.sleep(2)
            scan_date(domain, formatted_date, domains, ips, progress_bar)
        
        finally:
            time.sleep(1)
            progress_bar.update(1)

    def subdomains_finder_main():
        current_date = datetime.now()
        start_date = current_date - timedelta(days=7*2)

        domain = input("Enter the domain name: ")
        if domain == 'help' or domain == '?':
            help_menu()
            clear_screen()
            subdomain_finder()
        elif domain == '':
            print("Domain cannot be empty. Please try again.")
            time.sleep(1)
            clear_screen()
            generate_ascii_banner("SUBDOmain", "FINDER")
            subdomains_finder_main()
            return
        domains = set()
        ips = set()
        total_days = (current_date - start_date).days + 1

        print(f"Start Date: {start_date.strftime('%Y-%m-%d')}")
        print(f"End Date: {current_date.strftime('%Y-%m-%d')}")

        save_domains = input("Do you want to save domains (y/n)? ").lower()

        if save_domains == 'y':
            output_domains_filename = input("Enter the output file name for domains (e.g., domains.txt): ")
            if not output_domains_filename:
                print("Output file name cannot be empty. Please try again.")
                time.sleep(1)
                clear_screen()
                subdomains_finder_main()
                return
        else:
            print("Domains will not be saved.")

        progress_bar = tqdm(total=total_days, desc="Scanning Dates", unit="day")
        current = start_date
        threads = []

        while current <= current_date:
            formatted_date = current.strftime("%Y-%m-%d")
            thread = threading.Thread(target=scan_date, args=(domain, formatted_date, domains, ips, progress_bar))
            thread.start()
            threads.append(thread)
            current += timedelta(days=1)
            time.sleep(0.5)

        for thread in threads:
            thread.join()

        progress_bar.close()

        if save_domains == 'y' and domains:
            with open(output_domains_filename, 'w') as domains_file:
                for domain in domains:
                    if domain is not None:  # Check for None values
                        domains_file.write(domain + '\n')
            print(f"{len(domains)} Domains saved to {output_domains_filename}")

    subdomains_finder_main()

#===URL.IO===#
def url_io():
    
    generate_ascii_banner("URL", ". IO")

    def search_urlscan(domain):
        url = f"https://urlscan.io/api/v1/search/?q=domain:{domain}"
        response = requests.get(url)
        return response.json() if response.status_code == 200 else None

    def save_results(results, filename):
        unique_urls = set()
        with open(filename, 'w') as file:
            for domain_info in results['DomainInfo']:
                unique_urls.add(domain_info['url'])
            
            for apex_domain, urlscan_info in results['Urlscan'].items():
                if urlscan_info is not None and 'results' in urlscan_info:
                    for result in urlscan_info['results']:
                        task = result.get('task', {})
                        unique_urls.add(task.get('url'))
            
            for url in unique_urls:
                file.write(f"{url}\n")

    def extract_domain_info(url):
        extracted = tldextract.extract(url)
        apex_domain = f"{extracted.domain}.{extracted.suffix}"
        return {
            'domain': extracted.domain,
            'apex_domain': apex_domain,
            'url': url
        }

    def extract_urlscan_info(urlscan_result):
        extracted_info = []
        if 'results' in urlscan_result:
            for result in urlscan_result['results']:
                task = result.get('task', {})
                extracted_info.append({
                    'domain': task.get('domain'),
                    'apex_domain': task.get('apexDomain'),
                    'url': task.get('url')
                })
        return extracted_info

    def process_domains(domains):
        processed_domains = set()
        results = {'DomainInfo': [], 'Urlscan': {}}

        for user_input in domains:
            try:
                domain_info = extract_domain_info(user_input.strip())
                apex_domain = domain_info['apex_domain']
                
                if apex_domain in processed_domains:
                    print(f"Domain '{apex_domain}' already processed. Skipping.")
                    continue

                processed_domains.add(apex_domain)
                results['DomainInfo'].append(domain_info)
                urlscan_result = search_urlscan(user_input)
                results['Urlscan'][apex_domain] = urlscan_result

                # Display the required fields on the screen
                print("Domain Info:")
                print(f"Domain: {domain_info['domain']}")
                print(f"Apex Domain: {domain_info['apex_domain']}")
                print(f"URL: {domain_info['url']}\n")

            except Exception as e:
                print(f"An error occurred:")

        output_filename = input("Enter a filename to save the results (e.g., results.txt): ")
        save_results(results, output_filename)
        print("Results saved successfully!")

    def url_io_main():
        input_option = input("Enter '1' to input a domain or IP manually, '2' to read from a file: ").strip()

        if input_option == '1':
            domain_or_ip = input("Enter a domain or IP: ").strip()
            process_domains([domain_or_ip])
        elif input_option == '2':
            file_path = input("Enter the filename (e.g., domains.txt): ").strip()
            try:
                with open(file_path, 'r') as file:
                    domains = file.readlines()
                    process_domains(domains)
            except FileNotFoundError:
                print(f"File '{file_path}' not found.")
        else:
            print("Invalid option selected.")
    
    url_io_main()

#===REVULTRA===#
def rev_ultra():
    
    generate_ascii_banner("REVULTRA", "")

    def random_user_agent():
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "Sogou web spider/4.0 (+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/84.0.4316.140",
            "OpenAI-GPT3/1.0 (compatible; +https://www.openai.com)",
            "HuggingFace/Transformers/4.0 (https://huggingface.co)",
            "Cohere/1.0 (https://cohere.ai)",
            "Anthropic/1.0 (https://www.anthropic.com)",
            "Google-Bard/1.0 (https://www.google.com/bard)",
            "Azure-Cognitive-Services/1.0 (https://azure.microsoft.com/en-us/services/cognitive-services/)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "Sogou web spider/4.0 (+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/84.0.4316.140",
            "OpenAI-GPT3/1.0 (compatible; +https://www.openai.com)",
            "HuggingFace/Transformers/4.0 (https://huggingface.co)",
            "Cohere/1.0 (https://cohere.ai)",
            "Anthropic/1.0 (https://www.anthropic.com)",
            "Google-Bard/1.0 (https://www.google.com/bard)",
            "Azure-Cognitive-Services/1.0 (https://azure.microsoft.com/en-us/services/cognitive-services/)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "Sogou web spider/4.0 (+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/84.0.4316.140",
            "OpenAI-GPT3/1.0 (compatible; +https://www.openai.com)",
            "HuggingFace/Transformers/4.0 (https://huggingface.co)",
            "Cohere/1.0 (https://cohere.ai)",
            "Anthropic/1.0 (https://www.anthropic.com)",
            "Google-Bard/1.0 (https://www.google.com/bard)",
            "Azure-Cognitive-Services/1.0 (https://azure.microsoft.com/en-us/services/cognitive-services/)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "Sogou web spider/4.0 (+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/84.0.4316.140",
            "OpenAI-GPT3/1.0 (compatible; +https://www.openai.com)",
            "HuggingFace/Transformers/4.0 (https://huggingface.co)",
            "Cohere/1.0 (https://cohere.ai)",
            "Anthropic/1.0 (https://www.anthropic.com)",
            "Google-Bard/1.0 (https://www.google.com/bard)",
            "Azure-Cognitive-Services/1.0 (https://azure.microsoft.com/en-us/services/cognitive-services/)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "Sogou web spider/4.0 (+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/84.0.4316.140",
            "OpenAI-GPT3/1.0 (compatible; +https://www.openai.com)",
            "HuggingFace/Transformers/4.0 (https://huggingface.co)",
            "Cohere/1.0 (https://cohere.ai)",
            "Anthropic/1.0 (https://www.anthropic.com)",
            "Google-Bard/1.0 (https://www.google.com/bard)",
            "Azure-Cognitive-Services/1.0 (https://azure.microsoft.com/en-us/services/cognitive-services/)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "Sogou web spider/4.0 (+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/84.0.4316.140",
            "OpenAI-GPT3/1.0 (compatible; +https://www.openai.com)",
            "HuggingFace/Transformers/4.0 (https://huggingface.co)",
            "Cohere/1.0 (https://cohere.ai)",
            "Anthropic/1.0 (https://www.anthropic.com)",
            "Google-Bard/1.0 (https://www.google.com/bard)",
            "Azure-Cognitive-Services/1.0 (https://azure.microsoft.com/en-us/services/cognitive-services/)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
            "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)",
            "Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)",
            "DuckDuckBot/1.0; (+http://duckduckgo.com/duckduckbot.html)",
            "Sogou web spider/4.0 (+http://www.sogou.com/docs/help/webmasters.htm#07)",
            "ia_archiver (+http://www.alexa.com/site/help/webmasters; crawler@alexa.com)",
            "facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 OPR/84.0.4316.140",
            "OpenAI-GPT3/1.0 (compatible; +https://www.openai.com)",

        ]

        return random.choice(user_agents)

    def scrape_page(url, scraped_domains, lock, file):
        headers = {'User-Agent': random_user_agent()}
        retries = 3
        for _ in range(retries):
            try:
                response = requests.get(url, headers=headers)
                if response.status_code == 500:
                    print("Hold 1 sec, error, retrying...")
                    time.sleep(3)
                    continue
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all <tr> tags containing data
                tr_tags = soup.find_all('tr')
                
                # Extract domain names and IPs
                has_domains = False
                for tr in tr_tags:
                    tds = tr.find_all('td')
                    if len(tds) >= 2:
                        domain = tds[0].text.strip()
                        ip = tds[1].text.strip()
                        # Add domain name and IP to the set of scraped domains
                        if domain and ip:  # Check if domain and IP are not empty
                            has_domains = True
                            with lock:
                                scraped_domains.add((domain, ip))
                                file.write(f"{domain}\n{ip}\n")  # Save each domain and IP immediately
                            print(f"Grabbed domain: {domain}, IP: {ip}")  # Print the scraped domain and IP
                # If no domains found, exit early
                if not has_domains:
                    print("No domains found on this page.")
                    return False  # Return False if no domains were found
                return True  # Return True if domains were found
            except:
                print("...Retrying...")
                time.sleep(3)  # Wait before retrying

        print("Max retries exceeded. Unable to fetch data")
        return False

    def scrape_rapiddns(domain, num_pages, file):
        base_url = "https://rapiddns.io/s/{domain}?page={page}"
        base_url2 = "https://rapiddns.io/sameip/{domain}?page={page}"
        scraped_domains = set()
        lock = threading.Lock()

        def scrape_for_page(page):
            for url_type in [base_url, base_url2]:  # Iterate over both URLs
                url = url_type.format(domain=domain, page=page)
                with tqdm(total=1, desc=f"Page {page}", leave=False) as pbar:
                    if scrape_page(url, scraped_domains, lock, file):
                        pbar.set_description(f"Page {page} ({len(scraped_domains)} domains)")  # Update description with count of domains
                        pbar.update(1)
                        return True  # Exit if domains were found
                    else:
                        print(f"No more data available for {domain}.")
            return False

        with ThreadPoolExecutor(max_workers=10) as executor:
            for page in range(1, num_pages + 1):
                future = executor.submit(scrape_for_page, page)
                if not future.result():  # If no more data is found, stop further scraping
                    break

        return scraped_domains

    def rev_ultra_main():
        domain_input = input("Enter the domain, IP/CDIR, or file name.txt: ")
        num_pages = 100
        filename = input("Enter the name of the file to save domains (without extension): ")
    
        # Add '.txt' extension if not provided
        if not filename.endswith('.txt'):
            filename += '.txt'
    
        # If input is a file
        if domain_input.endswith('.txt'):
            with open(filename, 'a') as file:
                all_domains = set()
                with open(domain_input, 'r') as input_file:
                    for line in input_file:
                        current_url = line.strip()
                        if current_url:
                            print(f"Finding data for URL: {current_url}")
                            domains = scrape_rapiddns(current_url, num_pages, file)
                            if domains:
                                all_domains |= domains  # Merge domains from all URLs
                            else:
                                print(f"No more domains found for {current_url}. Moving to next URL.")
                        else:
                            print("Empty line encountered in the file, moving to next.")
    
                print(f"Total unique domains scraped: {len(all_domains)}")
        else:  # If single domain input
            with open(filename, 'a') as file:
                domains = scrape_rapiddns(domain_input, num_pages, file)
                print(f"Total unique domains scraped: {len(domains)}")
        return filename
    filename = rev_ultra_main()
    print(filename)
    time.sleep(2)
    clear_screen()
    file_proccessing()

#===DR ACCESS===#
def dr_access():
    
    generate_ascii_banner("D.R", "ACCESS")
    lock = threading.RLock()

    def get_value_from_list(data, index, default=""):
        try:
            return data[index]
        except IndexError:
            return default

    def log(value):
        with lock:
            print(value)

    def log_replace(value):
        with lock:
            sys.stdout.write(f"{value}\r")
            sys.stdout.flush()

    class BugScanner:
        def __init__(self):
            self.output = None
            self.mode = {"direct": {}, "ssl": {}, "proxy": {}}
            self.method = {"HEAD": {}, "GET": {}, "OPTIONS": {}}
            self.deep = 10
            self.ignore_redirect_location = ""
            
            self.scanned = {"direct": {}, "ssl": {}, "proxy": {}}

            self.port = 80, 443, 8080, 8443, 53, 22
            self.proxy = None
            self.threads = 8

        brainfuck_config = {

            "ProxyRotator": {
                "Port": "1080"
            },
            "Inject": {
                "Enable": True,
                "Type": 2,
                "Port": "8989",
                "Rules": {
                    "akamai.net:80": [
                        "125.235.36.177"
                    ]
                },
                "Payload": "",
                "ServerNameIndication": "",
                "MeekType": 0,
                "Timeout": 5,
                "ShowLog": False
            },
            "PsiphonCore": 12,
            "Psiphon": {
                "CoreName": "psiphon-tunnel-core",
                "Tunnel": 1,
                "Region": "SG",
                "Protocols": [
                    "FRONTED-MEEK-HTTP-OSSH",
                    "FRONTED-MEEK-OSSH"
                ],
                "TunnelWorkers": 2,
                "KuotaDataLimit": 1,
                "Authorizations": []
            }

        }

        def request(self, method, hostname, port, *args, **kwargs):
            try:
                url = ("https" if port == 443 else "http") + "://" + (hostname if port == 443 else f"{hostname}:{port}")
                log_replace(f"{method} {url}")
                return requests.request(method, url, *args, **kwargs)
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                return None

        def resolve(self, hostname):
            try:
                cname, hostname_list, host_list = socket.gethostbyname_ex(hostname)
            except (socket.gaierror, socket.herror):
                return []

            for i in range(len(hostname_list)):
                yield get_value_from_list(host_list, i, host_list[-1]), hostname_list[i]

            yield host_list[-1], cname

        def get_direct_response(self, method, hostname, port):
            if f"{hostname}:{port}" in self.scanned["direct"]:
                return None

            response = self.request(method.upper(), hostname, port, timeout=5, allow_redirects=False)
            if response is not None:
                status_code = response.status_code
                server = response.headers.get("server", "")
            else:
                status_code = ""
                server = ""

            self.scanned["direct"][f"{hostname}:{port}"] = {
                "status_code": status_code,
                "server": server,
            }
            return self.scanned["direct"][f"{hostname}:{port}"]

    class SSLScanner(BugScanner):
        def __init__(self):
            super().__init__()
            self.host_list = []

        def get_task_list(self):
            for host in self.filter_list(self.host_list):
                yield {
                    'host': host,
                }

        def log_info(self, color, status, server_name_indication):
            log(f'{color}{status:<6}  {server_name_indication}')

        def log_info_result(self, **kwargs):
            status = kwargs.get('status', '')
            server_name_indication = kwargs.get('server_name_indication', '')

            if status:
                self.log_info('', 'True', server_name_indication)
            else:
                self.log_info('', 'False', server_name_indication)

        def init(self):
            log('Stat  Host')
            log('----  ----')

        def task(self, payload):
            server_name_indication = payload['host']
            log_replace(server_name_indication)

            response = {
                'server_name_indication': server_name_indication,
                'status': False
            }

            try:
                socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.settimeout(5)
                socket_client.connect((server_name_indication, 443))
                socket_client = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(
                    socket_client, server_hostname=server_name_indication, do_handshake_on_connect=True
                )
                response['status'] = True

                self.task_success(server_name_indication)

            except Exception:
                pass

            finally:
                socket_client.close()

            self.log_info_result(**response)
            if response['status']:
                self.scanned["ssl"][f"{server_name_indication}:443"] = response
            

        def get_proxy_response(self, method, hostname, port, proxy):
            if f"{hostname}:{port}" in self.scanned["proxy"]:
                return None

            response = self.request(method.upper(), hostname, port, proxies={"http": "http://" + proxy, "https": "http://" + proxy}, timeout=5, allow_redirects=False)
            if response is None:
                return None

            if response.headers.get("location") == self.ignore_redirect_location:
                log(f"{self.proxy} -> {self.method} {response.url} ({response.status_code})")
                return None

            self.scanned["proxy"][f"{hostname}:{port}"] = {
                "proxy": self.proxy,
                "method": self.method,
                "url": response.url,
                "status_code": response.status_code,
                "headers": response.headers,
            }
            return self.scanned["proxy"][f"{hostname}:{port}"]

        def print_result(self, host, hostname, port=None, status_code=None, server=None, sni=None, color=""):
            if ((server == "AkamaiGHost" and status_code != 400) or
                    (server == "Varnish" and status_code != 500) or
                    (server == "AkamainetStorage" and status_code != 400) or
                    (server == "Cloudflare" and status_code != 400) or
                    (server == "Cloudfront" and status_code != 400)):
                 
                color = 'G2'  # Assuming G2 is some special char

            host = f"{host:<15}"
            hostname = f"  {hostname}"
            sni = f"  {sni:<4}" if sni is not None else ""
            server = f"  {server:<20}" if server is not None else ""
            status_code = f"  {status_code:<4}" if status_code is not None else ""

            log(f"{host}{status_code}{server}{sni}{hostname}")

        def print_result_proxy(self, response):
            if response is None:
                return

            data = []
            data.append(f"{response['proxy']} -> {response['method']} {response['url']} ({response['status_code']})\n")
            for key, val in response['headers'].items():
                data.append(f"|   {key}: {val}")
            data.append("|\n\n")

            log("\n".join(data))

        def is_valid_hostname(self, hostname):
            if len(hostname) > 255:
                return False
            if hostname[-1] == ".":
                hostname = hostname[:-1]
            allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
            return all(allowed.match(x) for x in hostname.split("."))

        def get_sni_response(self, hostname, deep):
            if f"{hostname}:443" in self.scanned["ssl"]:
                return None

            try:
                socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.settimeout(5)
                socket_client.connect((hostname, 443))
                context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
                with context.wrap_socket(socket_client, server_hostname=hostname) as ssock:
                    ssock.do_handshake()
                    response = {
                        "server_name_indication": hostname,
                        "status": True,
                    }
                    self.scanned["ssl"][f"{hostname}:443"] = response
                    return response
            except (socket.timeout, ssl.SSLError, socket.error):
                return {
                    "server_name_indication": hostname,
                    "status": False,
                }
            finally:
                socket_client.close()

        def scan(self):
            while True:
                hostname = self.queue_hostname.get()
                if not self.is_valid_hostname(hostname):
                    log(f"Invalid hostname: {hostname}")
                    self.queue_hostname.task_done()
                    continue

                for host, resolved_hostname in self.resolve(hostname):
                    if self.mode == "direct":
                        response = self.get_direct_response(self.method, resolved_hostname, self.port)
                        if response is None:
                            continue
                        self.print_result(host, resolved_hostname, port=self.port, status_code=response["status_code"], server=response["server"])

                    elif self.mode == "ssl":
                        response = self.get_sni_response(resolved_hostname, self.deep)
                        self.print_result(host, response["server_name_indication"], sni="True" if response["status"] else "False")
                        if response["status"]:
                            self.scanned["ssl"][f"{resolved_hostname}:443"] = response


                        if response["status"] and self.output is not None:
                            with open(self.output, 'a', encoding='utf-8') as f:
                                f.write(f"{host},{response['server_name_indication']},True\n")

                    elif self.mode == "proxy":
                        response = self.get_proxy_response(self.method, resolved_hostname, self.port, self.proxy)
                        self.print_result_proxy(response)

                self.queue_hostname.task_done()

        def start(self, hostnames):
            try:
                if self.mode == "direct":
                    self.print_result("host", "hostname", status_code="code", server="server")
                    self.print_result("----", "--------", status_code="----", server="------")
                elif self.mode == "ssl":
                    self.print_result("host", "hostname", sni="sni")
                    self.print_result("----", "--------", sni="---")

                self.queue_hostname = queue.Queue()
                for hostname in hostnames:
                    self.queue_hostname.put(hostname)

                for _ in range(min(self.threads, self.queue_hostname.qsize())):
                    thread = threading.Thread(target=self.scan)
                    thread.daemon = True
                    thread.start()

                self.queue_hostname.join()

                if self.output is not None:
                    with open(f"{self.output}", 'a', encoding='utf-8') as f:
                        for key, value in self.scanned.items():
                            f.write(f"{key}:\n")
                            for sub_key, sub_value in value.items():
                                if sub_value.get("server"):  # Check if server field is not empty
                                    f.write(f"  {sub_key}: {sub_value}\n")

                    log(f"Output saved to {self.output}")
            except KeyboardInterrupt:
                log("Keyboard interrupt received. Exiting...")

    def dr_access_main():
        bugscanner = SSLScanner()
        bugscanner.mode = input("Enter the mode (direct, ssl,) (default: direct): ") or "direct"
        bugscanner.method = input("Enter, GET, HEAD, OPTIONS (default: HEAD): ") or "HEAD"
        bugscanner.deep = int(input("Enter the target Depth (default: 5): ") or 5)
        bugscanner.ignore_redirect_location = ""
        bugscanner.port = int(input("Enter the target port (default: 80): ") or 80)
        filename = input("Enter file name or domains or ip: ")
        if not filename.endswith('.txt'):
            filename += '.txt'
        bugscanner.mode = "ssl" if bugscanner.mode == "ssl" else "direct"
        bugscanner.method = "HEAD" if bugscanner.method == "HEAD" else "GET"
        bugscanner.deep = 5 if bugscanner.deep == 5 else bugscanner.deep
        bugscanner.ignore_redirect_location = ""
        bugscanner.port = 80 if bugscanner.port == 80 else bugscanner.port

        bugscanner.proxy = None
        bugscanner.threads = int(input("Enter the Number of Threads (default: 8): ") or 8)
        bugscanner.output = input("Enter output file name (optional): ")
        if bugscanner.output and not bugscanner.output.endswith('.txt'):
            bugscanner.output += '.txt'


        with open(filename) as file:
            bugscanner.start(file.read().splitlines())

    dr_access_main()

#===HOST CHECKER===# 
def host_checker():
        
    generate_ascii_banner("HOST", "CHECKER")

    class bcolors:
        OKPURPLE = '\033[95m'
        OKCYAN = '\033[96m'
        OKPINK = '\033[94m'
        OKlime = '\033[92m'
        ORANGE = '\033[91m\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        UNDERLINE = '\033[4m'
        MAGENTA = '\033[35m'
        OKBLUE = '\033[94m'
        blue2 = '\033[96m'
        brown = '\033[33m'
        peach = '\033[95m'

    def get_ip_addresses(url):
        try:
            result = socket.getaddrinfo(url, None)
            ipv4_addresses = set()
            ipv6_addresses = set()

            for entry in result:
                ip = entry[4][0]
                if ':' in ip:
                    ipv6_addresses.add(ip)
                else:
                    ipv4_addresses.add(ip)

            return list(ipv4_addresses), list(ipv6_addresses)
        except socket.gaierror:
            return [], []

    def check_status(url, filename=None, not_found_filename=None):
        try:
            if not url.startswith('http://') and not url.startswith('https://'):
                url = 'http://' + url

            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            }

            # Send GET request for HTTP
            url_http = url
            
            r_http = requests.Session().get(url_http, headers=headers, timeout=5)
            status_http = r_http.status_code
            http_headers = r_http.headers
            server_http = r_http.headers.get('server', 'server information not found')
            connection_http = r_http.headers.get('connection', '')

            # Send GET request for HTTPS
            url_https = url_http.replace('http://', 'https://')
            r_https = requests.Session().get(url_https, headers=headers, timeout=5)
            status_https = r_https.status_code
            https_headers = r_https.headers
            server_https = r_https.headers.get('server', 'server information not found')
            connection_https = r_https.headers.get('connection', '').lower()

            # Resolve IP addresses for both HTTP and HTTPS URLs
            ipv4_addresses_http, ipv6_addresses_http = get_ip_addresses(url_http.replace('http://', ''))
            ipv4_addresses_https, ipv6_addresses_https = get_ip_addresses(url_https.replace('https://', ''))

            # Debug output for IP addresses and URLs
            print(f'{bcolors.ORANGE}{url_http}, HTTP IPs: {ipv4_addresses_http}, {ipv6_addresses_http}{bcolors.ENDC}')
            print(f'{bcolors.ORANGE}{url_https}, HTTPS IPs: {ipv4_addresses_https}, {ipv6_addresses_https}{bcolors.ENDC}')

            if status_http == 200:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [OK] 200: port 80: {bcolors.OKCYAN} Keep-Alive: active{bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [OK] 200: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 301:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Moved Permanently] 301: port 80: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Moved Permanently] 301: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 302:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Temporary redirect] 302: port 80 {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Temporary redirect] 302: port 80 {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 409:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Conflict] 409: port 80: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Conflict] 409: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 403:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Forbidden] 403: port 80: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Forbidden] 403: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 404:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Not Found] 404: port 80: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Not Found] 404: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 401:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Unauthorized Error] 401: port 80: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Unauthorized Error] 401: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 206:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Partial Content] 206: port 80: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Partial Content] 206: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 500:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Internal Server Error] 500: port 80: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Internal Server Error] 500: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_http == 400:
                if connection_http and 'keep-alive' in connection_http.lower():
                    print(f'{bcolors.OKlime} [Bad Request] 400: port 80: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Bad Request] 400: port 80: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')

            # Print status for HTTPS
            if status_https == 200:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [OK] 200: port 443: {bcolors.OKCYAN} Keep-Alive: active{bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [OK] 200: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 301:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Moved Permanently] 301: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Moved Permanently] 301: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 302:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Temporary redirect] 302: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Temporary redirect] 302: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 409:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Conflict] 409: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Conflict] 409: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 403:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Forbidden] 403: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Forbidden] 403: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 404:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Not Found] 404: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Not Found] 404: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 401:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Unauthorized Error] 401: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Unauthorized Error] 401: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 206:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Partial Content] 206: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Partial Content] 206: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 500:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Internal Server Error] 500: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Internal Server Error] 500: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')
            elif status_https == 400:
                if connection_https and 'keep-alive' in connection_https.lower():
                    print(f'{bcolors.OKlime} [Bad Request] 400: port 443: {bcolors.OKCYAN} Keep-Alive: active {bcolors.ENDC}')
                else:
                    print(f'{bcolors.OKlime} [Bad Request] 400: port 443: {bcolors.FAIL} Keep-Alive: inactive{bcolors.ENDC}')

            # Add color coding based on server information
            if 'cloudflare' in server_http.lower() or 'cloudflare' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.ORANGE} {url} {server_http if "cloudflare" in server_http.lower() else server_https}{bcolors.ENDC} {bcolors.UNDERLINE}check host {status_http} status found : {connection_http} \x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.ORANGE} {url_https} {server_https if "cloudflare" in server_https.lower() else server_http}{bcolors.ENDC} {bcolors.UNDERLINE}check host {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'cloudfront' in server_http.lower() or 'cloudfront' in server_https.lower():
                print(f'{bcolors.blue2} {url} {server_http if "cloudfront" in server_http.lower() else server_https} {bcolors.UNDERLINE}check host {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.blue2} {url_https} {server_https if "cloudfront" in server_https.lower() else server_http} {bcolors.UNDERLINE}check host {status_https} status : {connection_https} found\x1b[0m{bcolors.ENDC}')
            elif 'sffe' in server_http.lower() or 'sffe' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.ORANGE} {url} {server_http if "sffe" in server_http.lower() else server_https}{bcolors.ENDC} {bcolors.UNDERLINE}check host {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.ORANGE} {url_https} {server_https if "sffe" in server_https.lower() else server_http}{bcolors.ENDC} {bcolors.UNDERLINE}check host {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'apple' in server_http.lower() or 'apple' in server_https.lower():
                print(f'{bcolors.blue2} {url} {server_http if "apple" in server_http.lower() else server_https}{bcolors.UNDERLINE}check host {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.blue2} {url_https} {server_https if "apple" in server_https.lower() else server_http} {bcolors.UNDERLINE}check host {status_https} status : {connection_https} found\x1b[0m{bcolors.ENDC}')
            elif 'akamaighost' in server_http.lower() or 'akamaighost' in server_https.lower():
                print(f'{bcolors.OKPURPLE} {url} {server_http if "akamaighost" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKPURPLE} {url_https} {server_https if "akamaighost" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'Apple' in server_http.lower() or 'Apple' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKPINK} {url} {server_http if "Apple" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKPINK} {url_https} {server_https if "Apple" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'microsoft-IIS/10.0' in server_http.lower() or 'microsoft-IIS/10.0' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "microsoft-IIS/10.0" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "microsoft-IIS/10.0" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'fastly' in server_http.lower() or 'fastly' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.brown} {url} {server_http if "fastly" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.brown} {url_https} {server_https if "fastly" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'varnish' in server_http.lower() or 'varnish' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.peach} {url} {server_http if "varnish" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.peach} {url_https} {server_https if "varnish" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'gws' in server_http.lower() or 'gws' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.ORANGE} {url} {server_http if "gws" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.ORANGE} {url_https} {server_https if "gws" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'gse' in server_http.lower() or 'gse' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKPURPLE} {url} {server_http if "gse" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKPURPLE} {url_https} {server_https if "gse" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'esf' in server_http.lower() or 'esf' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "esf" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "esf" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'Google frontend' in server_http.lower() or 'Google frontend' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKlime} {url} {server_http if "Google frontend" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKlime} {url_https} {server_https if "Google frontend" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'ClientMapServer' in server_http.lower() or 'ClientMapServer' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKPINK} {url} {server_http if "ClientMapServer" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKPINK} {url_https} {server_https if "ClientMapServer" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'UploadServer' in server_http.lower() or 'UploadServer' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.peach} {url} {server_http if "UploadServer" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.peach} {url_https} {server_https if "UploadServer" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'OFE' in server_http.lower() or 'OFE' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.peach} {url} {server_http if "OFE" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.peach} {url_https} {server_https if "OFE" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'tengine' in server_http.lower() or 'tengine' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "tengine" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "tengine" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'TornadoServer' in server_http.lower() or 'TornadoServer' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.peach} {url} {server_http if "TornadoServer" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.peach} {url_https} {server_https if "TornadoServer" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'awselb/2.0' in server_http.lower() or 'awselb/2.0' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.peach} {url} {server_http if "awselb/2.0" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.peach} {url_https} {server_https if "awselb/2.0" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'nginx' in server_http.lower() or 'nginx' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "nginx" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "nginx" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'openresty' in server_http.lower() or 'openresty' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "openresty" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "openresty" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'Apache' in server_http.lower() or 'Apache' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "Apache" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "Apache" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'istio-envoy' in server_http.lower() or 'istio-envoy' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "istio-envoy" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "istio-envoy" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'Caddy' in server_http.lower() or 'Caddy' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "Caddy" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "Caddy" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')
            elif 'lighttpd' in server_http.lower() or 'lighttpd' in server_https.lower() and connection_https.lower() or connection_http.lower():
                print(f'{bcolors.OKCYAN} {url} {server_http if "lighttpd" in server_http.lower() else server_https} {bcolors.UNDERLINE}check {status_http} status found : {connection_http}\x1b[0m{bcolors.ENDC}')
                print(f'{bcolors.OKCYAN} {url_https} {server_https if "lighttpd" in server_https.lower() else server_http} {bcolors.UNDERLINE}check {status_https} status found : {connection_https}\x1b[0m{bcolors.ENDC}')

            if filename:
                with open(filename, 'a') as f:
                    f.write(f'{url_http} : HTTP({status_http}), Server: {server_http}, Connection: {connection_http}, IPs: IPv4: {", ".join(ipv4_addresses_http)}, IPv6: {", ".join(ipv6_addresses_http)} {http_headers}\n')
                    f.write(f'{url_https} : HTTPS({status_https}), Server: {server_https}, Connection: {connection_https}, IPs: IPv4: {", ".join(ipv4_addresses_https)}, IPv6: {", ".join(ipv6_addresses_https)} {https_headers}\n')

        except requests.ConnectionError:
            print(f'{bcolors.FAIL}{url} failed to connect{bcolors.ENDC}')

        except requests.Timeout:
            print(f'{url} timeout error')
            if not_found_filename:
                with open(not_found_filename, 'a') as f:
                    f.write(f'{url} timed out\n')
        except requests.RequestException as e:
            print(f'{url} general error: {str(e)}')

    while True:
        file_name = input("Enter the name of the file to scan: ")
        try:
            with open(file_name) as f:
                lines = f.readlines()
            break
        except FileNotFoundError:
            print("File not found. Please enter a valid file name.")

    while True:
        save_output = input("Save output to file? (y/n) ")
        if save_output.lower() == 'y':
            filename = input("Enter the name of the output file: ")
            break
        elif save_output.lower() == 'n':
            filename = None
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    while True:
        save_not_found = input("Save time out domains? (y/n) ")
        if save_not_found.lower() == 'y':
            not_found_filename = input("Enter the name of the file name: ")
            break
        elif save_not_found.lower() == 'n':
            not_found_filename = None
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

    while True:
        try:
            num_threads = int(input("Enter the number of threads (1-200): "))
            if num_threads < 1 or num_threads > 200:
                raise ValueError
            break
        except ValueError:
            print("Invalid input. Please enter a number between 1 and 200.")

    threads = []

    for line in tqdm(lines):
        url = line.strip()
        t = threading.Thread(target=check_status, args=(url, filename, not_found_filename))
        threads.append(t)
        t.start()
        if len(threads) >= num_threads:
            for t in threads:
                t.join()
            threads = []

    for t in threads:
        t.join()

    if not_found_filename:
        print(f'Time Out Domains Saved In {not_found_filename}')

    time.sleep(1)

    print("""
    ===============================
                Menu                
    ===============================
    1. Return to main menu
    2. View output file
    """)

    while True:
        choice = input("Enter your choice (1 or 2): ")
        if choice == '1':
            randomshit("Returning to BUGHUNTERS PRO...")
            break
        elif choice == '2':
            if filename and os.path.exists(filename):
                with open(filename, 'r') as f:
                    print(f.read())
                time.sleep(2)
                randomshit("Returning to BUGHUNTERS PRO...")
            else:
                print("Output file not found or not saved.")
            break

#===HOST CHECKER V2===#      
def hostchecker_v2():

    generate_ascii_banner("HOST", "CHECKER V2")

    class bcolors:
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        WARNING = '\033[93m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'

    # Function to get color based on HTTP status code
    def get_color_for_status(status):
        if isinstance(status, int):
            if status == 200:
                return bcolors.OKGREEN
            elif 400 <= status < 500:
                return bcolors.WARNING
            elif status >= 500:
                return bcolors.FAIL
            else:
                return bcolors.OKBLUE
        return bcolors.FAIL

    # Function to resolve domain names and CIDRs to IPs
    def resolve_ips(url):
        try:
            if '/' in url:  # CIDR range
                return [str(ip) for ip in ipaddress.IPv4Network(url, strict=False).hosts()]
            return [socket.gethostbyname(url)]
        except Exception as e:
            print(f"Error resolving IPs for {url}: {e}")
            return []

    # Function to extract certificate information
    def get_certificate_info(domain):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
            issuer = dict(x[0] for x in cert['issuer'])
            subject = dict(x[0] for x in cert['subject'])
            expiry = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
            days_left = (expiry - datetime.utcnow()).days
            return {
                "issuer": issuer.get("organizationName", "Unknown"),
                "subject": subject.get("commonName", "Unknown"),
                "expiry": expiry.strftime('%Y-%m-%d'),
                "days_left": days_left
            }
        except Exception as e:
            return {"error": f"Could not retrieve certificate: {e}"}

    # Function to check HTTP/HTTPS status and details
    def check_status(url, output_file=None, not_found_file=None):
        try:
            url_http = f'http://{url}'
            url_https = f'https://{url}'
            ips = resolve_ips(url)

            # Check HTTP
            try:
                response_http = requests.get(url_http, timeout=5)
                if response_http.status_code:
                    print(f"{get_color_for_status(response_http.status_code)}{url_http} : HTTP({response_http.status_code}), Server: {response_http.headers.get('Server', 'None')}, Connection: {response_http.headers.get('Connection', 'None')}, IPs: {', '.join(ips)}{bcolors.ENDC}")
                    if output_file:
                        with open(output_file, 'a') as f:
                            f.write(f"{url_http} : HTTP({response_http.status_code}), Server: {response_http.headers.get('Server', 'None')}, Connection: {response_http.headers.get('Connection', 'None')}, IPs: {', '.join(ips)}\n")
            except Exception as e:
                if not_found_file:
                    with open(not_found_file, 'a') as nf:
                        nf.write(f"{url_http} failed: {e}\n")

            # Check HTTPS and get certificate info
            try:
                response_https = requests.get(url_https, timeout=5)
                cert_info = get_certificate_info(url)
                if response_https.status_code:
                    print(f"{get_color_for_status(response_https.status_code)}{url_https} : HTTPS({response_https.status_code}), Server: {response_https.headers.get('Server', 'None')}, Connection: {response_https.headers.get('Connection', 'None')}, IPs: {', '.join(ips)}, Cert: {cert_info}{bcolors.ENDC}")
                    if output_file:
                        with open(output_file, 'a') as f:
                            f.write(f"{url_https} : HTTPS({response_https.status_code}), Server: {response_https.headers.get('Server', 'None')}, Connection: {response_https.headers.get('Connection', 'None')}, IPs: {', '.join(ips)}, Cert: {cert_info}\n")
            except Exception as e:
                if not_found_file:
                    with open(not_found_file, 'a') as nf:
                        nf.write(f"{url_https} failed: {e}\n")

            # Fall-Back to IP Connection
            if not ips:
                print(f"{bcolors.FAIL}Could not resolve IP for {url}. Skipping IP fallback.{bcolors.ENDC}")
            else:
                for ip in ips:
                    try:
                        response_fallback = requests.get(f"http://{ip}", timeout=5)
                        print(f"{bcolors.OKBLUE}IP {ip}: HTTP({response_fallback.status_code}){bcolors.ENDC}")
                    except Exception:
                        print(f"{bcolors.WARNING}check failed for IP {ip}{bcolors.ENDC}")

        except Exception as e:
            print(f"Error processing {url}: {e}")

    # Detect input type
    def detect_input_type(user_input):
        if user_input.endswith('.txt'):
            return 'File'
        elif '/' in user_input:
            try:
                ipaddress.IPv4Network(user_input, strict=False)
                return 'CIDR'
            except ValueError:
                return 'Invalid'
        elif re.match(r'^\d{1,3}(\.\d{1,3}){3}$', user_input):
            return 'IP'
        elif re.match(r'^[a-zA-Z0-9.-]+$', user_input):
            return 'URL'
        return 'Invalid'

    # Process file input
    def handle_file_input(file_name):
        try:
            with open(file_name, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"File not found: {file_name}")
            return []

    def hostchecker_main():
        user_input = input("Enter URL, CIDR, IP, or .txt file: ").strip()
        input_type = detect_input_type(user_input)

        # Prompt for file outputs for all input types
        output_file = input("Enter output file name (or leave blank to skip saving): ").strip()
        not_found_file = input("Enter timeout file name (or leave blank to skip saving): ").strip()

        if input_type == 'CIDR':
            ips = resolve_ips(user_input)
            for ip in ips:
                check_status(ip, output_file, not_found_file)
        elif input_type in ['IP', 'URL']:
            check_status(user_input, output_file, not_found_file)
        elif input_type == 'File':
            lines = handle_file_input(user_input)
            if not lines:
                print("File is empty or invalid.")
                return

            num_threads = int(input("Enter number of threads (1-200): "))

            threads = []
            for line in tqdm(lines):
                t = threading.Thread(target=check_status, args=(line, output_file, not_found_file))
                threads.append(t)
                t.start()
                if len(threads) >= num_threads:
                    for thread in threads:
                        thread.join()
                    threads = []
            for thread in threads:
                thread.join()
        else:
            print("Invalid input.")

    hostchecker_main()

#######BUCKET########
def bucket():
    generate_ascii_banner("BUCKET", "")
    import ipaddress
    import os
    import subprocess
    import threading
    import requests
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tqdm import tqdm
    from colorama import Fore, Style, init

    # Initialize colorama
    init()

    lock = threading.Lock()
    saved_domains = set()  # Using set to avoid duplicates
    cdn_keywords = ['cloudfront.net', 'cloudflare', 'imperva', 'gws']
    output_file = "domains.txt"

    def color_status_code(status_code):
        if not status_code:
            return ""
        status_code = str(status_code)
        if status_code.startswith('2'):
            return f"{Fore.GREEN}{status_code}{Style.RESET_ALL}"
        elif status_code.startswith('3'):
            return f"{Fore.YELLOW}{status_code}{Style.RESET_ALL}"
        elif status_code.startswith('4'):
            return f"{Fore.BLUE}{status_code}{Style.RESET_ALL}"
        elif status_code.startswith('5'):
            return f"{Fore.RED}{status_code}{Style.RESET_ALL}"
        else:
            return status_code

    def color_server(server):
        if not server:
            return ""
        server = server.lower()
        if 'cloudfront' in server:
            return f"{Fore.CYAN}{server}{Style.RESET_ALL}"
        elif 'cloudflare' in server:
            return f"{Fore.MAGENTA}{server}{Style.RESET_ALL}"
        elif 'apache' in server:
            return f"{Fore.YELLOW}{server}{Style.RESET_ALL}"
        elif 'nginx' in server:
            return f"{Fore.GREEN}{server}{Style.RESET_ALL}"
        elif 'microsoft' in server or 'iis' in server:
            return f"{Fore.BLUE}{server}{Style.RESET_ALL}"
        else:
            return f"{Fore.WHITE}{server}{Style.RESET_ALL}"

    def is_file(path):
        return os.path.isfile(path)

    def is_cidr(input_str):
        try:
            ipaddress.ip_network(input_str)
            return True
        except ValueError:
            return False

    def expand_cidr(cidr):
        try:
            return [str(ip) for ip in ipaddress.IPv4Network(cidr, strict=False).hosts()]
        except ValueError:
            print(f"[!] Invalid CIDR: {cidr}")
            return []

    def nslookup_host(hostname):
        try:
            result = subprocess.check_output(['nslookup', hostname], stderr=subprocess.DEVNULL).decode()
            ip_list = []
            alias_list = []

            for line in result.splitlines():
                line = line.strip()

                if line.lower().startswith("name:"):
                    cname = line.split("Name:")[-1].strip().strip('.')
                    if cname and cname not in alias_list:
                        alias_list.append(cname)

                elif line.lower().startswith("aliases:"):
                    alias = line.split("Aliases:")[-1].strip().strip('.')
                    if alias and alias not in alias_list:
                        alias_list.append(alias)

                elif "name =" in line:
                    alias = line.split("name =")[-1].strip().strip('.')
                    if alias and alias not in alias_list:
                        alias_list.append(alias)

                elif line.lower().startswith("address:") and ":" not in line:
                    ip = line.split("Address:")[-1].strip()
                    if ip and ip not in ip_list:
                        ip_list.append(ip)

            return ip_list, alias_list
        except Exception as e:
            return [], []

    def check_http_status(url):
        try:
            # Try with keep-alive first
            with requests.Session() as session:
                session.headers.update({'Connection': 'keep-alive'})
                response = session.get(url, timeout=5, allow_redirects=True)
                server = response.headers.get('Server', '')
                return response.status_code, True, server
        except requests.exceptions.SSLError:
            try:
                # Try without SSL verification
                with requests.Session() as session:
                    session.headers.update({'Connection': 'keep-alive'})
                    response = session.get(url, timeout=5, verify=False, allow_redirects=True)
                    server = response.headers.get('Server', '')
                    return response.status_code, True, server
            except:
                try:
                    # Fallback to single request
                    response = requests.get(url, timeout=5, allow_redirects=True)
                    server = response.headers.get('Server', '')
                    return response.status_code, False, server
                except:
                    return None, False, ''
        except:
            try:
                # Fallback to single request
                response = requests.get(url, timeout=5, allow_redirects=True)
                server = response.headers.get('Server', '')
                return response.status_code, False, server
            except:
                return None, False, ''

    def save_to_file(filename, data):
        with lock:
            # Remove ALL color codes using regex
            import re
            clean_data = re.sub(r'\x1b\[[0-9;]*m', '', data)
            
            if clean_data not in saved_domains:
                saved_domains.add(clean_data)
                with open(filename, 'a', encoding='utf-8') as f:
                    f.write(clean_data + '\n')
                
                # Print colored version to console
                print(data)

    def process_target(target):
        # Add http:// if not present
        if not target.startswith(('http://', 'https://')):
            target = f"http://{target}"
        
        # Get status code, keep-alive status, and server header
        status_code, keepalive, server = check_http_status(target)
        
        ip_list, aliases = nslookup_host(target.replace('http://', '').replace('https://', '').split('/')[0])
        
        # Prepare display components
        status_display = ""
        if status_code:
            colored_status = color_status_code(status_code)
            # More visible keep-alive indicator
            keepalive_status = f"{Fore.CYAN}[keep-alive]{Style.RESET_ALL}" if keepalive else f"{Fore.MAGENTA}[no-keep-alive]{Style.RESET_ALL}"
            server_display = f" [Server: {color_server(server)}]" if server else ""
            status_display = f" {keepalive_status} [Status: {colored_status}]{server_display}"
        
        for alias in aliases:
            for cdn in cdn_keywords:
                if cdn in alias.lower():
                    save_to_file(output_file, f"{target} -> {alias}{status_display}")
                    return
        
        # If no CDN found but we have a status code, save it with status only
        if status_code:
            save_to_file(output_file, f"{target} -> {target}{status_display}")
            
    def bucket_main():
        user_input = input("Enter a domain, IP, CIDR, or path to a file: ").strip()
        targets = []

        if is_file(user_input):
            with open(user_input, 'r', encoding='utf-8') as f:
                targets = [line.strip() for line in f if line.strip()]
        elif is_cidr(user_input):
            targets = expand_cidr(user_input)
        else:
            targets = [user_input]

        print(f"[*] Checking {len(targets)} targets using 15 threads...\n")

        with ThreadPoolExecutor(max_workers=75) as executor:
            futures = [executor.submit(process_target, target) for target in targets]
            for _ in tqdm(as_completed(futures), total=len(futures), desc="Processing"):
                pass

        if saved_domains:
            print(f"\n[✓] Done. Results saved to: {output_file}")
        else:
            print(f"\n[{Fore.RED}×{Style.RESET_ALL}] No results were found or saved.")

        # Clear output file at start
        open(output_file, 'w').close()
    bucket_main()

#===FREE PROXIES===#         
def free_proxies():

    generate_ascii_banner("FREE", "PROXY")

    def get_proxies_from_source(source_url):
        try:
            response = requests.get(source_url, timeout=3)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print("Error fetching proxy:")
            return None

    def extract_proxies(data):
        # Use regular expression to extract proxies from the response
        proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', data)
        return proxies

    def scrape_proxies(sources):
        all_proxies = []

        for source in tqdm(sources, desc="Scraping Proxies", unit="source"):
            source_data = get_proxies_from_source(source)

            if source_data:
                proxies = extract_proxies(source_data)
                all_proxies.extend(proxies)

        return all_proxies

    def check_proxy(proxy):
        try:
            response = requests.get("https://www.twitter.com", proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=5)
            response.raise_for_status()
            return proxy
        except requests.exceptions.RequestException:
            return None

    def check_proxies(proxies):
        working_proxies = []

        with ThreadPoolExecutor(max_workers=80) as executor:
            results = list(tqdm(
                executor.map(check_proxy, proxies),
                total=len(proxies),
                desc="Checking Proxies",
                unit="proxy"
            ))

        working_proxies = [proxy for proxy in results if proxy is not None]

        return working_proxies

    def ask_to_check_proxies(proxies):

        user_input = input(f"Do you want to check the proxies for validity? (yes/no): ").strip().lower()
        if user_input in ['yes', 'y']:
            return check_proxies(proxies)
        elif user_input in ['no', 'n']:
            return proxies
        else:
            print("Invalid input. Assuming 'no'.")
            return proxies

    def save_to_file(proxies, filename):
        with open(filename, 'w') as file:
            for proxy in proxies:
                file.write(f"{proxy}\n")

    def load_proxies_from_file(filename):
        try:
            with open(filename, 'r') as file:
                return [line.strip() for line in file if line.strip()]
        except FileNotFoundError:
            print(f"File {filename} not found")
            return []

    def free_proxies_main():
        http_sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http",
            "https://openproxylist.xyz/http.txt",
            "https://proxyspace.pro/http.txt",
            "https://proxyspace.pro/https.txt",
            "http://free-proxy-list.net",
            "http://us-proxy.org",
            "https://www.proxy-list.download/api/v1/?type=http",
            "https://www.proxy-list.download/api/v1/?type=https",
            "https://proxylist.geonode.com/api/proxy-list?limit=500&page=1&sort_by=lastChecked&sort_type=desc"
            # Add other HTTP sources from your configuration here
            # ...
        ]

        socks4_sources = [
            "https://www.vpnside.com/proxy/list/"
            #"https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4",
            "https://www.proxy-list.download/api/v1/get?type=socks4&anon=elite"
            "https://openproxylist.xyz/socks4.txt",
            "https://proxyspace.pro/socks4.txt",
            "https://www.proxy-list.download/api/v1/get/?type=socks4"
            
            # Add other SOCKS4 sources from your configuration here
            # ...
        ]

        socks5_sources = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5",
            "https://www.proxy-list.download/api/v1/?type=socks5",
            "https://www.proxy-list.download/api/v1/get?type=socks5&anon=elite"
            "https://openproxylist.xyz/socks5.txt",
            "https://proxyspace.pro/socks5.txt",
            # Add other SOCKS5 sources from your configuration here
            # ...
        ]

        while True:
            print("\nChoose an option:")
            print("1. Scrape HTTP Proxies")
            print("2. Scrape SOCKS4 Proxies") 
            print("3. Scrape SOCKS5 Proxies")
            print("4. Check Existing Proxies")
            print("5. Exit")

            try:
                user_choice = int(input("Enter your choice (1-5): "))
            except ValueError:
                print("Invalid input. Please enter a number.")
                continue

            if user_choice in [1, 2, 3]:
                sources = {
                    1: (http_sources, 'http.txt', 'HTTP'),
                    2: (socks4_sources, 'socks4.txt', 'SOCKS4'),
                    3: (socks5_sources, 'socks5.txt', 'SOCKS5')
                }
                source_list, filename, proxy_type = sources[user_choice]
                proxies = scrape_proxies(source_list)
                save_to_file(proxies, filename)
                print(f"{proxy_type} Proxies saved to {filename}. Total proxies: {len(proxies)}")
                working_proxies = ask_to_check_proxies(proxies)
                save_to_file(working_proxies, f'working_{filename}')
                print(f"Working {proxy_type} Proxies saved to working_{filename}. Total working: {len(working_proxies)}")
                time.sleep(2)
                clear_screen()

            elif user_choice == 4:
                filename = input("Enter the filename to check proxies from: ")
                proxies = load_proxies_from_file(filename)
                working_proxies = ask_to_check_proxies(proxies)
                save_to_file(working_proxies, f'working_{filename}')
                print(f"Working Proxies saved to working_{filename}. Total working: {len(working_proxies)}")
                time.sleep(2)
                clear_screen()
            
            elif user_choice == 5:
                clear_screen()
                break
            else:
                print("Invalid choice. Please enter a number between 1-5.")

    free_proxies_main()

#===TLS CHECKER===#
def tls_checker():
        
    import socket
    import ssl
    from concurrent.futures import ThreadPoolExecutor
    from tqdm import tqdm

    # Color codes
    PINK = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'



    def clear_screen():
        print("\033[H\033[J")  # ANSI escape codes to clear screen

    def generate_ascii_banner():
        """Generate a clean ASCII banner"""
        clear_screen()
        print(f"{PINK}{BOLD}")
        print("┌──────────────────────────────┐")
        print("│         TLS CHECKER          │")
        print("└──────────────────────────────┘")
        print(f"{ENDC}")

    def print_success(message):
        print(f"{GREEN}✓{ENDC} {message}")

    def print_warning(message):
        print(f"{WARNING}⚠{ENDC} {message}")

    def print_error(message):
        print(f"{FAIL}✗{ENDC} {message}")

    def print_info(message):
        print(f"{CYAN}ℹ{ENDC} {message}")

    IGNORED_SSL_ERRORS = {'WRONG_VERSION_NUMBER'}

    def save_to_file(result, file_name):
        try:
            with open(file_name, 'a') as file:
                file.write(result + "\n")
            print_success(f"Results saved to {file_name}")
        except Exception as e:
            print_error(f"Failed to save results: {e}")

    def check_tls_details(host, port, file_name, pbar):
        global progress_counter
        ip_address = None
        
        try:
            ip_address = socket.gethostbyname(host)
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            with socket.create_connection((host, port), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    result = (f"\n{BOLD}Results for {host}:{port}{ENDC}\n"
                            f"IP Address: {ip_address}\n"
                            f"TLS Version: {ssock.version()}\n"
                            f"Cipher Suite: {ssock.cipher()[0]}\n")
                    print(result)
                    if file_name:
                        save_to_file(result, file_name)
        except ssl.SSLError as e:
            error_code = getattr(e, 'reason', None)
            if error_code in IGNORED_SSL_ERRORS:
                print_warning(f"Ignored SSL error for {host}:{port} - {e}")
            else:
                print_error(f"SSL error for {host}:{port} - {e}")
        except socket.timeout:
            print_error(f"Timeout connecting to {host}:{port}")
        except Exception as e:
            print_error(f"Error checking {host}:{port} - {e}")
        finally:
            progress_counter += 1
            pbar.update(1)

    def check_tls_for_domains(domains, ports=(443, 80)):
        global total_tasks
        
        print_info("\nSave results to file (leave blank to skip saving)")
        file_name = input("Filename (e.g., results.txt): ").strip()
        
        total_tasks = len(domains) * len(ports)
        max_workers = min(10, total_tasks) or 1
        
        print(f"\n{BOLD}Starting scan for {len(domains)} domain(s)...{ENDC}")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor, \
            tqdm(total=total_tasks, desc="Scan Progress", unit="check") as pbar:
            
            futures = []
            for domain in domains:
                for port in ports:
                    futures.append(executor.submit(check_tls_details, domain, port, file_name, pbar))
            
            for future in futures:
                future.result()  # Wait for completion and handle any exceptions

    def tls_checker_main():
        generate_ascii_banner()
        while True:
            print(f"\n{BOLD}Main Menu:{ENDC}")
            print(f"{GREEN}1{ENDC} - Check single domain")
            print(f"{GREEN}2{ENDC} - Check domains from file")
            print(f"{GREEN}3{ENDC} - Exit")
            
            choice = input("\nSelect an option (1-3): ").strip()
            
            if choice == '1':
                domain = input("\nEnter domain or IP: ").strip()
                if domain:
                    check_tls_for_domains([domain])
                else:
                    print_error("Domain cannot be empty")
            elif choice == '2':
                file_name = input("\nEnter filename with domains: ").strip()
                try:
                    with open(file_name, "r") as file:
                        domains = [line.strip() for line in file if line.strip()]
                    
                    if domains:
                        check_tls_for_domains(domains)
                    else:
                        print_error("File is empty")
                except FileNotFoundError:
                    print_error("File not found")
            elif choice == '3':
                print_success("\nGoodbye!")
                break
            else:
                print_error("Invalid choice")

    tls_checker_main()

#===BUGSLUTH===#
def bg_sluth():
    
    banner_lines = [ 

    ORANGE + "██████╗  ██████╗ ███████╗██╗     ███████╗██╗   ██╗████████╗██╗  ██╗" + ENDC,
    ORANGE + "██╔══██╗██╔════╝ ██╔════╝██║     ██╔════╝██║   ██║╚══██╔══╝██║  ██║" + ENDC,
    ORANGE + "██████╔╝██║  ███╗███████╗██║     █████╗  ██║   ██║   ██║   ███████║" + ENDC,
    ORANGE + "██╔══██╗██║   ██║╚════██║██║     ██╔══╝  ██║   ██║   ██║   ██╔══██║" + ENDC,
    ORANGE + "██████╔╝╚██████╔╝███████║███████╗███████╗╚██████╔╝   ██║   ██║  ██║" + ENDC,
    ORANGE + "╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚══════╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝" + ENDC,
    LIME +  "Inspired by @wicky12317018" + ENDC,
    FAIL + "Re- written by @ssskingssss" + ENDC,

    FAIL + "Please use 1.(ONE) Option At A time" + ENDC,
    FAIL + "DO NOT ENTER FILE NAME THEN CDIR, USE OTION 0 FOR HELP," + ENDC,
        ]

    for line in banner_lines:
        print(line)


    class BugScanner(multithreading.MultiThreadRequest):
        threads: int

        def request_connection_error(self, *args, **kwargs):
            return 1

        def request_read_timeout(self, *args, **kwargs):
            return 1

        def request_timeout(self, *args, **kwargs):
            return 1

        def convert_host_port(self, host, port):
            return host + (f':{port}' if bool(port not in ['80', '443']) else '')

        def get_url(self, host, port, uri=None):
            port = str(port)
            protocol = 'https' if port == '443' else 'http'
            return f'{protocol}://{self.convert_host_port(host, port)}' + (f'/{uri}' if uri is not None else '')

        def init(self):
            self._threads = self.threads or self._threads

        def complete(self):
            pass

    class DirectScanner(BugScanner):
        method_list = []
        host_list = []
        port_list = []
        isp_redirects = [
            "isp.tstt.co.tt",
            "tstt.co.tt",
            "www.tstt.net.tt",
            # Africa
            "www.mtn.com",
            "www.vodacom.co.za",
            "www.orange.com", 
            "www.airtel.africa",
            "www.glo.com",
            "safaricom.co.ke",
            "www.telkom.co.za",
            # Asia
            "www.singtel.com",
            "www.airtel.in",
            "www.jio.com",
            "www.docomo.ne.jp",
            "www.kddi.com",
            "www.chinamobile.com",
            "www.telkomsel.com",
            "www.globe.com.ph",
            # Europe 
            "www.vodafone.com",
            "www.telekom.de",
            "www.orange.fr",
            "www.t-mobile.com",
            "www.telefonica.com",
            # North America
            "www.verizon.com", 
            "www.att.com",
            "www.tmobile.com",
            "www.sprint.com",
            "www.rogers.com",
            "www.telus.com",
            # South America
            "www.claro.com.br",
            "www.vivo.com.br",
            "www.movistar.com.ar",
            "www.personal.com.ar",
            # Oceania
            "www.telstra.com.au",
            "www.optus.com.au",
            "www.vodafone.com.au",
            "www.spark.co.nz"
        ]


        def log_info(self, **kwargs):
            for x in ['status_code', 'server']:
                kwargs[x] = kwargs.get(x, '')

            location = kwargs.get('location')
            if location:
                if location.startswith(f"https://{kwargs['host']}"):
                    kwargs['status_code'] = f"{kwargs['status_code']:<4}"
                else:
                    kwargs['host'] += f" -> {location}"

            messages = []
            for x in ['\033[36m{method:<6}\033[0m', '\033[35m{status_code:<4}\033[0m', '{server:<22}', '\033[94m{port:<4}\033[0m', '\033[92m{host}\033[0m']:
                messages.append(f'{x}')

            super().log('  '.join(messages).format(**kwargs))

        def get_task_list(self):
            for method in self.filter_list(self.method_list):
                for host in self.filter_list(self.host_list):
                    for port in self.filter_list(self.port_list):
                        yield {
                            'method': method.upper(),
                            'host': host,
                            'port': port,
                        }

        def init(self):
            super().init()
            self.log_info(method='Method', status_code='Code', server='Server', port='Port', host='Host')
            self.log_info(method='------', status_code='----', server='------', port='----', host='----')

        def task(self, payload):
            method = payload['method']
            host = payload['host']
            port = payload['port']

            try:
                response = self.request(method, self.get_url(host, port), retry=1, timeout=3, allow_redirects=False)
            except:
                return

            if response is not None:
                status_code = response.status_code
                server = response.headers.get('server', '')
                location = response.headers.get('location', '')

                if status_code == 302 and location in self.isp_redirects:
                    return

                if status_code and status_code != 302:
                    data = {
                        'method': method,
                        'host': host,
                        'port': port,
                        'status_code': status_code,
                        'server': server,
                        'location': location,
                    }
                    self.task_success(data)
                    self.log_info(**data)

    class PingScanner(BugScanner):

        def init(self):
            self.host_list = []
            self.method_list = []
            # Allow custom ports or use defaults
            self.port_list = []
            self.threads = 10

        async def scan(self):
            self.init_log()
            tasks = []
            for host in self.host_list:
                # Create task for each host+port combination
                for port in self.port_list:
                    tasks.append(self.scan_host_port(host, port))
            await asyncio.gather(*tasks)

        async def scan_host_port(self, host, port):
            try:
                if await self.ping(host):
                    # Try to connect to specific port
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((host, int(port)))
                    sock.close()
                    
                    if result == 0:
                        status = '\033[36mOpen\033[0m'
                        # Get server info for open ports
                        server = await self.get_server_info(host, port)
                    else:
                        status = '\033[31mClosed\033[0m'
                        server = ''
                        
                    self.log_info(status=status, host=host, port=port, server=server)
                    self.task_success({'host': host, 'port': port, 'status': status, 'server': server})
                    
            except Exception as e:
                print(f"Error scanning {host}:{port} - {str(e)}")

        async def ping(self, host):
            process = await asyncio.create_subprocess_shell(
                f'ping -n 1 {host}',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0

        async def get_server_info(self, host, port):
            try:
                if port == 443:
                    # For HTTPS
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    
                    reader, writer = await asyncio.open_connection(
                        host, port, ssl=context)
                else:
                    # For HTTP and other ports
                    reader, writer = await asyncio.open_connection(
                        host, port)
                    
                writer.write(b'GET / HTTP/1.1\r\nHost: '+host.encode()+b'\r\n\r\n')
                await writer.drain()
                
                data = await reader.read(1024)
                writer.close()
                await writer.wait_closed()
                
                # Try to extract server header
                response = data.decode()
                server = ''
                for line in response.split('\n'):
                    if line.startswith('Server:'):
                        server = line.split(':', 1)[1].strip()
                        break
                return server
            except:
                return ''

        def log_info(self, **kwargs):
            status = kwargs.get('status', '')
            host = kwargs.get('host', '')
            port = kwargs.get('port', '')
            server = kwargs.get('server', '')
            message = f"{status:<4}  {host:<15} {port:<6}  {server}"
            self.logger.log(message)

        def init_log(self):
            self.log_info(status='Stat', host='Host', port='Port', server='Server')
            self.log_info(status='----', host='----', port='----', server='----')

        def start(self):
            asyncio.run(self.scan())

    class ProxyScanner(DirectScanner):
        proxy = []

        def log_replace(self, *args):
            super().log_replace(':'.join(self.proxy), *args)

        def request(self, *args, **kwargs):
            proxy = self.get_url(self.proxy[0], self.proxy[1])
            return super().request(*args, proxies={'http': proxy, 'https': proxy}, **kwargs)

    class SSLScanner(BugScanner):
        host_list = []

        def get_task_list(self):
            for host in self.filter_list(self.host_list):
                yield {
                    'host': host,
                }

        def log_info(self, color='', status='', server='', port='', host=''):
            super().log(f'{color}{status:<6}  {server:<22}  {port:<4}  {host}')
        def log_info_result(self, **kwargs):
            G1 = self.logger.special_chars['G1']
            status = kwargs.get('status', '')
            server_name_indication = kwargs.get('server_name_indication', '')
            if status:
                color = G1
                self.log_info(color, 'True', server_name_indication,)
                self.task_success(server_name_indication)
            else:
                self.log_info(FAIL, 'False', server_name_indication)

        def init(self):
            super().init()
            self.log_info('', 'Stat', 'Host', 'Port', 'Server Name Indication',)
            self.log_info('', '----', '----', '----', '---------------------',)

        def task(self, payload):
            server_name_indication = payload['host']
            self.log_replace(server_name_indication)
            response = {
                'server_name_indication': server_name_indication,
                'status': False
            }

            try:
                socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                socket_client.settimeout(5)
                socket_client.connect((server_name_indication, 443))
                socket_client = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2).wrap_socket(
                    socket_client, server_hostname=server_name_indication, do_handshake_on_connect=True
                )
                response['status'] = True
                self.task_success(server_name_indication)

            except Exception:
                pass

            if response['status']:
                self.log_info_result(**response)

    def generate_ips_from_cidr(cidr):
        ip_list = []
        try:
            network = ipaddress.ip_network(cidr)
            for ip in network.hosts():
                ip_list.append(ip)
        except ValueError as e:
            print("Error:", e)
        return ip_list

    def bug_sluth_main():
        mode = input("Enter mode (direct, proxy, ssl, ping): ").strip()
        choice = input("(1)File name (2)Cdir: ")
        if choice == "1":
            filename = input("Enter filename: ").strip()
        elif choice == "2":
            cdir = input("Enter CIDR (e.g., 192.168.1.0/24): ").strip()

        method_list = input("Enter method (default: head): ").strip() or 'head'
        port_list = input("Enter port (default: 80): ").strip() or '80'
        choice2 = input("Do you want to use proxy?: y/n: ").lower()
        if choice2 == "y":
            proxy_input = input("Enter proxy (host:port): ").strip()
        else:
            proxy_input = ""  # Set empty string as default when no proxy needed
        output = input("Enter output file name: ").strip()
        threads = input("Enter number of threads: ").strip()
        threads = int(threads) if threads else None

        if not filename and not cdir:
            print("Either filename or CIDR must be provided.")
            sys.exit()

        method_list = method_list.split(',')
        if filename:
            host_list = open(filename).read().splitlines()
        elif cdir:
            ip_list = generate_ips_from_cidr(cdir)
            host_list = [str(ip) for ip in ip_list]

        port_list = port_list.split(',')
        proxy = proxy_input.split(':')

        if mode == 'direct':
            scanner = DirectScanner()
        elif mode == 'ssl':
            scanner = SSLScanner()
        elif mode == 'ping':
            scanner = PingScanner()
        elif mode == 'proxy':
            if not proxy or len(proxy) != 2:
                sys.exit('--proxy host:port')
            scanner = ProxyScanner()
            scanner.proxy = proxy
        else:
            sys.exit('Not Available!')

        scanner.method_list = method_list
        scanner.host_list = host_list
        scanner.port_list = port_list
        scanner.threads = threads
        scanner.start()

        if output:
            with open(output, 'w+') as file:
                file.write('\n'.join([str(x) for x in scanner.success_list()]) + '\n')

    bug_sluth_main()

#===CDN FINDER===#
def cdn_finder():
    
    generate_ascii_banner("CDN", "SCANNER")

    def findcdnfromhost(host):
        cloudflare_headers = ["cloudflare", "cloudfront", "cloudflare-nginx", "Google Frontend", "Google Cloud", "GW_Elastic_LB", "Fastly", "AkamaiGHost", "AkamainetStorage", "Akamai", "Akamai Technologies", "Akamai-Cdn", "Akamai-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai", "ningx", "cdnetworks", "edgecast", "incapsula", "maxcdn", "sucuri", "micosoft-azure", "amazonaws", "cloudfront", "cloudflare", "fastly", "maxcdn", "akamai", "edgecast", "sucuri", "incapsula", "amazonaws", "microsoft", "azure", "google", "cloud", "googlecloud", "googlecloudplatform", "gstatic", "gstatic.com", "gstatic.net", "gstatic.com.net", "gstatic.net.com", "gstatic.net.com.net", "gstatic.com.net", "gstatic.com.net.com", "gstatic.net.com.net", "gstatic.net.com.net.com", "gstatic.com.net.com.net", "gstatic.com.net.com.net.com", "gstatic.net.com.net.com.net", "gstatic.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net"]
        for header in cloudflare_headers:
            if header.lower() in host.lower():
                return "cloudflare", "cloudfront", "cloudflare-nginx", "Google Frontend", "Google Cloud", "GW_Elastic_LB", "Fastly", "AkamaiGHost", "AkamainetStorage", "Akamai", "Akamai Technologies", "Akamai-Cdn", "Akamai-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage", "Akamai-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn-Netstorage-Cdn", "Akamai", "ningx", "cdnetworks", "edgecast", "incapsula", "maxcdn", "sucuri", "micosoft-azure", "amazonaws", "cloudfront", "cloudflare", "fastly", "maxcdn", "akamai", "edgecast", "sucuri", "incapsula", "amazonaws", "microsoft", "azure", "google", "cloud", "googlecloud", "googlecloudplatform", "gstatic", "gstatic.com", "gstatic.net", "gstatic.com.net", "gstatic.net.com", "gstatic.net.com.net", "gstatic.com.net", "gstatic.com.net.com", "gstatic.net.com.net", "gstatic.net.com.net.com", "gstatic.com.net.com.net", "gstatic.com.net.com.net.com", "gstatic.net.com.net.com.net", "gstatic.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com", "gstatic.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net.com.net", "gstatic.net.com.net.com.net"
            
            
        return host

    def fetch_tls_ssl_certificate(host):
        ip_address = resolve_host_ip(host)
        if ip_address:
            try:
                with socket.create_connection((ip_address, 443)) as sock:
                    context = ssl.create_default_context()
                    with context.wrap_socket(sock, server_hostname=host) as ssock:
                        return ssock.getpeercert()
            except (socket.error, ssl.SSLError) as e:
                print(f"Error fetching TLS/SSL certificate for {host}:")
                return None
        return None

    def resolve_host_ip(host):
        try:
            ip_address = socket.gethostbyname(host)
            return ip_address
        except socket.gaierror as e:
            print(f"Error resolving IP address for {host}:")
            return None

    def get_http_headers(url):
        try:
            response = requests.head(url, timeout=5)
            return response.headers
        except Exception as e:
            print(f"HTTP request failed for {url}:")
            return None

    def get_dns_records(host):
        try:
            answers_a = dns.resolver.resolve(host, 'A')
            a_records = [str(answer) for answer in answers_a]
        except Exception as e:
            print(f"Failed to fetch A records for {host}:")
            a_records = []

        try:
            nslookup_result = get_aaaa_records(host)
            aaaa_records = nslookup_result if nslookup_result else []
        except Exception as e:
            print(f"Failed to fetch AAAA records for {host}:")
            aaaa_records = []

        try:
            answers_ptr = dns.resolver.resolve(host, 'PTR')
            ptr_records = [str(answer) for answer in answers_ptr]
        except Exception as e:
            print(f"Failed to fetch PTR records for {host}:")
            ptr_records = []

        try:
            answers_txt = dns.resolver.resolve(host, 'TXT')
            txt_records = [str(txt_answer) for txt_answer in answers_txt]
        except Exception as e:
            print(f"Failed to fetch TXT records for {host}:")
            txt_records = []

        try:
            answers_mx = dns.resolver.resolve(host, 'MX')
            mx_records = [f"{answer.preference} {answer.exchange}" for answer in answers_mx]
        except Exception as e:
            print(f"Failed to fetch MX records for {host}:")
            mx_records = []

        try:
            soa_records = [str(answer) for answer in dns.resolver.resolve(host, 'SOA')]
        except Exception as e:
            print(f"Failed to fetch SOA records for {host}:")
            soa_records = []

        return a_records, aaaa_records, ptr_records, txt_records, mx_records, soa_records

    def get_aaaa_records(host):
        result = subprocess.run(["nslookup", "-query=AAAA", host], capture_output=True, text=True)
        return result.stdout.splitlines()

    def save_to_file(filename, content):
        with open(filename, 'a') as file:
            file.write(content)

    def process_url(url, output_file):
        try:
            if not urlparse(url).scheme:
                url = "http://" + url

            hostname = urlparse(url).hostname
            a_records, aaaa_records, ptr_records, txt_records, mx_records, soa_records = get_dns_records(hostname)

            with open(output_file, 'a') as output_file:
                output_file.write(f"\nProcessing URL: {url}")
                output_file.write("\nDNS Records:")
                if a_records:
                    output_file.write(f"\nA Records: {a_records}")
                else:
                    output_file.write("\nNo A Records found.")

                if aaaa_records:
                    output_file.write("\n\nAAAA Records:")
                    for line in aaaa_records:
                        output_file.write(f"\n{line}")
                else:
                    output_file.write("\nNo AAAA Records found.")

                if ptr_records:
                    output_file.write(f"\n\nPTR Records: {ptr_records}")
                else:
                    output_file.write("\nNo PTR Records found.")

                if txt_records:
                    output_file.write("\n\nTXT Records:")
                    for line in txt_records:
                        output_file.write(f"\n{line}")
                else:
                    output_file.write("\nNo TXT Records found.")

                if mx_records:
                    output_file.write("\n\nMX Records:")
                    for line in mx_records:
                        output_file.write(f"\n{line}")
                else:
                    output_file.write("\nNo MX Records found.")

                if soa_records:
                    output_file.write(f"\n\nSOA Records: {soa_records}")
                else:
                    output_file.write("\nNo SOA Records found.")

                headers = get_http_headers(url)

                tls_ssl_certificate = fetch_tls_ssl_certificate(hostname)

                if headers:
                    output_file.write("\n\nHTTP Headers:")
                    for key, value in headers.items():
                        output_file.write(f"\n{key}: {value} ")

                    if tls_ssl_certificate:
                        output_file.write("\n\nTLS/SSL Certificate Information:")
                        for key, value in tls_ssl_certificate.items():
                            output_file.write(f"\n{key}: {value}")
                    else:
                        output_file.write("\nFailed to fetch TLS/SSL certificate.")
                else:
                    output_file.write("\nFailed to fetch HTTP headers.")

                server_header = headers.get("Server", "") if headers else ""
                cdn_provider = findcdnfromhost(server_header)
                output_file.write(f"\n\nCDN Provider: {cdn_provider}\n\n")

        except Exception as e:
            print(f"Error processing URL {url}:")
            with open(output_file, 'a') as output_file:
                output_file.write(f"\nError processing URL {url}:\n")

    def cdn_finder_main():
        user_input = input("Enter '1' to provide a URL, '2' to provide a text file with URLs: ")

        if user_input == '1':
            url = input("Enter the URL: ")
            urls = [url]  # Single URL
        elif user_input == '2':
            file_name = input("Enter the name of the text file with URLs: ")
            with open(file_name, 'r') as file:
                urls = [line.strip() for line in file.readlines() if line.strip()]
        else:
            print("Invalid input. Exiting.")
            exit()

        output_filename = input("Enter the output file name: ")

        # Threading setup
        max_threads = min(10, len(urls))  # Use up to 10 threads or as many as URLs
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Create a list to hold all futures
            futures = [executor.submit(process_url, url, output_filename) for url in urls]

            # Use tqdm to show progress bar
            for future in tqdm(as_completed(futures), total=len(urls), desc="Processing URLs"):
                try:
                    future.result()  # This will re-raise any exception that was raised in the thread
                except Exception as e:
                    print("An error occurred in a thread:")

        print(f"Output saved to {output_filename}")

    cdn_finder_main()

#===CDN FINDER2===#
def cdn_finder2():

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    generate_ascii_banner("CDN", "FINDER 2")

    cdn_endpoints = [
        ("kendo.cdn.telerik.com", "CloudFront"),
        ("cdn.jsdelivr.net", "CloudFlare"),
        ("cdn.statically.io", "CloudFlare"),

        ("www.facebook.com", "Facebook"),
        ("fonts.gstatic.com", "Google"),
        ("www.instagram.com", "Facebook"),

        ("instagram.com", "Facebook"),
        ("schema.org", "Google"),
        ("www.w3.org", "Cloudflare"),
        ("www.youtube.com", "Google"),
        ("fonts.googleapis.com", "Google"),
        ("www.tiktok.com", "Akamai"),
        ("use.fontawesome.com", "Cloudflare"),
        ("www.googletagmanager.com", "Google"),
        ("www.googletagservices.com", "Google"),
        ("www.google-analytics.com", "Google"),
        ("www.google.com", "Google"),
        ("www.gstatic.com", "Google"),
        ("www.snapchat.com", "Google"),
        ("cdnjs.cloudflare.com", "Cloudflare"),
        ("www.fastly.com", "Fastly"),
        ("www.apple.com", "Akamai"),
        ("cdn.intellimize.co", "Fastly"),
        ("www.linkedin.com", "Akamai"),
        ("www.twitter.com", "Twitter"),
        ("www.cloudflare.com", "Cloudflare"),
        ("cdn-cookieyes.com", "Cloudflare"),
        ("ns1.tstt.net.tt", "TsTT"),
        ("ns2.tstt.net.tt", "TsTT"),
        ("www.cachefly.com", "CacheFly"),
        ("www.maxcdn.com", "MaxCDN"),
        ("www.maxcdn.net", "MaxCDN"),
        ("www.netdna-cdn.com", "MaxCDN"),
        ("www.netdna-ssl.com", "MaxCDN"),
        ("www.netdna.com", "MaxCDN"),
    ]

    def resolve_hostname(hostname):
        ip_addresses = set()
        try:
            addr_info = socket.getaddrinfo(hostname, None)
            for info in addr_info:
                ip = info[4][0]
                ip_addresses.add(ip)
        except socket.gaierror:
            print(f"{Fore.RED}Could not resolve {hostname}.{Fore.RESET}")
        return list(ip_addresses)

    def reverse_dns_lookup(ip):
        try:
            hostname = socket.gethostbyaddr(ip)[0]

            return hostname
        
        except socket.herror:
            return "No record found"

    def check_direct_connection(ip, scheme="https"):
        try:
            url = f"{scheme}://[{ip}]" if ':' in ip else f"{scheme}://{ip}"
            response = requests.get(url, timeout=3, verify=False)
            server = response.headers.get("Server", "Server information not found")
            return True, server
        except requests.RequestException:
            print(f"{Fore.RED}Connection error with {ip}.{Fore.RESET}")
            return False, "Server information not found"

    def check_cdn_reachability(cdn_hostname, cdn_name, host_ip, output, unique_results, original_host, scheme="https"):
        print(f"\nChecking CDN: {cdn_name} ({cdn_hostname})")
        cdn_ips = resolve_hostname(cdn_hostname)
        if not cdn_ips:
            print(f"{Fore.RED}Could not resolve {cdn_hostname}.{Fore.RESET}")
            return
        print(f"{Fore.CYAN}Resolved IPs for {cdn_hostname}: {', '.join(cdn_ips)}{Fore.RESET}")
        for cdn_ip in cdn_ips:
            reverse_dns = reverse_dns_lookup(cdn_ip)
            print(f"{Fore.YELLOW} Checking {cdn_ip}: {reverse_dns}{Fore.RESET}")
            reachable, server_info = check_direct_connection(cdn_ip, scheme=scheme)
            if reachable:
                result_message = (
                    f"{Fore.GREEN}Connection to {original_host} ({host_ip}) via CDN {cdn_name} ({cdn_hostname}) "
                    f"using IP {cdn_ip} is reachable via {scheme.upper()} with server: {server_info} "
                    f"(Reverse DNS: {reverse_dns_lookup(cdn_ip)}).{Fore.RESET}"
                )
                if result_message not in unique_results:
                    output.append(result_message)
                    unique_results.add(result_message)

    def get_host_ips(host_input):
        if os.path.isfile(host_input):
            with open(host_input, 'r') as file:
                hosts = file.read().splitlines()
        else:
            hosts = [host_input]
        
        all_ips = []
        for host in hosts:
            ips = resolve_hostname(host)
            if ips:
                all_ips.append((host, ips))  # Store both the hostname and its resolved IPs
            else:
                print(f"{Fore.RED}Could not resolve {host}.{Fore.RESET}")
        return all_ips

    def cdn_finder2_main():
        output = []
        unique_results = set()
        host_input = input("Enter host IP/CIDR or .txt file with IP/domain or CIDR: ")
        print(f"\nResolving host(s): {host_input}")
        
        host_ips = get_host_ips(host_input)
        if not host_ips:
            print(f"{Fore.RED}No valid IPs resolved.{Fore.RESET}")
            return

        scheme = "https" if not host_input.lower().startswith("http://") else "http"
        with ThreadPoolExecutor() as executor:
            for original_host, ips in host_ips:
                for ip in ips:
                    futures = [
                        executor.submit(
                            check_cdn_reachability, cdn_hostname, cdn_name, ip, output, unique_results, original_host, scheme
                        )
                        for cdn_hostname, cdn_name in cdn_endpoints
                    ]
                    for future in futures:
                        future.result()

        print("\n".join(output))

        if output:
            save_option = input("\nWould you like to save the results to a file? (y/n): ").strip().lower()
            if save_option == 'y':
                filename = input("Enter the filename (with .txt extension): ")
                with open(filename, "w") as f:
                    f.write("\n".join(output))
                print(f"Results saved to {filename}")
        else:
            print(f"{Fore.RED}No reachable CDN connections found. No results to save.{Fore.RESET}")

    cdn_finder2_main()

#===HOST PROXY CHECKER===#
def host_proxy_checker():

    generate_ascii_banner("HOST PROXY", "CHECKER")

    def extract_cert_domain(host):
        try:
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.settimeout(3)
                s.connect((host, 443))
                cert = s.getpeercert()
                subject = dict(x[0] for x in cert.get('subject', []))
                common_name = subject.get('commonName')
                return common_name or host
        except Exception:
            return host

    def check_udp_dns(host, domain_to_query=None):
        try:
            if not domain_to_query:
                domain_to_query = host
            transaction_id = os.urandom(2)
            flags = b'\x01\x00'  # standard query
            questions = b'\x00\x01'
            answer_rrs = authority_rrs = additional_rrs = b'\x00\x00'
            header = transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs

            qname = b''.join((bytes([len(label)]) + label.encode() for label in domain_to_query.split('.'))) + b'\x00'
            qtype = b'\x00\x01'  # A record
            qclass = b'\x00\x01'  # IN
            query = header + qname + qtype + qclass

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2)
            sock.sendto(query, (host, 53))
            data, _ = sock.recvfrom(512)
            return True if data else False
        except Exception:
            return False
        finally:
            sock.close()

    def try_request(url, isp_domain):
        try:
            headers = {"Host": isp_domain}
            response = requests.get(url, headers=headers, timeout=5)
            return response.status_code, response.headers.get('Server'), response.headers.get('Connection')
        except Exception:
            return None, None, None

    def save_result(line, filename, save_flag):
        if save_flag:
            with open(filename, "a") as f:
                f.write(line + "\n")

    def is_ip(item):
        try:
            socket.inet_aton(item)
            return True
        except socket.error:
            return False

    def is_cidr(item):
        try:
            ipaddress.IPv4Network(item)
            return True
        except Exception:
            return False

    def resolve_domain(domain):
        try:
            return socket.gethostbyname(domain)
        except:
            return None

    def process_target(target, save_flag, output_file, path, isp_domain):
        if not target:
            return

        hostname = target
        if target.startswith("http://") or target.startswith("https://"):
            hostname = urlparse(target).netloc

        target_http = "http://" + hostname
        target_https = "https://" + hostname

        saved = False

        for url in [target_http, target_https]:
            status_code, server, connection = try_request(url, isp_domain)
            if status_code:
                server = server or "Unknown"
                connection = connection or "Unknown"
                print(f"\033[94mURL:\033[0m {url}")
                print(f"\033[92mStatus:\033[0m {status_code} | \033[93mServer:\033[0m {server} | \033[96mConnection:\033[0m {connection}")

                # Save if status code is 200 OK, regardless of Connection header
                if status_code in [200, 301, 400, 405, 409, 500]:
                    line = f"{url} | Status: {status_code} | Server: {server} | Connection: {connection}"
                    save_result(line, output_file, save_flag)
                    saved = True

        ip_to_check = resolve_domain(hostname) or hostname
        udp_open = check_udp_dns(ip_to_check, isp_domain)
        if udp_open:
            print(f"\033[92mUDP port 53 OPEN on {ip_to_check} (queried {isp_domain})\033[0m")
            line = f"{ip_to_check} | UDP port 53 OPEN (queried {isp_domain})"
            save_result(line, output_file, save_flag)
            saved = True

        return saved

    def mj4():
        isp_list = [
            "isp1.example.com",
            "google.com",
            "ns1.isp.org"
        ]

        print("Choose ISP domain to use as MITM for checks:")
        for idx, isp in enumerate(isp_list, 1):
            print(f"  {idx}. {isp}")
        print(f"  {len(isp_list)+1}. Enter domain")

        choice = input(f"Select option (1-{len(isp_list)+1}): ").strip()

        if choice == str(len(isp_list)+1):
            isp_domain = input("Enter custom domain: ").strip()
        elif choice.isdigit() and 1 <= int(choice) <= len(isp_list):
            isp_domain = isp_list[int(choice)-1]
        else:
            print("Invalid choice, defaulting to first ISP.")
            isp_domain = isp_list[0]

        print(f"Using ISP domain: {isp_domain}")

        input_data = input("Enter IP / domain / CIDR / filename: ").strip()
        path = "/"
        save_results = input("Do you want to save successful connections? (yes/no): ").strip().lower()
        save_flag = save_results == "yes" or save_results == "y"
        output_file = input("Enter output filename (default: results.txt): ").strip() or "results.txt"

        targets = []

        if os.path.isfile(input_data) and input_data.endswith(".txt"):
            with open(input_data, "r") as f:
                for line in f:
                    item = line.strip()
                    if item:
                        targets.append(item)
        elif is_cidr(input_data):
            net = ipaddress.IPv4Network(input_data, strict=False)
            targets.extend(str(ip) for ip in net.hosts())
        else:
            targets.append(input_data)

        saved_any = False
        # Use ThreadPoolExecutor with tqdm progress bar
        with ThreadPoolExecutor(max_workers=255) as executor:
            futures = {executor.submit(process_target, target, save_flag, output_file, path, isp_domain): target for target in targets}

            for f in tqdm(as_completed(futures), total=len(futures), desc="Scanning targets"):
                if f.result():
                    saved_any = True

        if save_flag:
            if saved_any:
                print(f"\033[92mResults saved to {output_file}\033[0m")
            else:
                print(f"\033[93mNo successful connections (200 OK) or UDP open ports found. Nothing saved.\033[0m")

    mj4()

#===WEB CRAWLER===#
def web_crawler():
    
    import aiohttp
    from urllib.parse import urlparse, urljoin
    from bs4 import BeautifulSoup
    import asyncio
    import time
    import os
    import socket
    import random

    def generate_ascii_banner(title, subtitle):
        print(f"==== {title} :: {subtitle} ====")

    generate_ascii_banner("WEB", "CRAWLER")

    visited_urls = {}
    found_urls = set()
    output_file = input("Input filename for output: ")
    max_depth = int(input("Enter maximum crawl depth (e.g. 2): ").strip())
    start_domain = None
    last_save = time.time()
    concurrency_limit = 5000

    # Load visited URLs if output file exists
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) == 4:
                    url, response_code, server, ip = parts
                    visited_urls[url] = {"response_code": response_code, "server": server, "ip": ip}

    async def fetch_url(session, url, depth):
        netloc = urlparse(url).netloc
        if url in visited_urls or (start_domain and not (netloc == start_domain or netloc.endswith('.' + start_domain))):
            return False
        if depth > max_depth:
            return False

        async with asyncio.Semaphore(concurrency_limit):
            try:
                headers = {
                    "User-Agent": random.choice([
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
                        "Mozilla/5.0 (Linux; Android 10; SM-G975F)...",
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0)..."
                    ])
                }

                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response_code = response.status
                    server = response.headers.get('Server', 'Unknown')
                    ip_address = socket.gethostbyname(netloc)
                    visited_urls[url] = {
                        "response_code": response_code,
                        "server": server,
                        "ip": ip_address
                    }
                    print(f"DEPTH {depth} | URL: {url} | Code: {response_code} | Server: {server} | IP: {ip_address}")

                    if response_code == 200 and depth < max_depth:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        tasks = []
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            next_url = urljoin(url, href).split('#')[0]
                            if next_url not in found_urls:
                                found_urls.add(next_url)
                                tasks.append(fetch_url(session, next_url, depth + 1))

                        if tasks:
                            await asyncio.gather(*tasks)

                    if len(found_urls) % 100 == 0 or time.time() - last_save > 300:
                        save_output()

                    return True

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"Error for {url}: {e}")
            except Exception as e:
                print(f"Unexpected error for {url}: {e}")

        return False


    def save_output():
        global last_save
        with open(output_file, 'w') as f:
            for url, data in visited_urls.items():
                f.write(f"{url} | Response Code: {data['response_code']} | Server: {data['server']} | IP: {data['ip']}\n")
        print(f"Output saved to {output_file}")
        last_save = time.time()

    async def process_sequential_urls(url_list):
        async with aiohttp.ClientSession() as session:
            for url in url_list:
                parsed_url = urlparse(url.strip())
                if not parsed_url.scheme:
                    url = 'https://' + url.strip()
                elif parsed_url.scheme not in ["http", "https"]:
                    print(f"Invalid URL scheme for {url}, skipping...")
                    continue
                global start_domain
                start_domain = urlparse(url).netloc
                print(f"\nProcessing domain: {start_domain}")
                new_urls_found = await fetch_url(session, url, depth=0)
                if not new_urls_found:
                    save_output()

    async def web_crawler_main():
        url_or_file = input("Enter a URL to crawl or a file name: ").strip()

        if url_or_file.endswith('.txt'):
            try:
                with open(url_or_file, 'r') as f:
                    urls = [line.strip() for line in f.readlines()]
                    await process_sequential_urls(urls)
            except FileNotFoundError:
                print("Error: File not found.")
        else:
            parsed_url = urlparse(url_or_file)
            if not parsed_url.scheme:
                url_or_file = 'https://' + url_or_file
            await process_sequential_urls([url_or_file])

        save_output()
        print("\nCrawl complete. Output saved.")

    asyncio.run(web_crawler_main())

#===DOSSIER===#
def dossier():

    generate_ascii_banner("DOSSIER", "")

    print(GREEN + "use with proxies from the free proxy option " + ENDC)
    print(RED + "http proxies seems to work best so far " + ENDC)

    # Add scan completion flag
    scan_complete = threading.Event()

    def generate_url(website, page):
        if page == 1:
            return f"http://www.sitedossier.com/referer/{website}/{page}"
        else:
            return f"http://www.sitedossier.com/referer/{website}/{(page-1)*100}"

    def fetch_table_data(url, proxies=None):
        try:
            response = requests.get(url, proxies=proxies, timeout=10)
            response.raise_for_status()
            
            if "End of list." in response.text:
                scan_complete.set()
                return False, "END"
                
            if response.status_code == 404:
                print("Job done.")
                return False, None
                
            if "Please enter the unique \"word\" below to confirm" in response.text:
                return False, None
                
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table')
                if table:
                    rows = table.find_all('tr')
                    data = []
                    for row in rows:
                        cells = row.find_all('td')
                        if cells:
                            row_data = [cell.text.strip() for cell in cells if cell.text.strip()]
                            if row_data:
                                data.append('\n'.join(row_data))
                    return True, data
                else:
                    print("No table found on page")
                    return False, None
        except Exception as e:
            print(f"Error fetching data: {e}")
            return False, None

    def load_domains_from_file(filename):
        domains = []
        with open(filename, 'r') as file:
            for line in file:
                domains.append(line.strip())
        return domains

    def load_proxies_from_file(filename):
        proxies = []
        try:
            with open(filename, 'r') as file:
                for line in file:
                    proxies.append(line.strip())
            return proxies
        except FileNotFoundError:
            print(f"File '{filename}' not found. Please provide a valid file name.")
            return []
        except Exception as e:
            print(f"Error reading file: {e}")
            return []

    def save_to_file(filename, data):
        # Initialize counters if they don't exist
        if not hasattr(save_to_file, 'total_items'):
            save_to_file.total_items = 0
            save_to_file.total_urls = 0
        
        save_to_file.total_items += len(data)
        save_to_file.total_urls += 1
        
        with open(filename, 'a') as file:
            for item in data:
                file.write(item.strip())
                file.write('\n')
        
        print(f"\nProgress: {save_to_file.total_items} total items saved from {save_to_file.total_urls} URLs")

    def fetch_data(url, proxies, save_file, output_file):
        if scan_complete.is_set():
            return
            
        if proxies:
            proxy_index = 0
            with tqdm(total=1, desc=f"Fetching {url}", leave=True) as pbar:
                while not scan_complete.is_set():
                    success, data = fetch_table_data(url, proxies={'http': proxies[proxy_index], 'https': proxies[proxy_index]})
                    
                    if data == "END":
                        print("\nReached end of list - stopping scan")
                        break
                        
                    if success:
                        pbar.update(1)
                        print(f"\nSuccess: {url}")
                        for item in data:
                            print(item)
                        if save_file == "yes":
                            save_to_file(output_file, data)
                        break
                        
                    proxy_index = (proxy_index + 1) % len(proxies)
                    if proxy_index == 0:
                        pbar.update(1)
                        break
        else:
            with tqdm(total=1, desc=f"Fetching {url}", leave=True) as pbar:
                success, data = fetch_table_data(url)
                if data == "END":
                    print("\nReached end of list - stopping scan") 
                    return
                if success:
                    pbar.update(1)
                    print(f"\nSuccess: {url}")
                    for item in data:
                        print(item)
                    if save_file == "yes":
                        save_to_file(output_file, data)
                else:
                    pbar.update(1)

    def dossier_main():
        scan_complete.clear()
        
        input_type = input("Choose input type (single/file): ").lower()
        
        if input_type == "single":
            website = input("Enter the website (e.g., who.int): ")
            num_pages = int(input("Enter the number of pages to fetch: "))
            urls = [generate_url(website, page) for page in range(1, num_pages + 1)]
            
        elif input_type == "file":
            domain_list_file = input("Enter the filename containing list of domains: ")
            domains = load_domains_from_file(domain_list_file)
            num_pages = int(input("Enter the number of pages to fetch per domain: "))
            urls = []
            for domain in domains:
                urls.extend([generate_url(domain, page) for page in range(1, num_pages + 1)])
        else:
            randomshit("you fool, you have chosen the wrong option")
            print("Reterning to main because you messed up.")
            time.sleep(2)
            return
        
        use_proxy = input("Do you want to use a proxy? (yes/no): ").lower()
        if use_proxy == "yes":
            proxy_list_name = input("Enter the proxy list file name: ")
            proxies = load_proxies_from_file(proxy_list_name)
        else:
            proxies = None
        
        save_file = input("Do you want to save the output data to a file? (yes/no): ").lower()
        if save_file == "yes":
            output_file = input("Enter the filename to save the output data (without extension): ") + ".txt"
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for url in urls:
                if scan_complete.is_set():
                    break
                futures.append(executor.submit(fetch_data, url, proxies, save_file, output_file))

            for future in futures:
                try:
                    future.result()
                    if scan_complete.is_set():
                        break
                except Exception as e:
                    print(f"Error in thread: {e}")

        print("Scan completed.")

    dossier_main()

#===HACKER TARGET===#
def hacker_target():
    
    generate_ascii_banner("Hacker", "Target")
    import requests
    import re
    import base64
    import json
    import os
    import platform
    from bs4 import BeautifulSoup


    def clear_screen():
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")


    class DNSDumpsterAPI:
        def __init__(self, verbose=False):
            self.verbose = verbose
            self.authorization = self.get_token()

        def get_token(self):
            session = requests.Session()
            response = session.get("https://dnsdumpster.com/")
            if response.status_code == 200:
                match = re.search(r'{"Authorization":\s?"([^"]+)"', response.text)
                if match:
                    token = match.group(1)
                    if self.verbose:
                        print(f"[+] Authorization Token found: {token}")
                    return token
            if self.verbose:
                print("[-] Failed to retrieve authorization token.")
            return None

        def get_dnsdumpster(self, target):
            if not self.authorization:
                print("[-] Authorization token is missing.")
                return None
            url = "https://api.dnsdumpster.com/htmld/"
            headers = {"Authorization": self.authorization}
            data = {"target": target}
            response = requests.post(url, headers=headers, data=data)
            return response.text if response.status_code == 200 else None

        def parse_dnsdumpster(self, html, domain):
            soup = BeautifulSoup(html, 'html.parser')
            tables = soup.findAll('table')
            res = {'domain': domain, 'dns_records': {}}

            if len(tables) >= 4:
                res['dns_records']['a'] = self.retrieve_results(tables[1])
                res['dns_records']['mx'] = self.retrieve_results(tables[2])
                res['dns_records']['ns'] = self.retrieve_results(tables[3])
                res['dns_records']['txt'] = self.retrieve_txt_record(tables[4])

                # Image
                try:
                    pattern = rf'https://api.dnsdumpster.com/static/maps/{re.escape(domain)}-[a-f0-9\-]+\.png'
                    map_url = re.findall(pattern, html)[0]
                    image_data = base64.b64encode(requests.get(map_url).content).decode('utf-8')
                    res['image_data'] = image_data
                except:
                    res['image_data'] = None

                # XLS
                try:
                    pattern = rf'https://api.dnsdumpster.com/static/xlsx/{re.escape(domain)}-[a-f0-9\-]+\.xlsx'
                    xls_url = re.findall(pattern, html)[0]
                    xls_data = base64.b64encode(requests.get(xls_url).content).decode('utf-8')
                    res['xls_data'] = xls_data
                except:
                    res['xls_data'] = None
            else:
                if self.verbose:
                    print("[-] Expected tables not found.")
                return None
            return res

        def retrieve_results(self, table):
            res = []
            for tr in table.findAll('tr'):
                tds = tr.findAll('td')
                try:
                    host = str(tds[0]).split('<br/>')[0].split('>')[1].split('<')[0]
                    ip = re.findall(r'\d+\.\d+\.\d+\.\d+', tds[1].text)[0]
                    reverse_dns = tds[1].find('span').text if tds[1].find('span') else ""
                    autonomous_system = tds[2].text if len(tds) > 2 else ""
                    asn = autonomous_system.split('\n')[1] if '\n' in autonomous_system else ""
                    asn_range = autonomous_system.split('\n')[2] if '\n' in autonomous_system else ""
                    span_elements = tds[3].find_all('span', class_='sm-text') if len(tds) > 3 else []
                    asn_name = span_elements[0].text.strip() if len(span_elements) > 0 else ""
                    country = span_elements[1].text.strip() if len(span_elements) > 1 else ""
                    open_service = "\n".join([line.strip() for line in tds[4].text.splitlines() if line.strip()]) if len(tds) > 4 else "N/A"
                    res.append({
                        'host': host,
                        'ip': ip,
                        'reverse_dns': reverse_dns,
                        'as': asn,
                        'asn_range': asn_range,
                        'asn_name': asn_name,
                        'asn_country': country,
                        'open_service': open_service
                    })
                except Exception:
                    continue
            return res

        def retrieve_txt_record(self, table):
            return [td.text.strip() for td in table.findAll('td')]

        def search(self, domain):
            if self.verbose:
                print(f"[+] Searching for domain: {domain}")
            html = self.get_dnsdumpster(domain)
            return self.parse_dnsdumpster(html, domain) if html else None


    # ======= HackerTarget Tools =======
    def save_output(filename, content):
        with open(filename, "w") as f:
            f.write(content)
        print(f"[+] Output saved to {filename}")


    def hostsearch(target):
        try:
            result = requests.get(f"https://api.hackertarget.com/hostsearch/?q={target}").text
            count = len(result.splitlines())
            print(f"[+] {count} domains found.\n")
            print(result)
            save_output(f"{target}_hostsearch.txt", result)
        except:
            print("[-] Error occurred during hostsearch.")


    def reversedns(target):
        try:
            result = requests.get(f"https://api.hackertarget.com/reversedns/?q={target}").text
            print(result)
            save_output(f"{target}_reversedns.txt", result)
        except:
            print("[-] Error occurred during reversedns.")


    def dnslookup(target):
        try:
            result = requests.get(f"https://api.hackertarget.com/dnslookup/?q={target}").text
            print(result)
            save_output(f"{target}_dnslookup.txt", result)
        except:
            print("[-] Error occurred during dnslookup.")


    def gethttpheaders(target):
        try:
            result = requests.get(f"https://api.hackertarget.com/httpheaders/?q={target}").text
            print(result)
            save_output(f"{target}_httpheaders.txt", result)
        except:
            print("[-] Error occurred during http headers fetch.")


    # ======== Main ========
    def hacker_target_main():
        # Show menu first
        while True:
            print("\n[+] Select a scanning option:")
            print("[1] Host Search")
            print("[2] Reverse DNS")
            print("[3] DNS Lookup")
            print("[4] HTTP Headers")
            print("[5] DNS Dumpster (Full Domain Scan)")
            print("[6] Exit")

            choice = input("\nChoose an option [1-6]: ").strip()

            if choice == "1":
                clear_screen()
                target = input("Enter the host to search: ").strip()
                hostsearch(target)
                input("\nPress Enter to return to menu...")
                clear_screen()

            elif choice == "2":
                clear_screen()
                target = input("Enter IP or domain for reverse DNS lookup: ").strip()
                reversedns(target)
                input("\nPress Enter to return to menu...")
                clear_screen()

            elif choice == "3":
                clear_screen()
                target = input("Enter domain for DNS lookup: ").strip()
                dnslookup(target)
                input("\nPress Enter to return to menu...")
                clear_screen()

            elif choice == "4":
                clear_screen()
                target = input("Enter URL for HTTP headers check (e.g., example.com): ").strip()
                gethttpheaders(target)
                input("\nPress Enter to return to menu...")
                clear_screen()

            elif choice == "5":
                clear_screen()
                target = input("Enter domain for full DNS dumpster scan: ").strip()
                
                api = DNSDumpsterAPI(verbose=True)
                res = api.search(target)

                if res:
                    print("\n[+] DNSDumpster Results:")
                    for key in ['a', 'mx', 'ns']:
                        print(f"\n### {key.upper()} Records ###")
                        for record in res['dns_records'].get(key, []):
                            print(f"{record['host']} ({record['ip']}) - {record['asn_name']} [{record['asn_country']}]")
                    print("\n### TXT Records ###")
                    for txt in res['dns_records'].get('txt', []):
                        print(txt)

                    with open(f"{target}_dnsdumpster_results.json", "w") as f:
                        json.dump(res, f, indent=4)
                    print(f"\n[+] Results saved to {target}_dnsdumpster_results.json")

                    if res.get("image_data"):
                        with open(f"{target}_network_map.png", "wb") as f:
                            f.write(base64.b64decode(res["image_data"]))
                        print(f"[+] Network map saved as {target}_network_map.png")

                    if res.get("xls_data"):
                        with open(f"{target}_hosts.xlsx", "wb") as f:
                            f.write(base64.b64decode(res["xls_data"]))
                        print(f"[+] XLS data saved as {target}_hosts.xlsx")
                else:
                    print("[-] DNSDumpster failed or no data found.")
                
                input("\nPress Enter to return to menu...")

            elif choice == "6":
                clear_screen()
                print("\nGoodbye!")
                break

            else:
                print("\nInvalid choice. Please select 1-6.")
                input("Press Enter to try again...")

    hacker_target_main()

#===URL REDIRECT===#
def url_redirect():

    generate_ascii_banner("URL", "REDIRECT")

    def get_ssl_server_info(hostname):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    return cert.get('subject', [('commonName', 'Unknown')])[0][1]
        except Exception:
            return 'info not available'

    def check_url(url):
        try:
            response = requests.get(url, timeout=3, allow_redirects=False)
            if response.status_code == 200:
                server_info = response.headers.get('Server', 'Server info not available')
                # If URL is HTTPS and server_info was not found, fetch SSL info
                if url.startswith('https://') and server_info == 'Server info not available':
                    hostname = re.sub(r'^https?://', '', url).split('/')[0]
                    server_info = get_ssl_server_info(hostname)
                return url, 200, server_info
        except requests.RequestException:
            return None

        return None

    def process_hostname(hostname):
        results = []
        for protocol in ['http://', 'https://']:
            url = f"{protocol}{hostname}"
            result = check_url(url)
            if result:
                results.append(result)
        return results

    def url_redirect_main():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_name = input("Enter the filename containing URLs or hostnames: ").strip()
        file_path = os.path.join(script_dir, file_name)

        urls = []
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]
        else:
            urls.append(file_name)

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(process_hostname, url): url for url in urls}
            for future in tqdm(as_completed(futures), total=len(urls), desc="Processing hostnames"):
                try:
                    result = future.result()
                    if result:
                        results.extend(result)
                except Exception as e:
                    print(f"Error processing hostname {futures[future]}: {e}")

        output_file = os.path.join(script_dir, 'cdn_data.txt')
        with open(output_file, 'w') as file:
            for url, status_code, server_info in results:
                info = f"{url} - Status Code: {status_code}\nServer Info: {server_info}\n"
                print(f"\033[92m{info}\033[0m")
                file.write(info + '\n')

    url_redirect_main()
    print("file saved to: cdn_data.txt")

#===TWISTED===#  
def twisted():

    generate_ascii_banner("TWISTED", "")

    def text(url_input):
        return os.path.isfile(url_input)

    def is_alive(connection_header):
        if connection_header:
            return 'alive' if 'keep-alive' in connection_header.lower() else 'inactive'
        return 'inactive'

    def extract_sources(csp_header, directives):
        if csp_header:
            sources = {}
            for directive in directives:
                pattern = rf"{directive}\s+([^;]+)"
                match = re.search(pattern, csp_header.lower())
                if match:
                    sources[directive] = match.group(1).strip().split()
            return sources if sources else "No sources found"
        return "header not found"

    def fetch_url(url, expected_csp_directives, output_set):
        output_lines = []
        try:
            r = requests.get(f"http://{url}", allow_redirects=True, timeout=3)

            final_conn_status = r.headers.get('connection', '')
            final_server_info = r.headers.get('server', '').lower() or 'Server info unavailable'
            csp_header = r.headers.get('content-security-policy', '')

            for resp in r.history:
                history_conn_status = resp.headers.get('connection', '') or 'inactive'
                history_server_info = resp.headers.get('server', '').lower() or 'Server info unavailable'
                redirect_info = f"Redirected to: {resp.url}, Status Code: {resp.status_code}, Connection: {is_alive(history_conn_status)}, Server Info: {history_server_info}"
                if redirect_info not in output_lines:
                    output_lines.append(redirect_info)
                print(redirect_info)

            final_info = f"Final Hosted Url: {r.url}, Status Code: {r.status_code}, Connection: {is_alive(final_conn_status)}, Server Info: {final_server_info}"
            if final_info not in output_lines:
                output_lines.append(final_info)
            print(final_info)
            
            sources = extract_sources(csp_header, expected_csp_directives)
            if isinstance(sources, dict):
                for directive, src_list in sources.items():
                    for src in src_list:
                        if src.startswith("*."):
                            src = src[2:]
                        if src not in output_set:
                            output_set.add(src)
                            output_lines.append(f"{src}")
            else:
                output_lines.append(sources)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching: {url}")

        return output_lines

    def twisted_main():
        url_input = input("Enter URL or path to .txt file: ")
        save_output_choice = input("Save the output? (yes/no): ").strip().lower()
        output_file = input("Output filename: ") if save_output_choice == "yes" else None

        expected_csp_directives = [
            "default-src",
            "script-src",
            "style-src",
            "connect-src",
            "font-src",
            "img-src",
            "media-src",
            "frame-src",
            "worker-src",
            "source value",
            "base-uri",
            "block-all-mixed-content",
            "child-src",
            "fenced-frame-src",
            "frame-ancestors",
            "form-action",
            "frame-src",
            "manifest-src",
            "object-src",
            "prefetch-src",
            "report-to",
            "report-uri",
            "require-trusted-types-for",
            "sandbox",
            "script-src-attr",
            "script-src-elem",
            "upgrade-insecure-requests",
            "trusted-types"
        ]

        if text(url_input):
            with open(url_input, 'r') as file:
                urls = [line.strip() for line in file if line.strip()]
        else:
            urls = [url_input]

        output_set = set()
        results = []
        
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = {executor.submit(fetch_url, url, expected_csp_directives, output_set): url for url in urls}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing URLs"):
                results.append(future.result())

        if save_output_choice == "yes" and output_file:
            with open(output_file, 'w') as file:
                for result in results:
                    if result:
                        for line in result:
                            file.write(f"{line}\n")
                        file.write("\n")

        print(f"\nTotal found: {len(output_set)}")

        print(f"Output saved to {output_file}" if save_output_choice == "yes" else "Output not saved.")

    twisted_main()

#===STAT===#
def stat():
    from urllib.parse import urljoin, urlparse
    from collections import OrderedDict
    from typing import List
    from urllib.parse import urlparse, urlunparse

    class URLTracker:
        def __init__(self):
            self.processed_urls = set()
            self.results = OrderedDict()
            self.processed_domains = set()

        def add_url(self, url):
            """Thread-safe URL addition with domain tracking."""
            normalized = self.normalize_url(url)
            domain = urlparse(normalized).netloc
            
            # Use tuple to ensure thread-safe checking
            key = (normalized, domain)
            if key not in self._get_processed_keys():
                self.processed_urls.add(normalized)
                self.processed_domains.add(domain)
                return True
            return False
        
        def _get_processed_keys(self):
            """Get set of (url, domain) tuples for processed URLs."""
            return {(url, urlparse(url).netloc) for url in self.processed_urls}

        def is_domain_processed(self, domain):
            """Check if a domain has been processed."""
            return domain in self.processed_domains

        @staticmethod
        def normalize_url(url):
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip('/')

        def get_stats(self):
            """Get statistics about processed URLs."""
            return {
                'total_processed': len(self.processed_urls),
                'unique_domains': len({urlparse(url).netloc for url in self.processed_urls})
            }

    class DomainChecker:
        def __init__(self, max_workers=20, timeout=5):
            self.max_workers = max_workers
            self.timeout = timeout
            self.session = requests.Session()
            self.analyzed_domains = set()  # Track analyzed domains to prevent loops

        def check_domain_status(self, domain):
            """Enhanced domain check with CSP analysis."""
            if domain in self.analyzed_domains:
                return None
            self.analyzed_domains.add(domain)
            
            try:
                response = self.session.get(domain, timeout=self.timeout, allow_redirects=True)
                result = {
                    'domain': domain,
                    'status': response.status_code,
                    'server': response.headers.get('server', 'Not specified'),
                    'content_type': response.headers.get('content-type', 'Not specified'),
                    'redirect': response.url if response.history else None,
                    'csp': self.extract_csp_headers(response),
                    'csp_domains': set()
                }
                
                # Extract domains from CSP if present
                if result['csp']:
                    result['csp_domains'] = self.extract_csp_domains(result['csp'])
                
                return result
            except Exception as e:
                return {'domain': domain, 'error': str(e)}

        def extract_csp_headers(self, response):
            """Extract all CSP related headers from response."""
            csp_headers = {}
            for header in response.headers:
                if 'content-security-policy' in header.lower():
                    csp_headers[header] = response.headers[header]
            return csp_headers

        def extract_csp_domains(self, csp_headers):
            """Extract domains from CSP directives."""
            domains = set()
            for csp in csp_headers.values():
                for directive in csp.split(';'):
                    if not directive.strip():
                        continue
                    parts = directive.strip().split()
                    if len(parts) > 1:
                        for source in parts[1:]:
                            domain = self.normalize_csp_source(source)
                            if domain:
                                domains.add(domain)
            return domains

        @staticmethod
        def normalize_csp_source(source):
            """Normalize CSP source to extract valid domain."""
            source = source.strip("'")
            if source in {'self', 'none', 'unsafe-inline', 'unsafe-eval'} or \
            source.startswith(('data:', 'blob:', 'filesystem:', 'about:')):
                return None
                
            if source.startswith('*.'):
                source = source[2:]
            if not source.startswith(('http://', 'https://')):
                source = f'https://{source}'
                
            try:
                parsed = urlparse(source)
                if parsed.netloc:
                    return source
            except Exception:
                pass
            return None

        def check_domains_parallel(self, domains):
            """Check multiple domains in parallel."""
            results = []
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_domain = {
                    executor.submit(self.check_domain_status, domain): domain 
                    for domain in domains
                }
                
                with tqdm(total=len(future_to_domain), desc="Checking domains") as pbar:
                    for future in as_completed(future_to_domain):
                        result = future.result()
                        results.append(result)
                        pbar.update(1)
            
            return results

    def log_csp_analysis(result, outfile, indent="    "):
        """Log CSP analysis results."""
        if 'csp' in result and result['csp']:
            log_output(f"{indent}CSP Headers found:", outfile)
            for header, value in result['csp'].items():
                log_output(f"{indent}  {header}:", outfile)
                for directive in value.split(';'):
                    if directive.strip():
                        log_output(f"{indent}    {directive.strip()}", outfile)
            
            if result.get('csp_domains'):
                log_output(f"{indent}  CSP Referenced Domains:", outfile)
                for domain in result['csp_domains']:
                    log_output(f"{indent}    - {domain}", outfile)

    def check_csp_domains(csp, outfile, source, url_tracker):
        """Enhanced CSP domain checking with recursive analysis."""
        domains = set()
        if not csp:
            return domains
        
        # List of special CSP keywords to ignore
        CSP_KEYWORDS = {
            'self', 'none', 'unsafe-inline', 'unsafe-eval', 
            'strict-dynamic', 'report-sample', '*', "'none'", "'self'",
            'unsafe-hashes', 'wasm-unsafe-eval', 'data:', 'blob:' 'filesystem:', 'about:',
        }
        
        for directive in csp.split(';'):
            if not directive.strip():
                continue
                
            policy_name, *sources = directive.strip().split()
            new_domains = set()
            
            for source in sources:
                source = source.replace('*.', '').strip("'")
                
                if (source.lower() in CSP_KEYWORDS or 
                    source.startswith(('data:', 'blob:', 'filesystem:', 'about:'))):
                    continue
                
                if source and not source.startswith(('http://', 'https://')):
                    source = f'https://{source}' if not source.startswith('//') else f'https:{source}'
                
                try:
                    parsed = urlparse(source)
                    if parsed.netloc and not url_tracker.is_domain_processed(parsed.netloc):
                        new_domains.add(source)
                except Exception:
                    continue
            
            if new_domains:
                log_output(f"\nChecking new domains for {policy_name}:", outfile)
                checker = DomainChecker()
                results = checker.check_domains_parallel(new_domains)
                
                for result in results:
                    if 'error' in result:
                        log_output(f"  Domain: {result['domain']} - Error: {result['error']}", outfile)
                    else:
                        log_output(f"  Domain: {result['domain']}", outfile)
                        log_output(f"    Status: {result['status']}", outfile)
                        log_output(f"    Server: {result['server']}", outfile)
                        log_output(f"    Content-Type: {result['content_type']}", outfile)
                        if result['redirect']:
                            log_output(f"    Redirects to: {result['redirect']}", outfile)
                        
                        # Log CSP information if found
                        if 'csp' in result:
                            log_csp_analysis(result, outfile)
                        
                domains.update(new_domains)

        return domains

    def check_url_with_progress(url, base_url, outfile, url_tracker):
        """Thread-safe URL checking with deduplication."""
        if not url_tracker.add_url(url):
            return None  # Skip if URL already processed
        
        try:
            # ...existing check_url_status code but return results instead of logging...
            response = requests.get(url, allow_redirects=True, timeout=5)
            results = []
            results.append(f"\nChecking URL: {url}")
            results.append(f"Final Status: {response.status_code}")
            # ...collect other results...
            return "\n".join(results)
        except Exception as e:
            return f"{url}: Error - {str(e)}"

    def process_urls_parallel(urls_to_check, base_url, outfile, url_tracker, max_workers=20):
        """Enhanced parallel processing with larger thread pool."""
        unique_urls = {url for url in urls_to_check 
                    if not url_tracker.add_url(url)}
        
        if not unique_urls:
            log_output("\nNo new URLs to process.", outfile)
            return
        log_output(f"\nProcessing {len(unique_urls)} unique URLs...", outfile)


        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(check_url_with_progress, url, base_url, outfile, url_tracker): url 
                for url in unique_urls
            }
            
            with tqdm(total=len(futures), desc="Checking URLs") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        log_output(result, outfile)
                    pbar.update(1)

    def analyze_csp_in_response(response, outfile, url_tracker, indent=""):
        """Analyze CSP headers in a response."""
        csp_headers = [
            ('Content-Security-Policy', 'CSP'),
            ('Content-Security-Policy-Report-Only', 'CSP Report-Only')
        ]

        
        found_csp = False
        for header, name in csp_headers:
            csp = response.headers.get(header, "")
            if csp:
                found_csp = True
                log_output(f"{indent}{name}:", outfile)
                policies = csp.split(';')
                for policy in policies:
                    if policy.strip():
                        log_output(f"{indent}  {policy.strip()}", outfile)
                
                # Analyze domains in CSP
                domains = check_csp_domains(csp, outfile, response.url, url_tracker)
                return domains
        
        if not found_csp:
            log_output(f"{indent}No Content Security Policy found", outfile)
        return set()

    def check_url_status(url, base_url, outfile):
        """Enhanced URL status checking with detailed CSP analysis."""
        try:
            if not url.startswith(('http://', 'https://')):
                url = urljoin(base_url, url)
            
            response = requests.get(url, allow_redirects=True, timeout=5)
            log_output(f"\nChecking URL: {url}", outfile)
            log_output(f"Final Status: {response.status_code}", outfile)
            log_output(f"Final URL: {response.url}", outfile)
            
            all_domains = set()
            
            # Create URL tracker for this check
            url_tracker = URLTracker()
            
            # Check redirect chain and their CSPs
            if response.history:
                log_output("\nRedirect Chain Analysis:", outfile)
                for i, hist in enumerate(response.history, 1):
                    log_output(f"\n  [{i}] Redirect URL: {hist.url}", outfile)
                    log_output(f"      Status: {hist.status_code}", outfile)
                    log_output(f"      Server: {hist.headers.get('server', 'Not specified')}", outfile)
                    log_output(f"      Location: {hist.headers.get('location', 'Not specified')}", outfile)
                    
                    log_output("      Security Headers:", outfile)
                    domains = analyze_csp_in_response(hist, outfile, url_tracker, indent="        ")
                    all_domains.update(domains)
            
            # Analyze final response
            log_output("\nFinal Response Analysis:", outfile)
            log_output(f"  URL: {response.url}", outfile)
            log_output(f"  Status: {response.status_code}", outfile)
            log_output(f"  Server: {response.headers.get('server', 'Not specified')}", outfile)
            log_output(f"  Content-Type: {response.headers.get('content-type', 'Not specified')}", outfile)
            
            log_output("\n  Security Headers:", outfile)
            domains = analyze_csp_in_response(response, outfile, url_tracker, indent="    ")
            all_domains.update(domains)
            
            return response, all_domains
        except requests.RequestException as e:
            log_output(f"{url}: Error - {str(e)}", outfile)
            return None, set()


    def log_output(message, file_handle):
        """Log message to both console and file."""
        print(message)
        file_handle.write(message + '\n')

    def create_combined_output_file() -> str:
        """Prompt the user to specify an output .txt file path."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f"combined_scan_{timestamp}.txt"
        
        # Prompt user for file path (or use default)
        user_path = input(f"Enter output file[Press Enter for default: '{default_filename}']: ").strip()
        # Use default if user presses Enter
        output_file = user_path if user_path else default_filename
        
        return output_file

    def analyze_url(url, outfile):
        """Modified analysis function to use shared output file."""
        if not url.startswith(('https://', 'http://')):
            url = 'https://' + url

        log_output("\n" + "="*50, outfile)
        log_output(f"Analyzing URL: {url}", outfile)
        log_output("="*50 + "\n", outfile)
        
        url_tracker = URLTracker()  # Create single tracker instance
        
        try:
            response, initial_domains = check_url_status(url, url, outfile)
            if not response:
                return
            
            # ...existing analysis code...
            
            # Enhanced statistics
            stats = url_tracker.get_stats()
            log_output(f"\n=== Analysis Summary for {url} ===", outfile)
            log_output(f"Total unique URLs processed: {stats['total_processed']}", outfile)
            log_output(f"Unique domains analyzed: {stats['unique_domains']}", outfile)
            log_output("\nCSP Domains Found:", outfile)
            for domain in initial_domains:
                log_output(f"  - {domain}", outfile)
            if initial_domains:
                log_output(f"\nTotal CSP Domains: {len(initial_domains)}", outfile)
            else:
                log_output("\nNo CSP domains found.", outfile)
            log_output("\n" + "-"*50 + "\n", outfile)
            
        except Exception as e:
            log_output(f"\nError during analysis: {str(e)}", outfile)

    def analyze_multiple_urls(urls: List[str]) -> str:
        """Analyze multiple URLs and save to single file."""
        output_file = create_combined_output_file()
        
        with open(output_file, 'w', encoding='utf-8') as outfile:
            log_output("=== URL Analysis Tool Results ===", outfile)
            log_output(f"Scan started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", outfile)
            log_output(f"Number of URLs to analyze: {len(urls)}\n", outfile)
            
            for i, url in enumerate(urls, 1):
                print(f"\nProcessing URL {i}/{len(urls)}: {url}")
                try:
                    analyze_url(url, outfile)
                except Exception as e:
                    log_output(f"Error analyzing {url}: {e}", outfile)
            
            log_output("\n=== Scan Complete ===", outfile)
            log_output(f"Scan finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", outfile)
        
        return output_file

    def is_valid_url(url: str) -> bool:
        """Check if string is a valid URL."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def read_urls_from_file(file_path: str) -> List[str]:
        """Read URLs from file, handling different formats."""
        urls = set()
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    # Clean up the line and extract URL
                    url = line.strip()
                    if url and not url.startswith('#'):  # Skip empty lines and comments
                        if not url.startswith(('http://', 'https://')):
                            url = f'https://{url}'
                        if is_valid_url(url):
                            urls.add(url)
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
        return list(urls)

    def process_input(user_input: str) -> List[str]:
        """Process user input and return list of URLs to analyze."""
        if not user_input:
            return []
            
        # Check if input is a file path
        path = pathlib.Path(user_input)
        if path.is_file():
            print(f"Reading URLs from file: {user_input}")
            return read_urls_from_file(user_input)
        
        # Check if input is a valid URL
        if not user_input.startswith(('http://', 'https://')):
            parsed = urlparse(user_input)
            user_input = urlunparse(parsed._replace(scheme='https'))

        
        return [user_input] if is_valid_url(user_input) else []

    def stat_main():
        """Modified main function for combined output."""
        print("=== URL Analysis Tool ===")
        while True:
            try:
                user_input = input('\nEnter URL or File Name (or "quit" to exit): ').strip()
                if user_input.lower() in ('quit', 'exit', 'q'):
                    break
                    
                if not user_input:
                    print("Please enter a URL or file path")
                    continue

                urls = process_input("http://" + user_input)
                if not urls:
                    print("No valid URLs found in input")
                    continue
                
                print(f"\nFound {len(urls)} URLs to analyze")
                output_file = analyze_multiple_urls(urls)
                
                print("\nAnalysis completed!")
                print(f"All results saved to: {output_file}")
                
                if input('\nAnalyze more URLs? (y/n): ').lower() != 'y':
                    break
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                break
            except Exception as e:
                print(f"\nError: {e}")
                continue
        
        print("\nThank you for using URL Analysis Tool!")

    stat_main()
    time.sleep(2)
    clear_screen()
    file_proccessing()

#============= Enumration Menu ==================#
def Enumeration_menu():

    while True:
        clear_screen()
        banner()
        print(MAGENTA +"=================================="+ ENDC)
        print(MAGENTA +"        Enumeration   Menu        "+ ENDC)    
        print(MAGENTA +"=================================="+ ENDC)
        
        print("1.""  SUBDOmain ENUM""             2."" C.A.S.P.E.R") 
        print("3.""  ASN2""                       4."" WAY BACK")
        print("5.""  OFFLINE SUBDOMAIN ENUM""     6."" WEBSOCKET SCANNER NEW")
        print("7.""  WEBSOCKET SCANNER""          8. ACCESS CONTROL")
        print("9.  IPGEN                     10. OPEN PORT CHECKER")
        print("11. UDP/TCP SCAN              12. DORK SCANNER  ")
        print("13. NS LOOKUP                 14. TCP_SSL")
        print("15. DNS KEY                   16. PAYLOAD HUNTER")
        print("17. Payload Hunter2           18. DNS RECON")

        print("Hit enter to return to the main menu",'\n')
        choice = input("Enter your choice: ")

        if choice == '':
            randomshit("Returning to BUGHUNTERS PRO...")
            time.sleep(2)
            return
        
        elif choice == '1':
            clear_screen()
            subdomain_enum()

        elif choice == '2':
            clear_screen()
            casper()

        elif choice == '3':
            clear_screen()
            asn2()

        elif choice == '4':
            clear_screen()
            wayback()

        elif choice == '5':
            clear_screen()
            Offline_Subdomain_enum()

        elif choice == '6':
            clear_screen()
            websocket_scanner()
            
        elif choice == '7':
            clear_screen()
            websocket_scanner_old()   
            
        elif choice == '8':
            clear_screen()
            access_control()

        elif choice == '9':
            clear_screen()
            ipgen()

        elif choice == '10':
            clear_screen()
            open_port_checker()

        elif choice == '11':
            clear_screen()
            udp_tcp()

        elif choice == '12':
            clear_screen()
            dork_scanner()

        elif choice == '13':
            clear_screen()
            nslookup()

        elif choice == '14':
            clear_screen()
            tcp_ssl()

        elif choice == '15':
            clear_screen()
            dnskey()

        elif choice == '16':
            clear_screen()
            payloadhunter()

        elif choice == '17':
            clear_screen()
            payloadhunter2()

        elif choice == '18':
            clear_screen()
            zonewalk()

        else:
            print("Invalid option. Please try again.")
            time.sleep(2)
            continue

        randomshit("\nTask Completed Press Enter to Continue")
        input()

#=========== Enumaration scripts =================#
#===SUBDOmainS ENUM===#
def subdomain_enum():
    
    generate_ascii_banner("SUB DOmainS", "ENUM")

    def write_subs_to_file(subdomain, output_file):
        with open(output_file, 'a') as fp:
            fp.write(subdomain.replace("*.","") + '\n')

    def process_target(t, output_file, subdomains):
        global lock  # Declare lock as a global variable

        req = requests.get(f'https://crt.sh/?q=%.{t}&output=json')
        if req.status_code != 200:
            print(f'[*] Information available for {t}!')
            return

        for (key,value) in enumerate(req.json()):
            subdomain = value['name_value']
            with lock:
                write_subs_to_file(subdomain, output_file)
                subdomains.append(subdomain)

    def subdomain_enum_main():
        global lock  # Declare lock as a global variable

        subdomains = []
        target = ""

        while True:
            target_type = input("Enter '1' for file name or '2' for single IP/domain: ")
            if target_type == '1':
                file_name = input("Enter the file name containing a list of domains: ")
                try:
                    with open(file_name) as f:
                        target = f.readlines()
                    target = [x.strip() for x in target]
                    break
                except:
                    print("Error opening the file. Try again.")
            elif target_type == '2':
                target = input("Enter a single domain name or IP address: ")
                break
            else:
                print("Invalid input. Try again.")

        output_file = input("Enter a file to save the output to: ")

        num_threads = int(input("Enter the number of threads (1-255): "))
        if num_threads < 1 or num_threads > 255:
            print("Invalid number of threads. Please enter a value between 1 and 255.")
            return

        lock = threading.Lock()

        if isinstance(target, list):
            with ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = []
                for t in target:
                    futures.append(executor.submit(process_target, t, output_file, subdomains))

                for future in tqdm(futures, desc="Progress"):
                    future.result()
        else:
            process_target(target, output_file, subdomains)

        print(f"\n\n[**] Process is complete, {len(subdomains)} subdomains have been found and saved to the file.")

    subdomain_enum_main()

#===CASPER===# 
def casper():
    
    generate_ascii_banner("C.A.S.P.E.R", "")

    import warnings
    from urllib3.exceptions import InsecureRequestWarning
    import warnings
    import re
    import dns.resolver
    import socket
    import requests
    import time
    import os
    import ipaddress
    from concurrent.futures import ThreadPoolExecutor, as_completed

    # Suppress SSL warnings
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)

    # Configuration
    THREADS = 100
    SLEEP_BETWEEN_BATCHES = 0.5
    BATCH_SIZE = 500
    TIMEOUT = 7
    seen_pairs = set()
    VALID_DOMAIN_REGEX = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")

    class CSPProcessor:
        def __init__(self):
            self.visited_domains = set()
            self.resolver = dns.resolver.Resolver(configure=False)
            self.resolver.nameservers = ['8.8.8.8', '1.1.1.1']
            self.resolver.timeout = 2
            self.resolver.lifetime = 2

        def clean_domain(self, domain):
            """Clean domain by removing wildcards and trailing dots"""
            if not domain:
                return None
            domain = domain.lstrip("*.").rstrip(".")
            return domain.lower() if domain else None

        def is_valid_domain(self, domain):
            """Validate domain format"""
            return bool(VALID_DOMAIN_REGEX.match(domain)) if domain else False

        def get_ip(self, domain):
            """Resolve domain to IP with multiple fallback methods"""
            domain = self.clean_domain(domain)
            if not domain:
                return None

            try:
                # Try direct resolution first
                ip = socket.gethostbyname(domain)
                return ip
            except socket.gaierror:
                try:
                    # Try DNS resolver
                    answer = self.resolver.resolve(domain, 'A')
                    return answer[0].to_text()
                except:
                    # Fallback to root domain
                    root_domain = self.extract_root_domain(domain)
                    if root_domain != domain:
                        try:
                            return socket.gethostbyname(root_domain)
                        except:
                            try:
                                answer = self.resolver.resolve(root_domain, 'A')
                                return answer[0].to_text()
                            except:
                                return None
                    return None

        def extract_root_domain(self, subdomain):
            """Extract root domain from subdomain"""
            parts = subdomain.split('.')
            if len(parts) >= 2:
                return '.'.join(parts[-2:])
            return subdomain

        def get_csp_domains(self, domain):
            """Get all domains from CSP header with comprehensive parsing"""
            try:
                response = requests.get(
                    f"https://{domain}",
                    timeout=TIMEOUT,
                    verify=False,
                    allow_redirects=True,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                
                csp_header = response.headers.get("Content-Security-Policy", "")
                if not csp_header:
                    return set()

                domains = set()
                
                # Extract all domains from CSP directives
                directives = [d.strip() for d in csp_header.split(';') if d.strip()]
                
                for directive in directives:
                    # Skip empty directives
                    if not directive:
                        continue
                    
                    # Split into directive name and sources
                    parts = directive.split()
                    if len(parts) < 2:
                        continue
                    
                    # Process each source in the directive
                    for source in parts[1:]:
                        source = source.strip("'\"")
                        
                        # Skip special CSP keywords
                        if source in ['self', 'none', 'unsafe-inline', 'unsafe-eval',
                                    'strict-dynamic', 'report-sample', 'wasm-unsafe-eval']:
                            continue
                        
                        # Skip data URIs and other non-domain sources
                        if source.startswith(('data:', 'blob:', 'filesystem:', 'about:')):
                            continue
                        
                        # Handle 'self' special case
                        if source == 'self':
                            domains.add(domain)
                            continue
                        
                        # Extract domain from URL sources
                        if '://' in source:
                            try:
                                domain_part = source.split('://')[1].split('/')[0]
                                clean_domain = self.clean_domain(domain_part)
                                if clean_domain and self.is_valid_domain(clean_domain):
                                    domains.add(clean_domain)
                            except IndexError:
                                continue
                        # Handle wildcard domains
                        elif source.startswith('*.'):
                            clean_domain = self.clean_domain(source[2:])
                            if clean_domain and self.is_valid_domain(clean_domain):
                                domains.add(clean_domain)
                        # Regular domain
                        elif '.' in source:
                            clean_domain = self.clean_domain(source)
                            if clean_domain and self.is_valid_domain(clean_domain):
                                domains.add(clean_domain)

                return domains

            except (requests.Timeout, requests.RequestException, requests.ConnectionError):
                return set()

        def process_domain(self, domain, seen_pairs, counter, output_file, temp_file):
            """Process a single domain and its CSP domains"""
            domain = self.clean_domain(domain)
            if not domain or not self.is_valid_domain(domain) or domain in self.visited_domains:
                return

            self.visited_domains.add(domain)
            start_time = time.time()

            # Get all domains from CSP header
            csp_domains = self.get_csp_domains(domain)
            
            # Process each CSP domain
            for csp_domain in csp_domains:
                if (time.time() - start_time) >= TIMEOUT:
                    break

                csp_domain = self.clean_domain(csp_domain)
                if not csp_domain or csp_domain == domain:
                    continue

                # Get IP for the CSP domain
                ip = self.get_ip(csp_domain)
                if ip:
                    self.save_pair(csp_domain, ip, seen_pairs, counter, output_file, temp_file)
                else:
                    # Fallback to root domain
                    root_domain = self.extract_root_domain(csp_domain)
                    if root_domain != csp_domain:
                        root_ip = self.get_ip(root_domain)
                        if root_ip:
                            self.save_pair(csp_domain, root_ip, seen_pairs, counter, output_file, temp_file)
                            self.save_pair(root_domain, root_ip, seen_pairs, counter, output_file, temp_file)

        def save_pair(self, domain, ip, seen_pairs, counter, output_file, temp_file):
            """Save domain-ip pair if not already seen"""
            pair1 = (domain, ip)
            pair2 = (ip, domain)
            
            if pair1 not in seen_pairs and pair2 not in seen_pairs and domain != ip:
                # Save to local output file
                with open(output_file, 'a') as f:
                    f.write(f"{domain} {ip}\n")
                
                # Save to temporary batch file for upload
                with open(temp_file, 'a') as f:
                    f.write(f"{domain} {ip}\n")
                
                seen_pairs.update([pair1, pair2])
                counter[0] += 1

    def process_batch(batch, seen_pairs, batch_index, total_batches, output_file):
        """Process a batch of domains"""
        temp_file = f"domains{batch_index}.txt"
        open(temp_file, 'w').close()  # Create empty temp file
        
        domain_counter = [0]
        processor = CSPProcessor()

        print(f"[Batch {batch_index}/{total_batches}] Processing {len(batch)} targets...")

        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = [
                executor.submit(
                    processor.process_domain,
                    target,
                    seen_pairs,
                    domain_counter,
                    output_file,
                    temp_file
                )
                for target in batch
            ]
            
            try:
                for future in as_completed(futures, timeout=TIMEOUT):
                    try:
                        future.result()
                    except Exception:
                        pass
            except TimeoutError:
                pass

        # Upload the temp file if it contains data
        if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
            upload_file(temp_file)
        else:
            print("ℹ️ No domains found in this batch")

        # Clean up temp file
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception:
            pass

        duration = time.time() - time.time()
        print(f"[Batch {batch_index}/{total_batches}] Found {domain_counter[0]} new domains in {duration:.2f} seconds\n")

    def upload_file(path, max_retries=3):
        """Upload file to remote server"""
        url = "https://calm-snail-92.telebit.io/api/v2/upload"
        api_key = "GROUP_USERS"

        for attempt in range(1, max_retries + 1):
            try:
                print(f"🌐 Hold On {attempt})")
                with open(path, 'rb') as f:
                    files = {'file': f}
                    data = {'api_key': api_key}
                    response = requests.post(url, files=files, data=data, timeout=25)

                if response.status_code == 200:
                    print("✅")
                    return True
            except Exception:
                pass

            time.sleep(2)
        return False

    def c123():
        """Main execution function"""
        user_input = input("Enter a domain, IP, CIDR, or .txt file containing them: ").strip()
        if user_input.lower() in ['help', '?']:
            print("This script performs DNS enumeration and IP resolution.")
            return

        output_file = input("Enter the output file name (default 'domains_ips.txt'): ") or 'domains_ips.txt'
        
        # Clear existing output file
        open(output_file, 'w').close()
        
        targets_to_scan = []

        if os.path.isfile(user_input) and user_input.endswith('.txt'):
            print(f"📁 Reading targets from file: {user_input}")
            with open(user_input, 'r') as file:
                for line in file:
                    item = line.strip()
                    if not item:
                        continue
                    if "/" in item:
                        targets_to_scan.extend(expand_ip_range(item))
                    else:
                        try:
                            ipaddress.ip_address(item)
                            targets_to_scan.append(item)
                        except ValueError:
                            processor = CSPProcessor()
                            if processor.is_valid_domain(item):
                                targets_to_scan.append(item)
            targets_to_scan = list(set(targets_to_scan))
        elif "/" in user_input:
            print(f"📡 Scanning CIDR: {user_input}")
            targets_to_scan = expand_ip_range(user_input)
        else:
            try:
                ipaddress.ip_address(user_input)
                targets_to_scan = [user_input]
            except ValueError:
                processor = CSPProcessor()
                if processor.is_valid_domain(user_input):
                    targets_to_scan = [user_input]
                else:
                    print("⚠️ Invalid input - must be a domain, IP, CIDR, or .txt file")
                    return

        if not targets_to_scan:
            print("⚠️ No valid targets found to scan.")
            return

        print(f"🔍 Starting scan of {len(targets_to_scan)} targets...")
        
        # Process targets in batches
        total_batches = (len(targets_to_scan) + BATCH_SIZE - 1) // BATCH_SIZE
        for index in range(0, len(targets_to_scan), BATCH_SIZE):
            batch_number = (index // BATCH_SIZE) + 1
            batch = targets_to_scan[index:index + BATCH_SIZE]
            process_batch(batch, seen_pairs, batch_number, total_batches, output_file)
            time.sleep(SLEEP_BETWEEN_BATCHES)

        print(f"\n✅ All results saved to: {output_file}")

    def expand_ip_range(cidr):
        """Expand CIDR to individual IPs"""
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            return [str(ip) for ip in network.hosts()]
        except ValueError:
            return []

    try:
        c123()
        file_proccessing()
        time.sleep(2)
        clear_screen()
        print("Hit Enter to return to main menu")
    except FileNotFoundError as e:
        print(f"❌ File not found:")
    except ValueError as e:
        print(f"❌ Value error:")
    except Exception as e:
        print(f"❌ An unexpected error occurred:")
        print(f"❌ An error occurred:")
        file_proccessing()
        
#===ASN2===#
def asn2():
    
    import gzip
    import io
    
    generate_ascii_banner("ASN", "LOOKUP")

    # Function to download and search the TSV data
    def search_ip2asn_data(company_name):
        # Download the TSV file
        url = 'https://iptoasn.com/data/ip2asn-combined.tsv.gz'
        response = requests.get(url)
        
        # Check if download was successful
        if response.status_code == 200:
            # Wrap the content in a BytesIO object
            content = io.BytesIO(response.content)
            
            # Decompress the gzip file
            with gzip.open(content, 'rb') as f:
                # Decode the content using 'latin-1' encoding
                decoded_content = f.read().decode('latin-1')
                
                # Check for occurrences of the company name
                if company_name.lower() in decoded_content.lower():
                    # Split the content by lines and search for the company name
                    lines = decoded_content.split('\n')
                    result_lines = [line for line in lines if company_name.lower() in line.lower()]
                    return result_lines
                else:
                    return ["Company not found in the IP2ASN data."]
        else:
            return ["Failed to download IP2ASN data."]

    # Function to save results to a file
    def save_to_file(file_path, lines):
        with open(file_path, 'w') as f:
            for line in lines:
                f.write(line + '\n')
        print(f"Results saved to {file_path}")

    # main function
    def asn2_main():
        # Prompt the user for the company name
        company_name = input("Enter the company name to look up: ")
        
        # Search for the company name in the IP2ASN data
        result_lines = search_ip2asn_data(company_name)
        
        # Prompt the user to save the results to a file
        if result_lines:
            for line in result_lines:
                print(line)
            
            save_option = input("Do you want to save the results to a file? (yes/no): ")
            if save_option.lower() == 'yes':
                file_name = input("Enter the file name (without extension): ")
                file_path = os.path.join(os.getcwd(), f"{file_name}.txt")
                save_to_file(file_path, result_lines)
        else:
            print("No results found.")

    asn2_main()
    file_proccessing()

#===WAYBACK===#
def wayback():
    
    generate_ascii_banner("WAYBACK", "")

    from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
    from tqdm import tqdm

    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15A372 Safari/604.1",
        ]
    
    def strip_www(url):
        """
        Removes the 'www.' prefix from a URL if it exists.
        """
        if url.startswith("www."):
            return url[4:]  # Remove the first 4 characters ('www.')
        return url

    def get_input():
        choice = input("Enter '1' for domain name or '2' for file name: ").strip()
        if choice == '1':
            domain = input("Enter the domain name: ").strip()
            return [strip_www(domain)]
        elif choice == '2':
            filename = input("Enter the name of the file: ").strip()
            if os.path.exists(filename):
                with open(filename, 'r') as file:
                    # Strip 'www.' for all domains in the file
                    return [strip_www(line.strip()) for line in file.readlines()]
            print("File not found. Try again.")
        return get_input()

    def save_output(output):
        filename = input("Save the results no extention(e.g., 'archive_output'): ").strip()
        if not filename.endswith('.txt'):
            filename += '.txt'
        
        try:
            with open(filename, 'a') as file:
                for line in output:
                    file.write(f"{line}\n")
            print(f"Output saved to {filename}")
            print(f"Total domains saved: {len(output)}")
        except Exception as e:
            print(f"Error saving file: {e}")

    def download_txt(url):
        while True:
            # Select a random User-Agent
            user_agent = random.choice(USER_AGENTS)
            headers = {"User-Agent": user_agent}
            
            try:
                response = requests.get(url, headers=headers,)
                if response.status_code == 200:
                    print(response.status_code,"ok","fetching data...")
                    time.sleep(45)
                    return response.text
                else:
                    print(f"Unexpected status code {response.status_code} for {url} using User-Agent '{user_agent}'. Retrying in 3 seconds...")
            except requests.ConnectionError as e:
                print(f"Connection error for {url} using User-Agent '{user_agent}': {e}. Retrying in 3 seconds...")
            return None

    def clean_url(url):
        parsed_url = urlparse(url)
        filtered_params = {k: v for k, v in parse_qs(parsed_url.query).items() if not k.startswith('utm') and k != 's'}
        return urlunparse(parsed_url._replace(query=urlencode(filtered_params, doseq=True)))

    def fetch_archive(domain, domain_set):
        for prefix in ["www."]:
            url = f"https://web.archive.org/cdx/search?url={prefix}{domain}&matchType=prefix&collapse=urlkey&fl=original&filter=mimetype:text/html&filter=statuscode:200&output=txt"
            content = download_txt(url)
            if content and domain not in domain_set:
                domain_set.add(domain)
                return content
        return None

    def wayback_main():
        domains = get_input()
        domain_set = set()
        all_cleaned_urls = []

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_archive, domain, domain_set): domain for domain in domains}
            with tqdm(total=len(domains), desc="Processing Domains") as pbar:
                for future in as_completed(futures):
                    result = future.result()
                    if result:
                        for url in result.splitlines():
                            all_cleaned_urls.append(clean_url(url))
                    pbar.update(1)
        
        deduplicated_urls = sorted(set(all_cleaned_urls))  # Remove duplicates and sort the URLs
        #print(f"Found {len(domain_set)} unique domains.")
        return deduplicated_urls, len(domain_set)

    result, num_domains = wayback_main()
    if num_domains > 0:
        save_output(result)
    else:
        print('nothing found')

#===OFFLINE SUBDOmainS ENUM===#
def Offline_Subdomain_enum():
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    import certifi

    generate_ascii_banner("OFFLINE", "SUBENUM")

    def fetch_certificate(hostname):
        try:
            # Create SSL context using certifi CA certificates
            context = ssl.create_default_context(cafile=certifi.where())

            with ssl.create_connection((hostname, 443)) as sock:
                # Fetch SSL/TLS certificate
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    # Get SSL/TLS certificate
                    cert_der = ssock.getpeercert(binary_form=True)

            return cert_der
        except Exception as e:
            print(f"Error fetching certificate for {hostname}:")
            return None

    def extract_subdomains(cert_der, domain):
        try:
            # Parse the certificate
            cert = x509.load_der_x509_certificate(cert_der, default_backend())

            # Extract subdomains from SAN extension
            subdomains = []
            for ext in cert.extensions:
                if isinstance(ext.value, x509.SubjectAlternativeName):
                    for name in ext.value:
                        if isinstance(name, x509.DNSName):
                            subdomain = name.value
                            if not subdomain.startswith("*."):  # Filter out subdomains starting with .*
                                if subdomain == domain:
                                    subdomains.append(f"{subdomain} (check)")
                                else:
                                    subdomains.append(subdomain)

            return subdomains
        except Exception as e:
            print(f"Error extracting subdomains:")
            return []

    def fetch_subdomains(domain):
        cert_der = fetch_certificate(domain)
        if cert_der:
            return extract_subdomains(cert_der, domain)
        else:
            return []

    def fetch_subdomains_from_file(file_path):
        try:
            with open(file_path, 'r') as file:
                domains = [line.strip() for line in file.readlines()]
            subdomains = []
            with ThreadPoolExecutor(max_workers=10) as executor:
                for result in tqdm(executor.map(fetch_subdomains, domains), total=len(domains), desc="Fetching Subdomains"):
                    subdomains.extend(result)
            return subdomains
        except FileNotFoundError:
            print("File not found.")
            return []

    def save_subdomains_to_file(subdomains, output_file):
        try:
            with open(output_file, 'w') as file:
                for subdomain in subdomains:
                    file.write(subdomain + '\n')
            print(f"Subdomains saved to {output_file}")
        except Exception as e:
            print(f"Error saving subdomains to {output_file}:")

    def offline_sub_enum_main():
        try:
            print("Choose an option:")
            print("1. Enter a single domain")
            print("2. Enter Dommain list from .txt file")
            choice = input("Enter your choice (1 or 2): ").strip()

            if choice == '1':
                domain = input("Enter the domain: ").strip()
                subdomains = fetch_subdomains(domain)
            elif choice == '2':
                file_name = input("Enter the filename of the text file: ").strip()
                subdomains = fetch_subdomains_from_file(file_name)
            else:
                print("Invalid choice.")
                return

            if subdomains:
                output_file = input("Enter the output filename: ").strip()
                save_subdomains_to_file(subdomains, output_file)
            else:
                print("No subdomains found.")
        except KeyboardInterrupt:
            print("\nCtrl+C detected. Saving results, if any...")
            if subdomains:
                output_file = input("Enter the output filename: ").strip()
                save_subdomains_to_file(subdomains, output_file)
                print("Results saved.")
            else:
                print("No subdomains found. Exiting...")
            return

    offline_sub_enum_main()  

#===WEBSOCKET SCANNER===#
def websocket_scanner():
        
    generate_ascii_banner("WEBSOCKET", "SCANNER")

    import concurrent.futures
    import ipaddress
    import http.client
    import ssl
    from colorama import Fore, init
    import time
    import os
    import threading

    init(autoreset=True)
    print_lock = threading.Lock()

    def attempt_connection(ip, output_file_name):
        ports = [80, 443]  # Check both HTTP and HTTPS
        for port in ports:
            try:
                context = ssl.create_default_context() if port == 443 else None
                conn = http.client.HTTPSConnection(ip, port, timeout=3, context=context) if port == 443 else http.client.HTTPConnection(ip, port, timeout=3)
                conn.request("GET", "/")
                response = conn.getresponse()
                status_code = response.status
                server = response.getheader("Server", "Server info not found")

                with print_lock:
                    print(f"{Fore.CYAN}Checked {ip}:{port} - Status: {Fore.YELLOW}{status_code} {Fore.MAGENTA}| Server: {server}")

                if status_code in [200, 301, 401, 402, 403, 404, 405, 500]:
                    with open(output_file_name, 'a') as output_file:
                        output_file.write(f"{ip}:{port} - {status_code} | Server: {server}\n")
                    return True

            except Exception as e:
                with print_lock:
                    print(f"{Fore.RED}Failed to connect to {ip}:{port}: {e}")
        return False

    def establish_websocket_connection(ip_or_domain, output_file_name):
        try:
            if '/' in ip_or_domain:
                ip_network = ipaddress.IPv4Network(ip_or_domain, strict=False)
                ip_addresses = [str(ip) for ip in ip_network.hosts()]
            else:
                ip_addresses = [ip_or_domain]

            successful_connections = 0

            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(attempt_connection, ip, output_file_name) for ip in ip_addresses]

                for future in concurrent.futures.as_completed(futures):
                    if future.result():
                        successful_connections += 1

            with print_lock:
                if successful_connections > 0:
                    print(f"{Fore.GREEN}Saved {successful_connections} connections to {output_file_name}.")
                else:
                    print(f"{Fore.RED}No valid WebSocket responses found for {ip_or_domain}.")

            return successful_connections

        except ValueError as e:
            with print_lock:
                print(f"{Fore.RED}Invalid CIDR block {ip_or_domain}: {e}")
            return 0

    def k():
        ip_or_domain_list = []

        choice = input("Choose an option (1 file, 2 Manual input, 3 Hardcoded IPs): ")

        if choice == '1':
            file_name = input("Enter the file name containing a list of WebSocket domains or IPs: ")
            try:
                with open(file_name, 'r') as file:
                    ip_or_domain_list.extend(line.strip() for line in file)
            except FileNotFoundError:
                print("File not found.")
                return

        elif choice == '2':
            manual_input = input("Enter a list of WebSocket domains or IPs: ")
            ip_or_domain_list.extend(manual_input.split(','))

        elif choice == '3':
            print("Choose a group of hardcoded IPs:")
            print("1 - CLOUDFRONT_GLOBAL_IP_LIST")
            print("2 - CLOUDFRONT_REGIONAL_EDGE_IP_LIST_1")
            print("3 - CLOUDFRONT_REGIONAL_EDGE_IP_LIST_1_cont'd")
            print("4 - CLOUDFRONT_REGIONAL_EDGE_IP_LIST_2")
            print("5 - CLOUDFRONT_REGIONAL_EDGE_IP_LIST_3")
            print("6 - CLOUDFRIONAL_EDGE_IP_LIST_4")
            print("7 - CLOUDFLARE_IPV4_LIST_1")

            group_choice = input("Enter the group number: ")

            if group_choice == '1':
                ip_or_domain_list.extend(["13.32.0.0/15", "52.46.0.0/18", "52.84.0.0/15", "52.222.128.0/17",
                                        "54.182.0.0/16", "54.192.0.0/16", "54.230.0.0/16", "54.239.128.0/18",
                                        "54.239.192.0/19", "54.240.128.0/18", "204.246.164.0/22 204.246.168.0/22",
                                        "204.246.174.0/23","204.246.176.0/20","205.251.192.0/19","205.251.249.0/24",
                                        "205.251.250.0/2","205.251.252.0/23","205.251.254.0/24","216.137.32.0/19",])
            elif group_choice == '2':
                ip_or_domain_list.extend(["13.54.63.128/26", "13.59.250.0/26", "13.113.203.0/24", "13.124.199.0/24", 
                                        "13.228.69.0/24", "18.216.170.128/25", "34.195.252.0/24", "34.216.51.0/25", 
                                        "34.226.14.0/24", "34.232.163.208/29", "35.158.136.0/24", "35.162.63.192/26", 
                                        "35.167.191.128/26", "52.15.127.128/26", "52.47.139.0/24", "52.52.191.128/26", 
                                        "52.56.127.0/25", "52.57.254.0/24", "52.66.194.128/26", "52.78.247.128/26", 
                                        "52.199.127.192/26", "52.212.248.0/26", "52.220.191.0/26", "54.233.255.128/26", 
                                        "2.57.12.0/24", "2.255.190.0/23", "3.0.0.0/15", "3.2.0.0/24", "3.2.2.0/23", 
                                        "3.2.8.0/21", "3.2.48.0/23", "3.2.50.0/24", "3.3.6.0/23", "3.3.8.0/21", 
                                        "3.3.16.0/20", "3.5.32.0/22", "3.5.40.0/21", "3.5.48.0/21", "3.5.64.0/21", 
                                        "3.5.72.0/23", "3.5.76.0/22", "3.5.80.0/21", "3.5.128.0/19", "3.5.160.0/21", 
                                        "3.5.168.0/23", "3.5.208.0/22", "3.5.212.0/23", "3.5.216.0/22", "3.5.220.0/23", 
                                        "3.5.222.0/24", "3.5.224.0/23", "3.5.226.0/24", "3.5.228.0/22", "3.5.232.0/21", 
                                        "3.5.240.0/20", "3.6.0.0/15", "3.8.0.0/13", "3.16.0.0/13", "3.24.0.0/14", "3.28.0.0/15", 
                                        "3.33.35.0/24", "3.33.44.0/22", "3.33.128.0/17", "3.34.0.0/15", "3.36.0.0/14", "3.64.0.0/12", 
                                        "3.96.0.0/14", "3.101.0.0/16", "3.104.0.0/13", "3.112.0.0/14", "3.120.0.0/13", "3.128.0.0/12", 
                                        "3.144.0.0/13", "3.248.0.0/13", "5.22.145.0/24", "5.183.207.0/24", "13.32.1.0/24", "13.32.2.0/23", 
                                        "13.32.4.0/22", "13.32.8.0/21", "13.32.16.0/20", "13.32.40.0/22", "13.32.45.0/24", "13.32.46.0/23", 
                                        "13.32.48.0/21", "13.32.56.0/23", "13.32.59.0/24", "13.32.60.0/23", "13.32.62.0/24", "13.32.64.0/23", 
                                        "13.32.66.0/24", "13.32.68.0/22", "13.32.72.0/21", "13.32.80.0/21", "13.32.88.0/22", "13.32.92.0/23", 
                                        "13.32.98.0/23", "13.32.100.0/22", "13.32.104.0/23", "13.32.106.0/24", "13.32.108.0/22", "13.32.112.0/20",
                                        ])
            elif group_choice == '3':
                ip_or_domain_list.extend(["13.32.128.0/22", "13.32.132.0/24", "13.32.134.0/23", "13.32.136.0/23", 
                                        "13.32.140.0/24", "13.32.142.0/23", "13.32.146.0/24", "13.32.148.0/22", "13.32.152.0/22",
                                        "13.32.160.0/19", "13.32.192.0/20", "13.32.208.0/21", "13.32.224.0/23", "13.32.226.0/24", 
                                        "13.32.229.0/24", "13.32.230.0/23", "13.32.232.0/24", "13.32.240.0/23", "13.32.246.0/23",
                                        "13.32.249.0/24", "13.32.252.0/22", "13.33.0.0/19", "13.33.32.0/21", "13.33.40.0/23", "13.33.43.0/24", 
                                        "13.33.44.0/22", "13.33.48.0/20", "13.33.64.0/19", "13.33.96.0/22", "13.33.100.0/23", "13.33.104.0/21", "13.33.112.0/20", "13.33.128.0/21", "13.33.136.0/22", "13.33.140.0/23", "13.33.143.0/24",
                                        "13.33.144.0/21", "13.33.152.0/22", "13.33.160.0/21", "13.33.174.0/24", "13.33.184.0/23", "13.33.189.0/24", "13.33.197.0/24", "13.33.200.0/21", "13.33.208.0/21", "13.33.224.0/23", "13.33.229.0/24", "13.33.230.0/23", "13.33.232.0/21", "13.33.240.0/20", "13.35.0.0/21", "13.35.8.0/23", "13.35.11.0/24", "13.35.12.0/22", "13.35.16.0/21", "13.35.24.0/23", "13.35.27.0/24", "13.35.28.0/22", "13.35.32.0/21", "13.35.40.0/23", "13.35.43.0/24", "13.35.44.0/22", "13.35.48.0/21", "13.35.56.0/24", "13.35.63.0/24", "13.35.64.0/21", "13.35.73.0/24", "13.35.74.0/23", "13.35.76.0/22", "13.35.80.0/20", "13.35.96.0/19", "13.35.128.0/20", "13.35.144.0/21", "13.35.153.0/24", "13.35.154.0/23", "13.35.156.0/22", "13.35.160.0/21", "13.35.169.0/24", "13.35.170.0/23", "13.35.172.0/22", "13.35.176.0/21", "13.35.192.0/24", "13.35.200.0/21", "13.35.208.0/21", "13.35.224.0/20", "13.35.249.0/24", "13.35.250.0/23",
                                        "13.35.252.0/22", "13.36.0.0/14", "13.40.0.0/14", "13.48.0.0/13", "13.56.0.0/14", 
                                        "13.112.0.0/14", "13.124.0.0/14", "13.200.0.0/15", "13.208.0.0/13", "13.224.0.0/18", 
                                        "13.224.64.0/19", "13.224.96.0/21", "13.224.105.0/24", "13.224.106.0/23", "13.224.108.0/22", 
                                        "13.224.112.0/21", "13.224.121.0/24", "13.224.122.0/23", "13.224.124.0/22", "13.224.128.0/20", 
                                        "13.224.144.0/21", "13.224.153.0/24", "13.224.154.0/23", "13.224.156.0/22", "13.224.160.0/21", "13.224.185.0/24", "13.224.186.0/23", "13.224.188.0/22", "13.224.192.0/18", "13.225.0.0/21", "13.225.9.0/24", "13.225.10.0/23", "13.225.12.0/22", "13.225.16.0/21", "13.225.25.0/24", "13.225.26.0/23", "13.225.28.0/22", "13.225.32.0/19", "13.225.64.0/19", "13.225.96.0/21", "13.225.105.0/24", "13.225.106.0/23", "13.225.108.0/22", "13.225.112.0/21", "13.225.121.0/24", "13.225.122.0/23", "13.225.124.0/22", "13.225.128.0/21", "13.225.137.0/24", "13.225.138.0/23", "13.225.140.0/22", "13.225.144.0/20", "13.225.160.0/21", "13.225.169.0/24", "13.225.170.0/23", "13.225.172.0/22", "13.225.176.0/21", "13.225.185.0/24", "13.225.186.0/23", "13.225.188.0/22", "13.225.192.0/19", "13.225.224.0/20", "13.225.240.0/21", "13.225.249.0/24", "13.225.250.0/23", "13.225.252.0/22", "13.226.0.0/21", "13.226.9.0/24", "13.226.10.0/23", "13.226.12.0/22", "13.226.16.0/20", "13.226.32.0/20", "13.226.48.0/21", "13.226.56.0/24", "13.226.73.0/24", "13.226.77.0/24", "13.226.78.0/23", "13.226.84.0/24", "13.226.86.0/23", "13.226.88.0/21", "13.226.96.0/21", "13.226.112.0/22", "13.226.117.0/24", "13.226.118.0/23", "13.226.120.0/21", "13.226.128.0/17", "13.227.1.0/24", "13.227.2.0/23", "13.227.5.0/24", "13.227.6.0/23",
                                        "13.227.8.0/21", "13.227.16.0/22", "13.227.21.0/24", "13.227.22.0/23", "13.227.24.0/21", "13.227.32.0/20", "13.227.48.0/22", "13.227.53.0/24", "13.227.54.0/23", "13.227.56.0/21", "13.227.64.0/20", "13.227.80.0/22", "13.227.85.0/24", "13.227.86.0/23", "13.227.88.0/21", "13.227.96.0/19", "13.227.128.0/19", "13.227.160.0/22", "13.227.164.0/24", "13.227.168.0/21", "13.227.198.0/23", "13.227.208.0/22", "13.227.216.0/21", "13.227.228.0/24", "13.227.230.0/23", "13.227.240.0/20", "13.228.0.0/14", "13.232.0.0/13", "13.244.0.0/14", "13.248.0.0/19", "13.248.32.0/20", "13.248.48.0/21", "13.248.60.0/22", "13.248.64.0/21", "13.248.72.0/24", "13.248.96.0/19", "13.248.128.0/17", "13.249.0.0/17", "13.249.128.0/20", "13.249.144.0/24", "13.249.146.0/23", "13.249.148.0/22", "13.249.152.0/21", "13.249.160.0/24", "13.249.162.0/23", "13.249.164.0/22", "13.249.168.0/21", "13.249.176.0/20", 
                                        "13.249.192.0/19", "13.249.224.0/20", "13.249.241.0/24", "13.249.242.0/23", "13.249.245.0/24", "13.249.246.0/23", "13.249.248.0/21", "13.250.0.0/15", "15.152.0.0/16", "15.156.0.0/15", "15.158.0.0/21", "15.158.8.0/22", "15.158.13.0/24", "15.158.15.0/24", "15.158.16.0/23", "15.158.19.0/24", "15.158.21.0/24", "15.158.22.0/23", "15.158.24.0/23", "15.158.27.0/24", "15.158.28.0/22", "15.158.33.0/24", "15.158.34.0/23", "15.158.36.0/22", "15.158.40.0/21", "15.158.48.0/21", "15.158.56.0/23", "15.158.58.0/24", "15.158.60.0/22", "15.158.64.0/22", "15.158.68.0/23", "15.158.70.0/24", "15.158.72.0/21", "15.158.80.0/21", "15.158.88.0/23", 
                                        "15.158.91.0/24", "15.158.92.0/22", "15.158.96.0/22", "15.158.100.0/24", "15.158.102.0/23", "15.158.104.0/23", "15.158.107.0/24", "15.158.108.0/22", "15.158.112.0/20", "15.158.128.0/24", "15.158.131.0/24", "15.158.135.0/24", "15.158.138.0/23", "15.158.140.0/23", "15.158.142.0/24", "15.158.144.0/22", "15.158.148.0/23", "15.158.151.0/24", "15.158.152.0/24", "15.158.156.0/22", "15.158.160.0/23", "15.158.162.0/24"
                                            ])
            elif group_choice == '4':
                ip_or_domain_list.extend(["15.158.165.0/24", "15.158.166.0/23", "15.158.168.0/21", "15.158.176.0/22", "15.158.180.0/24", "15.158.182.0/24", "15.158.184.0/21", "15.160.0.0/15", "15.164.0.0/15", "15.168.0.0/16", "15.177.8.0/21", "15.177.16.0/20", "15.177.32.0/19", "15.177.66.0/23", "15.177.68.0/22", "15.177.72.0/21", "15.177.80.0/21", "15.177.88.0/22", "15.177.92.0/23", "15.177.94.0/24", "15.177.96.0/22", "15.181.0.0/17", "15.181.128.0/20", "15.181.144.0/22", "15.181.160.0/19", "15.181.192.0/19", 
                                        "15.181.224.0/20", "15.181.240.0/21", "15.181.248.0/22", "15.181.252.0/23", "15.181.254.0/24", "15.184.0.0/15", "15.188.0.0/16", "15.190.0.0/22", "15.190.16.0/20", "15.193.0.0/22", "15.193.4.0/23", "15.193.7.0/24", "15.193.8.0/23", "15.193.10.0/24", "15.197.4.0/22", "15.197.12.0/22", "15.197.16.0/22", "15.197.20.0/23", "15.197.24.0/22", "15.197.28.0/23", "15.197.32.0/21", "15.197.128.0/17", "15.206.0.0/15", "15.220.0.0/19", "15.220.32.0/21", "15.220.40.0/22", "15.220.48.0/20", "15.220.64.0/21", "15.220.80.0/20", "15.220.112.0/20", "15.220.128.0/18", "15.220.192.0/20", "15.220.216.0/21", "15.220.224.0/19", "15.221.7.0/24", "15.221.8.0/21", "15.221.16.0/20", "15.221.36.0/22", "15.221.40.0/21", "15.221.128.0/22", "15.222.0.0/15", "15.228.0.0/15", "15.236.0.0/15", "15.248.8.0/22", "15.248.16.0/22", "15.248.32.0/21", "15.248.40.0/22", "15.248.48.0/21", "15.253.0.0/16", "15.254.0.0/16", "16.12.0.0/23", "16.12.2.0/24", "16.12.4.0/23", "16.12.9.0/24", "16.12.10.0/23", "16.12.12.0/23", "16.12.14.0/24", "16.12.18.0/23", "16.12.20.0/24", "16.12.24.0/21", "16.12.32.0/21", "16.12.40.0/23", "16.16.0.0/16", "16.24.0.0/16", "16.50.0.0/15", "16.62.0.0/15", "16.162.0.0/15", "16.168.0.0/14", "18.34.32.0/19", "18.34.64.0/20", "18.34.240.0/20", "18.35.32.0/19", "18.35.64.0/20", "18.35.240.0/20", "18.60.0.0/15", "18.64.0.0/19", "18.64.32.0/21", "18.64.40.0/22", "18.64.44.0/24", 
                                        "18.64.75.0/24", "18.64.76.0/22", "18.64.80.0/20", "18.64.96.0/20", "18.64.112.0/21", "18.64.135.0/24", "18.64.136.0/21", "18.64.144.0/20", "18.64.160.0/19", "18.64.192.0/20", "18.64.208.0/23", "18.64.225.0/24", "18.64.226.0/23", "18.64.228.0/22", "18.64.232.0/21", "18.64.255.0/24", "18.65.0.0/17", "18.65.128.0/18", "18.65.192.0/19", "18.65.224.0/21", "18.65.232.0/22", "18.65.236.0/23", "18.65.238.0/24", "18.65.254.0/23", "18.66.0.0/16", "18.67.0.0/18", "18.67.64.0/19", "18.67.96.0/20", "18.67.112.0/22", "18.67.116.0/24", "18.67.147.0/24", "18.67.148.0/22", "18.67.152.0/21", "18.67.160.0/23", "18.67.237.0/24", "18.67.238.0/23", "18.67.240.0/20", "18.68.0.0/20", "18.68.16.0/23", "18.68.19.0/24", "18.68.20.0/24", "18.68.64.0/20", "18.68.80.0/24", "18.68.82.0/23", "18.68.130.0/23", "18.68.133.0/24", "18.68.134.0/23", "18.68.136.0/22", "18.88.0.0/18", "18.100.0.0/15", "18.102.0.0/16", "18.116.0.0/14", "18.130.0.0/16", "18.132.0.0/14", "18.136.0.0/16", "18.138.0.0/15", "18.140.0.0/14", "18.144.0.0/15", "18.153.0.0/16", "18.154.30.0/23", "18.154.32.0/20", "18.154.48.0/21", "18.154.56.0/22", "18.154.90.0/23", "18.154.92.0/22", "18.154.96.0/19", "18.154.128.0/20", "18.154.144.0/22", "18.154.148.0/23", "18.154.180.0/22", "18.154.184.0/21", "18.154.192.0/18", "18.155.0.0/21", "18.155.8.0/22", "18.155.12.0/23", "18.155.29.0/24", "18.155.30.0/23", "18.155.32.0/19", "18.155.64.0/21", "18.155.72.0/23", "18.155.89.0/24", "18.155.90.0/23", "18.155.92.0/22", 
                                        "18.155.96.0/19", "18.155.128.0/17", "18.156.0.0/14", "18.160.0.0/18", "18.160.64.0/19", "18.160.96.0/22", "18.160.100.0/23", "18.160.102.0/24", "18.160.133.0/24", "18.160.134.0/23", "18.160.136.0/21", "18.160.144.0/20", "18.160.160.0/19", "18.160.192.0/19", "18.160.224.0/20", "18.160.240.0/21", "18.160.248.0/22", "18.160.252.0/24", "18.161.12.0/22", "18.161.16.0/20", "18.161.32.0/19", "18.161.64.0/21", "18.161.87.0/24", "18.161.88.0/21", "18.161.96.0/19", "18.161.128.0/19", "18.161.160.0/20", "18.161.176.0/24", "18.161.192.0/19", "18.161.224.0/20", "18.161.240.0/21", "18.161.248.0/22", "18.162.0.0/15", "18.164.15.0/24", "18.164.16.0/20", "18.164.32.0/19", "18.164.64.0/18", "18.164.128.0/17", "18.165.0.0/17", "18.165.128.0/22", "18.165.132.0/23", "18.165.149.0/24", "18.165.150.0/23", "18.165.152.0/21", "18.165.160.0/22", "18.165.179.0/24", "18.165.180.0/22", "18.165.184.0/21", "18.165.192.0/20", "18.165.208.0/24", "18.165.225.0/24", "18.165.226.0/23", "18.165.228.0/22", "18.165.232.0/21", "18.165.255.0/24", "18.166.0.0/15", "18.168.0.0/14", "18.172.86.0/23", "18.172.88.0/21", "18.172.96.0/22", "18.172.100.0/24", "18.172.116.0/22", "18.172.120.0/21", "18.172.128.0/19", "18.172.160.0/20", "18.172.206.0/23", "18.172.208.0/20", "18.172.224.0/21", "18.172.232.0/22", "18.172.251.0/24", "18.172.252.0/22", "18.173.0.0/21", "18.173.8.0/23", "18.173.40.0/22", "18.173.44.0/24", "18.173.49.0/24", "18.173.50.0/24", "18.173.55.0/24", "18.173.56.0/23", "18.173.58.0/24", "18.173.62.0/23", "18.173.64.0/23", 
                                        "18.173.70.0/23", "18.173.72.0/23", "18.173.74.0/24", "18.173.76.0/22", "18.173.81.0/24", "18.173.82.0/23", "18.173.84.0/24", "18.173.91.0/24", "18.173.92.0/23", "18.173.95.0/24", "18.173.98.0/23", "18.173.105.0/24", "18.173.106.0/23", "18.175.0.0/16", "18.176.0.0/13", "18.184.0.0/15", "18.188.0.0/14", "18.192.0.0/13", "18.200.0.0/14", "18.216.0.0/13", "18.224.0.0/13", "18.236.0.0/15", "18.238.0.0/21", "18.238.8.0/22", "18.238.12.0/23", "18.238.14.0/24", "18.238.121.0/24", "18.238.122.0/23", "18.238.124.0/22", "18.238.128.0/21", "18.238.161.0/24", "18.238.162.0/23", "18.238.164.0/22", "18.238.168.0/21", "18.238.200.0/23", "18.238.203.0/24", "18.238.204.0/23", "18.238.207.0/24", "18.238.209.0/24", "18.238.211.0/24", "18.238.235.0/24", "18.239.230.0/24", "18.244.111.0/24", "18.244.112.0/21", "18.244.120.0/22", "18.244.124.0/23", "18.244.131.0/24", "18.244.132.0/22", "18.244.136.0/21", "18.244.144.0/23", "18.244.151.0/24", "18.244.152.0/21", "18.244.160.0/22", "18.244.164.0/23", "18.244.171.0/24", "18.244.172.0/22", "18.244.176.0/21", "18.244.184.0/23", "18.244.191.0/24", "18.244.192.0/21", "18.244.200.0/22", "18.244.204.0/23", "18.245.229.0/24", "18.245.251.0/24", "18.246.0.0/16", "18.252.0.0/15", "18.254.0.0/16", "23.92.173.0/24", "23.92.174.0/24", "23.130.160.0/24", "23.131.136.0/24", "23.142.96.0/24", "23.144.82.0/24", "23.156.240.0/24", "23.161.160.0/24", "23.183.112.0/23", "23.191.48.0/24", "23.239.241.0/24", "23.239.243.0/24", "23.249.168.0/24", "23.249.208.0/23", "23.249.215.0/24", 
                                        "23.249.218.0/23", "23.249.220.0/24", "23.249.222.0/23", "23.251.224.0/22", "23.251.232.0/21", "23.251.240.0/21", "23.251.248.0/22", "27.0.0.0/22", "31.171.211.0/24", "31.171.212.0/24", "31.223.192.0/20", "34.208.0.0/12", "34.240.0.0/12", "35.71.64.0/22", "35.71.72.0/22", "35.71.97.0/24", "35.71.100.0/24", "35.71.102.0/24", "35.71.105.0/24", "35.71.106.0/24", "35.71.111.0/24", "35.71.114.0/24", "35.71.118.0/23", "35.71.128.0/17", "35.72.0.0/13", "35.80.0.0/12", 
                                        "35.152.0.0/16", "35.154.0.0/15", "35.156.0.0/14", "35.160.0.0/13", "35.176.0.0/13", "37.221.72.0/22", "43.198.0.0/15", "43.200.0.0/13", "43.218.0.0/16", "43.247.34.0/24", "43.250.192.0/23", "44.224.0.0/11", "45.8.84.0/22", "45.10.57.0/24", "45.11.252.0/23", "45.13.100.0/22", "45.42.136.0/22", "45.42.252.0/22", "45.45.214.0/24", "45.62.90.0/23", "45.88.28.0/22", "45.91.255.0/24", "45.92.116.0/22", "45.93.188.0/24", "45.95.94.0/24", "45.95.209.0/24", "45.112.120.0/22", "45.114.220.0/22", "45.129.53.0/24", "45.129.54.0/23", "45.129.192.0/24", "45.136.241.0/24", "45.136.242.0/24", "45.138.17.0/24", "45.140.152.0/22", "45.143.132.0/24", "45.143.134.0/23", "45.146.156.0/24", "45.149.108.0/22", "45.152.134.0/23", "45.154.18.0/23", "45.155.99.0/24", "45.156.96.0/22", "45.159.120.0/22", "45.159.224.0/22", "45.223.12.0/24", "46.18.245.0/24", "46.19.168.0/23", "46.28.58.0/23", "46.28.63.0/24", "46.51.128.0/18", "46.51.192.0/20", "46.51.216.0/21", "46.51.224.0/19", "46.137.0.0/16", "46.227.40.0/22", "46.227.44.0/23", "46.227.47.0/24", "46.228.136.0/23", "46.255.76.0/24", "47.128.0.0/14", "50.18.0.0/16", "50.112.0.0/16", "50.115.212.0/23", "50.115.218.0/23", "50.115.222.0/23", "51.16.0.0/15", "51.149.8.0/24", "51.149.14.0/24", "51.149.250.0/23", "51.149.252.0/24", "52.8.0.0/13", "52.16.0.0/14", "52.24.0.0/13", "52.32.0.0/13", 
                                        "52.40.0.0/14", "52.46.0.0/21", "52.46.8.0/24", "52.46.25.0/24", "52.46.34.0/23", "52.46.36.0/24", "52.46.43.0/24", "52.46.44.0/24", "52.46.46.0/23", "52.46.48.0/23", "52.46.51.0/24", "52.46.53.0/24", "52.46.54.0/23", "52.46.56.0/23", "52.46.58.0/24", "52.46.61.0/24", "52.46.62.0/23", "52.46.64.0/20", "52.46.80.0/21", "52.46.88.0/22", "52.46.96.0/19", "52.46.128.0/19", "52.46.172.0/22", "52.46.180.0/22", "52.46.184.0/22", "52.46.192.0/19", "52.46.240.0/22", "52.46.249.0/24", "52.47.0.0/16", "52.48.0.0/14", "52.52.0.0/15", "52.56.0.0/14", "52.60.0.0/16", "52.62.0.0/15", "52.64.0.0/14", "52.68.0.0/15", "52.74.0.0/15", "52.76.0.0/14", "52.84.2.0/23", "52.84.4.0/22", "52.84.8.0/21", "52.84.16.0/20", "52.84.32.0/23", "52.84.35.0/24", "52.84.36.0/22", "52.84.40.0/21", "52.84.48.0/21", "52.84.56.0/23", "52.84.58.0/24", "52.84.60.0/22", "52.84.64.0/22", "52.84.68.0/23", "52.84.70.0/24", "52.84.73.0/24", "52.84.74.0/23", "52.84.76.0/22", "52.84.80.0/22", "52.84.84.0/24", "52.84.86.0/23", "52.84.88.0/21", "52.84.96.0/19", "52.84.128.0/22", "52.84.132.0/23", "52.84.134.0/24", "52.84.136.0/21", "52.84.145.0/24", "52.84.146.0/23", "52.84.148.0/22", "52.84.154.0/23", "52.84.156.0/22", "52.84.160.0/19", "52.84.192.0/21", "52.84.212.0/22", "52.84.216.0/23", "52.84.219.0/24", "52.84.220.0/22", "52.84.230.0/23", "52.84.232.0/22", "52.84.243.0/24", "52.84.244.0/22", "52.84.248.0/23", "52.84.251.0/24", "52.84.252.0/22", "52.85.0.0/20", "52.85.22.0/23", "52.85.24.0/21", "52.85.32.0/21", "52.85.40.0/22", "52.85.44.0/24", "52.85.46.0/23", "52.85.48.0/21", "52.85.56.0/22", "52.85.60.0/23", "52.85.63.0/24", "52.85.64.0/19", "52.85.96.0/22", "52.85.101.0/24", "52.85.102.0/23", "52.85.104.0/21", "52.85.112.0/20", "52.85.128.0/19", "52.85.160.0/21", "52.85.169.0/24", "52.85.170.0/23", "52.85.180.0/24", "52.85.183.0/24", "52.85.185.0/24", "52.85.186.0/23", "52.85.188.0/22", "52.85.192.0/19", "52.85.224.0/20", "52.85.240.0/22", "52.85.244.0/24", "52.85.247.0/24", "52.85.248.0/22", 
                                        "52.85.252.0/23", "52.85.254.0/24", "52.88.0.0/15", "52.92.0.0/22", "52.92.16.0/21", "52.92.32.0/21", "52.92.128.0/19", "52.92.160.0/21", "52.92.176.0/21", "52.92.192.0/21", "52.92.208.0/21", "52.92.224.0/21", "52.92.240.0/20", "52.93.110.0/24", "52.94.0.0/21", "52.94.8.0/24", "52.94.10.0/23", "52.94.12.0/22", "52.94.16.0/22", "52.94.20.0/24", "52.94.22.0/23", "52.94.24.0/23", "52.94.28.0/23", "52.94.30.0/24", "52.94.32.0/19", "52.94.64.0/22", "52.94.68.0/23", "52.94.72.0/21", "52.94.80.0/20", "52.94.96.0/20", "52.94.112.0/22", "52.94.120.0/21", "52.94.128.0/20", "52.94.144.0/23", "52.94.146.0/24", "52.94.148.0/22", "52.94.160.0/19", "52.94.204.0/22", "52.94.208.0/20", "52.94.224.0/20", "52.94.240.0/22", "52.94.252.0/22", "52.95.0.0/20", "52.95.16.0/21", "52.95.24.0/22", "52.95.28.0/24", "52.95.30.0/23", "52.95.34.0/23", "52.95.48.0/22", "52.95.56.0/22", "52.95.64.0/19", "52.95.96.0/22", "52.95.104.0/22", 
                                        "52.95.108.0/23", "52.95.111.0/24", "52.95.112.0/20", "52.95.128.0/20", "52.95.144.0/21", "52.95.152.0/22", "52.95.156.0/24", "52.95.160.0/19", "52.95.192.0/20", "52.95.212.0/22", "52.95.224.0/22", "52.95.228.0/23", "52.95.230.0/24", "52.95.235.0/24", "52.95.239.0/24", "52.95.240.0/22", "52.95.244.0/24", "52.95.246.0/23", "52.95.248.0/22", "52.95.252.0/23", "52.95.254.0/24", "52.119.41.0/24", "52.119.128.0/20", "52.119.144.0/21", "52.119.156.0/22", "52.119.160.0/19", "52.119.192.0/21", "52.119.205.0/24", "52.119.206.0/23", "52.119.210.0/23", "52.119.212.0/22", "52.119.216.0/21", "52.119.224.0/21", "52.119.232.0/22", "52.119.240.0/21", "52.119.248.0/23", "52.119.252.0/22", "52.124.130.0/24", "52.124.180.0/24", "52.124.199.0/24", "52.124.215.0/24", "52.124.219.0/24", "52.124.220.0/23", "52.124.225.0/24", "52.124.227.0/24", "52.124.228.0/22", "52.124.232.0/22", "52.124.237.0/24", "52.124.239.0/24", "52.124.240.0/21", "52.124.248.0/23", "52.124.251.0/24", "52.124.252.0/22", "52.128.43.0/24", "52.129.34.0/24", "52.129.64.0/24", "52.129.66.0/24", "52.129.100.0/22", "52.129.104.0/21", "52.144.61.0/24", "52.192.0.0/13", "52.208.0.0/13", "52.216.0.0/18", "52.216.64.0/21", "52.216.72.0/24", "52.216.76.0/22", "52.216.80.0/20", "52.216.96.0/19", "52.216.128.0/18", "52.216.192.0/22", "52.216.200.0/21", "52.216.208.0/20", "52.216.224.0/19", "52.217.0.0/16", "52.218.0.0/21", "52.218.16.0/20", "52.218.32.0/19", "52.218.64.0/22", "52.218.80.0/20", "52.218.96.0/19", "52.218.128.0/24", "52.218.132.0/22", "52.218.136.0/21", "52.218.144.0/24", "52.218.148.0/22", "52.218.152.0/21", "52.218.160.0/24", "52.218.168.0/21", "52.218.176.0/21", "52.218.184.0/22", "52.218.192.0/18", "52.219.0.0/20", "52.219.16.0/22", "52.219.24.0/22", "52.219.32.0/20", "52.219.56.0/21", "52.219.64.0/21", "52.219.72.0/22", "52.219.80.0/20", "52.219.96.0/19", "52.219.128.0/20", "52.219.144.0/22", "52.219.148.0/23", "52.219.152.0/21", "52.219.160.0/23", "52.219.164.0/22", "52.219.168.0/21", 
                                        "52.219.176.0/20", "52.219.192.0/21", "52.219.200.0/24", "52.219.202.0/23", "52.219.204.0/22", "52.219.208.0/22", "52.219.216.0/23", "52.219.218.0/24", "52.220.0.0/15", "52.222.128.0/18", "52.222.192.0/21", "52.222.200.0/22", "52.222.207.0/24", "52.222.211.0/24", "52.222.221.0/24", "52.222.222.0/23", "52.222.224.0/19", "52.223.0.0/17", "54.64.0.0/12", "54.92.0.0/17", "54.93.0.0/16", "54.94.0.0/15", "54.148.0.0/14", "54.153.0.0/16", "54.154.0.0/15", "54.168.0.0/14", "54.176.0.0/14", "54.180.0.0/15", "54.182.0.0/21", "54.182.134.0/23", "54.182.136.0/21", "54.182.144.0/20", "54.182.162.0/23", "54.182.166.0/23", "54.182.171.0/24", "54.182.172.0/22", "54.182.176.0/21", "54.182.184.0/23", "54.182.188.0/23", "54.182.190.0/24", "54.182.195.0/24", "54.182.196.0/22", "54.182.200.0/22", "54.182.205.0/24", "54.182.206.0/23", "54.182.209.0/24", "54.182.211.0/24", "54.182.215.0/24", "54.182.216.0/21", "54.182.224.0/22", "54.182.228.0/23", "54.182.235.0/24", "54.182.240.0/23", "54.182.246.0/23", "54.182.248.0/22", "54.182.252.0/23", "54.182.254.0/24", "54.183.0.0/16", "54.184.0.0/13", "54.192.0.0/21", "54.192.8.0/22", "54.192.13.0/24", "54.192.14.0/23", "54.192.16.0/21", "54.192.28.0/22", "54.192.32.0/21", "54.192.41.0/24", "54.192.42.0/23", "54.192.48.0/20", "54.192.64.0/18", "54.192.128.0/22", "54.192.136.0/22", "54.192.144.0/22", 
                                        "54.192.152.0/21", "54.192.160.0/20", "54.192.177.0/24", "54.192.178.0/23", "54.192.180.0/22", "54.192.184.0/23", "54.192.187.0/24", "54.192.188.0/23", "54.192.191.0/24", "54.192.192.0/21", "54.192.200.0/24", 
                                        "54.192.202.0/23", "54.192.204.0/22", "54.192.208.0/22", "54.192.216.0/21", "54.192.224.0/20", "54.192.248.0/21", "54.193.0.0/16", "54.194.0.0/15", "54.199.0.0/16", "54.200.0.0/14", "54.206.0.0/15", "54.212.0.0/14", "54.216.0.0/14", "54.220.0.0/16", "54.228.0.0/15", "54.230.0.0/22", "54.230.6.0/23", "54.230.8.0/21", "54.230.16.0/21", "54.230.28.0/22", "54.230.32.0/21", "54.230.40.0/22", "54.230.48.0/20", "54.230.64.0/22", "54.230.72.0/21", "54.230.80.0/20", "54.230.96.0/22", "54.230.100.0/24", "54.230.102.0/23", "54.230.104.0/21", "54.230.112.0/20", "54.230.129.0/24", "54.230.130.0/24", "54.230.136.0/22", "54.230.144.0/22", "54.230.152.0/23", "54.230.155.0/24", "54.230.156.0/22", "54.230.160.0/20", "54.230.176.0/21", "54.230.184.0/22", "54.230.188.0/23", "54.230.190.0/24", "54.230.192.0/20", "54.230.208.0/22", "54.230.216.0/21", "54.230.224.0/19", "54.231.0.0/24", "54.231.10.0/23", "54.231.16.0/22", "54.231.32.0/22", "54.231.36.0/24", "54.231.40.0/21", "54.231.48.0/20", "54.231.72.0/21", "54.231.80.0/21", "54.231.88.0/24", "54.231.96.0/19", "54.231.128.0/17", "54.232.0.0/15", "54.238.0.0/16", "54.239.2.0/23", "54.239.4.0/22", "54.239.8.0/21", "54.239.16.0/20", "54.239.32.0/21", "54.239.48.0/20", "54.239.64.0/21", "54.239.96.0/24", "54.239.98.0/23", "54.239.108.0/22", "54.239.113.0/24", "54.239.116.0/22", "54.239.120.0/21"],)
            elif group_choice == '5':  
                ip_or_domain_list.extend(["144.81.144.0/21", "144.81.152.0/24", "144.220.1.0/24", "144.220.2.0/23", "144.220.4.0/23", "144.220.11.0/24", "144.220.12.0/22", "144.220.16.0/21", "144.220.26.0/24", "144.220.28.0/23", "144.220.31.0/24", "144.220.37.0/24", "144.220.38.0/24", "144.220.40.0/24", "144.220.49.0/24", "144.220.50.0/23", "144.220.52.0/24", "144.220.55.0/24", "144.220.56.0/24", "144.220.59.0/24", "144.220.60.0/22", "144.220.64.0/22", "144.220.68.0/23", "144.220.72.0/22", "144.220.76.0/24", "144.220.78.0/23", "144.220.80.0/23", "144.220.82.0/24", "144.220.84.0/24", "144.220.86.0/23", "144.220.90.0/24", "144.220.92.0/23", "144.220.94.0/24", "144.220.99.0/24", "144.220.100.0/23", "144.220.103.0/24", "144.220.104.0/21", "144.220.113.0/24", "144.220.114.0/23", "144.220.116.0/23", "144.220.119.0/24", "144.220.120.0/23", "144.220.122.0/24", "144.220.125.0/24", "144.220.126.0/23", "144.220.128.0/21", "144.220.136.0/22", "144.220.140.0/23", "144.220.143.0/24", "146.66.3.0/24", "146.133.124.0/24", "146.133.127.0/24", "147.124.160.0/22", "147.124.164.0/23", "147.160.133.0/24", "147.189.18.0/23", "148.5.64.0/24", "148.5.74.0/24", "148.5.76.0/23", "148.5.80.0/24", "148.5.84.0/24", "148.5.86.0/23", "148.5.88.0/24", "148.5.93.0/24", "148.5.95.0/24", "148.163.131.0/24", "149.19.6.0/24", "149.20.11.0/24", "150.242.68.0/24", "151.148.32.0/22", "151.148.37.0/24", "151.148.38.0/23", "151.148.40.0/23", "152.129.248.0/23", "152.129.250.0/24", "155.46.191.0/24", "155.46.192.0/23", "155.46.195.0/24", "155.46.196.0/23", "155.46.212.0/24", "155.63.85.0/24", "155.63.86.0/24", "155.63.90.0/23", "155.63.208.0/23", "155.63.210.0/24", "155.63.213.0/24", "155.63.215.0/24", "155.63.216.0/23", "155.63.221.0/24", "155.63.222.0/23", "155.226.224.0/20", "155.226.254.0/24", "156.70.116.0/24", "157.53.255.0/24", "157.84.32.0/23", "157.84.40.0/23", "157.166.132.0/22", "157.166.212.0/24", "157.167.134.0/23", "157.167.136.0/21", "157.167.144.0/21", "157.167.152.0/23", "157.167.155.0/24", "157.167.156.0/24", "157.167.225.0/24", "157.167.226.0/23", "157.167.228.0/22", "157.167.232.0/23", "157.175.0.0/16", "157.241.0.0/16", "157.248.214.0/23", "157.248.216.0/22", "158.51.9.0/24", "158.51.65.0/24", "158.115.133.0/24", "158.115.141.0/24", "158.115.147.0/24", "158.115.151.0/24", "158.115.156.0/24", "159.60.0.0/20", 
                                        "159.60.192.0/19", "159.60.224.0/20", "159.60.240.0/21", "159.60.248.0/22", "159.112.232.0/24", "159.140.140.0/23", "159.140.144.0/24", "159.148.136.0/23", "160.202.21.0/24", "160.202.22.0/24", "161.38.196.0/22", "161.38.200.0/21", "161.69.8.0/21", "161.69.58.0/24", "161.69.75.0/24", "161.69.76.0/22", "161.69.94.0/23", "161.69.100.0/22", "161.69.105.0/24", "161.69.106.0/23", "161.69.109.0/24", "161.69.110.0/23", "161.69.124.0/24", "161.69.126.0/23", "161.129.19.0/24", "185.206.120.0/24", "161.188.128.0/20", "161.188.144.0/22", "161.188.148.0/23", "161.188.152.0/22", "161.188.158.0/23", "161.188.160.0/23", 
                                        "161.188.205.0/24", "161.199.67.0/24", "162.33.124.0/23", "162.33.126.0/24", "162.136.61.0/24", "162.212.32.0/24", "162.213.126.0/24", "162.213.205.0/24", "162.218.159.0/24", "162.219.9.0/24", "162.219.11.0/24", "162.219.12.0/24", "162.221.182.0/23", "162.247.163.0/24", "162.248.24.0/24", "162.249.117.0/24", "162.250.61.0/24", "162.250.63.0/24", "163.123.173.0/24", "163.123.174.0/24", "163.253.47.0/24", "164.55.233.0/24", "164.55.235.0/24", "164.55.236.0/23", "164.55.240.0/23", "164.55.243.0/24", "164.55.244.0/24", "164.55.255.0/24", "164.152.64.0/24", "164.153.130.0/23", "164.153.132.0/23", "164.153.134.0/24", "165.1.160.0/21", "165.1.168.0/23", "165.69.249.0/24", "165.84.210.0/24", "165.140.171.0/24", "165.225.100.0/23", "165.225.126.0/24", "167.88.51.0/24", "185.206.228.0/24", "168.87.180.0/22", "168.100.27.0/24", "168.100.65.0/24", "168.100.67.0/24", "168.100.68.0/22", "168.100.72.0/22", "168.100.76.0/23", "168.100.79.0/24", "168.100.80.0/21", "168.100.88.0/22", "168.100.93.0/24", "168.100.94.0/23", "168.100.97.0/24", "168.100.98.0/23", "168.100.100.0/22", "168.100.104.0/24", "168.100.107.0/24", "168.100.108.0/22", "168.100.113.0/24", "168.100.114.0/23", "168.100.116.0/22", "168.100.122.0/23", "168.100.164.0/24", "168.100.168.0/24", "168.149.242.0/23", "168.149.244.0/23", "168.149.247.0/24", "168.203.6.0/23", "168.238.100.0/24", 
                                        "169.150.104.0/24", "169.150.106.0/24", "169.150.108.0/22", "170.39.131.0/24", "170.39.141.0/24", "170.72.226.0/24", "170.72.228.0/22", "170.72.232.0/24", "170.72.234.0/23", "170.72.236.0/22", "170.72.240.0/22", "170.72.244.0/23", "170.72.252.0/22", "170.89.128.0/22", "170.89.132.0/23", "170.89.134.0/24", "170.89.136.0/22", "170.89.141.0/24", "170.89.144.0/24", "170.89.146.0/23", "170.89.149.0/24", "170.89.150.0/24", "170.89.152.0/23", "170.89.156.0/22", "170.89.160.0/24", "170.89.164.0/24", "170.89.173.0/24", "170.89.176.0/24", "170.89.178.0/24", "170.89.181.0/24", "170.89.182.0/23", "170.89.184.0/24", "170.89.189.0/24", "170.89.190.0/23", "170.114.16.0/20", "170.114.34.0/23", "170.114.37.0/24", "170.114.38.0/24", "170.114.40.0/23", "170.114.42.0/24", "170.114.44.0/24", "170.114.49.0/24", "170.114.53.0/24", "170.176.129.0/24", "170.176.135.0/24", "170.176.153.0/24", "170.176.154.0/24", "170.176.156.0/24", "170.176.158.0/24", "170.176.160.0/24", "170.176.200.0/24", "170.176.212.0/22", "170.176.216.0/23", "170.176.218.0/24", "170.176.220.0/22", "170.200.94.0/24", "172.86.224.0/24", "172.99.250.0/24", "173.199.36.0/23", "173.199.38.0/24", "173.199.56.0/23", "173.231.88.0/22", "173.240.165.0/24", "173.241.39.0/24", "173.241.44.0/23", "173.241.46.0/24", "173.241.82.0/24", "173.241.87.0/24", "173.241.94.0/24", "173.249.168.0/22", "174.34.225.0/24", "175.29.224.0/19", "175.41.128.0/17", "176.32.64.0/19", "176.32.96.0/20", "176.32.112.0/21", "176.32.120.0/22", "176.32.126.0/23", "176.34.0.0/16", "176.110.104.0/24", "176.116.14.0/24", "176.116.21.0/24", "176.124.224.0/24", "176.221.80.0/24", "176.221.82.0/23", "177.71.128.0/17", "177.72.240.0/21", "178.21.147.0/24", "178.21.148.0/24", "185.207.135.0/24", "178.213.75.0/24", 
                                        "178.236.0.0/20", "178.239.128.0/23", "178.239.130.0/24", "179.0.17.0/24", "182.54.135.0/24", "184.72.0.0/18", "184.94.214.0/24", "184.169.128.0/17", "185.7.73.0/24", "185.20.4.0/24", "185.31.204.0/22", "185.36.216.0/22", "185.37.37.0/24", "185.37.39.0/24", "185.38.134.0/24", "185.39.10.0/24", "185.43.192.0/22", "185.44.176.0/24", "185.48.120.0/22", 
                                        "185.49.132.0/23", "185.53.16.0/22", "185.54.72.0/22", "185.54.124.0/24", "185.54.126.0/24", "185.55.188.0/24", "185.55.190.0/23", "185.57.216.0/24", "185.57.218.0/24", "185.64.6.0/24", "185.64.73.0/24", "185.66.202.0/23", "185.68.58.0/23", "185.69.1.0/24", "185.75.61.0/24", "185.75.62.0/23", "185.79.75.0/24", "185.83.20.0/22", "185.88.184.0/23", "185.88.186.0/24", "185.95.174.0/24", "185.97.10.0/24", "185.98.156.0/24", "185.98.159.0/24", "185.107.197.0/24", "185.109.132.0/22", "185.118.109.0/24", "185.119.223.0/24", "185.120.172.0/22", "185.121.140.0/23", "185.121.143.0/24", "185.122.214.0/24", "185.127.28.0/24", "185.129.16.0/23", "185.133.70.0/24", "185.134.79.0/24", "185.135.128.0/24", "185.137.156.0/24", "185.143.16.0/24", "185.143.236.0/24", "185.144.16.0/24", "185.144.18.0/23", "185.144.236.0/24", "185.145.38.0/24", "185.146.155.0/24", "185.150.179.0/24", "185.151.47.0/24", 
                                        "185.166.140.0/22", "185.169.27.0/24", "185.170.188.0/23", "185.172.153.0/24", "185.172.155.0/24", "185.175.91.0/24", "185.186.212.0/24", "185.187.116.0/22", "185.195.0.0/22", "185.195.148.0/24", "185.210.156.0/24", "185.212.105.0/24", "185.212.113.0/24", "185.214.22.0/23", "185.215.115.0/24", "185.219.146.0/23", "185.221.84.0/24", "185.225.252.0/24", "185.225.254.0/23", "185.226.166.0/24", "185.232.99.0/24", "185.235.38.0/24", "185.236.142.0/24", "185.237.5.0/24", "185.237.6.0/23", "185.253.9.0/24", "185.255.32.0/22", "185.255.54.0/24", "188.72.93.0/24", "188.95.140.0/23", "188.95.142.0/24", "188.116.35.0/24", "188.172.137.0/24", "188.172.138.0/24", "188.209.136.0/22", "188.241.223.0/24", "188.253.16.0/20", "191.101.94.0/24", "191.101.242.0/24", "192.35.158.0/24", "192.42.69.0/24", "192.64.71.0/24", "192.71.84.0/24", "192.71.255.0/24", "192.80.240.0/24", "192.80.242.0/24", "192.80.244.0/24", "192.81.98.0/24", "192.84.23.0/24", "192.84.38.0/24", "192.84.231.0/24", "192.101.70.0/24", "192.111.5.0/24", "192.111.6.0/24", "192.118.71.0/24", "192.132.1.0/24", "192.151.28.0/23", "192.152.132.0/23", "192.153.76.0/24", "192.161.151.0/24", "192.161.152.0/24", "192.161.157.0/24", "192.175.1.0/24", "192.175.3.0/24", "192.175.4.0/24", "192.184.67.0/24", "192.184.69.0/24", "192.184.70.0/23", "192.190.135.0/24", "192.190.153.0/24", "192.197.207.0/24", "192.206.0.0/24", "192.206.146.0/23", "192.206.206.0/23", "192.210.30.0/23", "192.225.99.0/24", "192.230.237.0/24", "192.245.195.0/24", "193.0.181.0/24", "193.3.28.0/24", "193.3.160.0/24", "193.9.122.0/24", "193.16.22.0/24", "193.17.68.0/24", "193.24.42.0/23", "193.25.48.0/24", "193.25.51.0/24", "193.25.52.0/23", "193.25.54.0/24", "193.25.60.0/22", "193.30.161.0/24", "193.31.111.0/24", "193.33.137.0/24", "193.35.157.0/24", "193.37.39.0/24", "193.37.132.0/24", "193.39.114.0/24", "193.47.187.0/24", "193.57.172.0/24", "193.84.26.0/24", "193.100.64.0/24", "193.104.169.0/24", "193.105.212.0/24", "193.107.65.0/24", "193.110.146.0/24", "193.111.200.0/24", "193.131.114.0/23", "193.138.90.0/24", "193.150.164.0/24", "193.151.92.0/24", "193.151.94.0/24", "193.160.155.0/24", "193.176.54.0/24", "193.200.30.0/24", "193.200.156.0/24", "193.207.0.0/24", "193.219.118.0/24", "193.221.125.0/24", "193.227.82.0/24", "193.234.120.0/22", "193.239.162.0/23", "193.239.236.0/24", "193.243.129.0/24", "194.5.67.0/24", "194.5.147.0/24", "194.29.54.0/24", "194.29.58.0/24", 
                                        "194.30.175.0/24", "194.33.184.0/24", "194.42.96.0/23", "194.42.104.0/23", "194.53.200.0/24", "194.99.96.0/23", "194.104.235.0/24", "194.140.230.0/24", "194.165.43.0/24", "194.176.117.0/24", "194.195.101.0/24", "194.230.56.0/24", "194.247.26.0/23", "195.8.103.0/24", "195.42.240.0/24", "195.46.38.0/24", "195.60.86.0/24", "195.69.163.0/24", "195.74.60.0/24", "195.82.97.0/24", "195.85.12.0/24", "195.88.213.0/24", "195.88.246.0/24", "195.93.178.0/24", "195.191.165.0/24", "195.200.230.0/23", "195.234.155.0/24", "195.244.28.0/24", "195.245.230.0/23", "198.99.2.0/24", "198.137.150.0/24", "198.154.180.0/23", "198.160.151.0/24", "198.169.0.0/24", "198.176.120.0/23", "198.176.123.0/24", "198.176.124.0/23", "198.176.126.0/24", "198.183.226.0/24", "198.202.176.0/24", "198.204.13.0/24", "198.207.147.0/24", "198.212.50.0/24", "198.251.128.0/18", "198.251.192.0/19", "198.251.224.0/21", "199.43.186.0/24", "199.47.130.0/23", "199.59.243.0/24", "199.65.20.0/22", "199.65.24.0/23", "199.65.26.0/24", "199.65.242.0/24", "199.65.245.0/24", "199.65.246.0/24", "199.65.249.0/24", "199.65.250.0/24", "199.65.252.0/23", "199.68.157.0/24", "199.85.125.0/24", "199.87.145.0/24", "199.91.52.0/23", "199.115.200.0/24", "199.127.232.0/22", 
                                        "199.165.143.0/24", "199.187.168.0/22", "199.192.13.0/24", "199.196.235.0/24", "199.250.16.0/24", "199.255.32.0/24", "199.255.192.0/22", "199.255.240.0/24", "202.8.25.0/24", "202.44.120.0/23", "202.44.127.0/24", "202.45.131.0/24", "202.50.194.0/24", "202.52.43.0/24", "202.92.192.0/23", "202.93.249.0/24", "202.128.99.0/24", "202.160.113.0/24", "202.160.115.0/24", "202.160.117.0/24", "202.160.119.0/24", "202.173.24.0/24", "202.173.26.0/23", "202.173.31.0/24", "203.12.218.0/24", "203.20.242.0/23", "203.27.115.0/24", "203.27.226.0/23", "203.55.215.0/24", "203.57.88.0/24", "203.83.220.0/22", "203.175.1.0/24", "203.175.2.0/23", "203.210.75.0/24", "204.10.96.0/21", "204.11.174.0/23", "204.15.172.0/24", "204.15.215.0/24", "204.27.244.0/24", "204.48.63.0/24", "204.77.168.0/24", "204.90.106.0/24", "204.110.220.0/23", "204.110.223.0/24", "204.154.231.0/24", "204.236.128.0/18", "204.239.0.0/24", "204.246.160.0/22", "204.246.166.0/24", "204.246.169.0/24", "204.246.175.0/24", "204.246.177.0/24", "204.246.178.0/24", "204.246.180.0/23", "204.246.182.0/24", "204.246.187.0/24", "204.246.188.0/22", "205.147.81.0/24", "205.157.218.0/23", "205.166.195.0/24", "205.201.44.0/23", "205.220.188.0/24", "205.235.121.0/24", "205.251.192.0/21",
                                        "205.251.200.0/24", "205.251.203.0/24", "205.251.206.0/23", "205.251.212.0/23", "205.251.216.0/24", "205.251.218.0/23", "205.251.222.0/23", "205.251.224.0/21", "205.251.232.0/22", "205.251.240.0/22", "205.251.244.0/23", "205.251.247.0/24", "205.251.248.0/23", "205.251.251.0/24", "205.251.253.0/24", "206.108.41.0/24", "206.130.88.0/23", "206.166.248.0/23", "206.195.217.0/24", "206.195.218.0/24", "206.195.220.0/24", "206.198.37.0/24", "206.198.131.0/24", "206.225.200.0/23", "206.225.203.0/24", "206.225.217.0/24", "206.225.219.0/24", "207.2.117.0/24", "207.2.118.0/23", "207.34.11.0/24", "207.45.79.0/24", "207.90.252.0/23", "207.167.92.0/22", "207.167.126.0/23", "207.171.160.0/19", "207.189.185.0/24", "207.202.17.0/24", "207.202.18.0/24", "207.202.20.0/24", "207.207.176.0/22", "207.230.151.0/24", "207.230.156.0/24", "208.56.44.0/23", "208.56.47.0/24", "208.56.48.0/20", "208.71.22.0/24", "208.71.106.0/24", "208.71.210.0/24", "208.71.245.0/24", "208.73.7.0/24", "208.81.250.0/24", "208.82.220.0/22", "208.89.247.0/24", "208.90.238.0/24", "208.91.36.0/23", "208.95.53.0/24", "208.127.200.0/21", "209.51.32.0/21", "209.54.160.0/19", "209.94.75.0/24", "209.126.65.0/24", "209.127.220.0/24", "209.160.100.0/22", "209.163.96.0/24", "209.169.228.0/24", "209.169.242.0/24", "209.182.220.0/24", "209.222.82.0/24", "211.44.103.0/24", "212.4.240.0/22", "212.8.241.0/24", "212.19.235.0/24", "212.19.236.0/24", "212.104.208.0/24", "212.192.221.0/24", "213.5.226.0/24", "213.109.176.0/22", "213.170.156.0/24", 
                                        "213.170.158.0/24", "213.217.29.0/24", "216.9.204.0/24", "216.24.45.0/24", "216.73.153.0/24", "216.73.154.0/23", "216.74.122.0/24", "216.75.96.0/22", "216.75.104.0/21", "216.99.220.0/24", "216.115.17.0/24", "216.115.20.0/24", "216.115.23.0/24", "216.120.142.0/24", "216.120.187.0/24", "216.122.176.0/22", "216.137.32.0/24", "216.137.34.0/23", "216.137.36.0/22", "216.137.40.0/21", "216.137.48.0/21", "216.137.56.0/23", "216.137.58.0/24", "216.137.60.0/23", "216.137.63.0/24", "216.147.0.0/23", "216.147.3.0/24", "216.147.4.0/22", "216.147.9.0/24", "216.147.10.0/23", "216.147.12.0/23", "216.147.15.0/24", "216.147.16.0/23", "216.147.19.0/24", "216.147.20.0/23", "216.147.23.0/24", "216.147.24.0/22", "216.147.29.0/24", "216.147.30.0/23", "216.147.32.0/23", "216.157.133.0/24", "216.157.139.0/24", "216.169.145.0/24", "216.170.100.0/24", "216.182.236.0/23", "216.198.2.0/23", "216.198.17.0/24", 
                                        "216.198.18.0/24", "216.198.33.0/24", "216.198.34.0/23", "216.198.36.0/24", "216.198.49.0/24", "216.211.162.0/24", "216.219.113.0/24", "216.238.188.0/23", "216.238.190.0/24", "216.241.208.0/20", "217.8.118.0/24", "217.117.65.0/24", "217.117.71.0/24", "217.117.76.0/24", "217.119.96.0/24", "217.119.98.0/24", "217.119.104.0/23", "217.169.73.0/24", "218.33.0.0/18" ],)
            elif group_choice == '6':  
                ip_or_domain_list.extend(["54.239.130.0/23", "54.239.132.0/23", "54.239.135.0/24", "54.239.142.0/23", "54.239.152.0/23", "54.239.158.0/23", "54.239.162.0/23", "54.239.164.0/23", "54.239.168.0/23", "54.239.171.0/24", "54.239.172.0/24", "54.239.174.0/23", "54.239.180.0/23", "54.239.186.0/24", "54.239.192.0/24", "54.239.195.0/24", "54.239.200.0/24", "54.239.204.0/22", "54.239.208.0/21", "54.239.216.0/23", "54.239.219.0/24", "54.239.220.0/23", "54.239.223.0/24", "54.240.0.0/21", "54.240.16.0/24", "54.240.24.0/22", "54.240.50.0/23", "54.240.52.0/22", "54.240.56.0/21", "54.240.80.0/20", "54.240.96.0/20", "54.240.112.0/21", "54.240.129.0/24", "54.240.130.0/23", "54.240.160.0/23", "54.240.166.0/23", "54.240.168.0/21", "54.240.184.0/21", "54.240.192.0/21", "54.240.200.0/24", "54.240.202.0/24", "54.240.204.0/22", "54.240.208.0/20", "54.240.225.0/24", "54.240.226.0/23", "54.240.228.0/22", "54.240.232.0/22", "54.240.244.0/22", "54.240.248.0/21", "54.241.0.0/16", "54.244.0.0/14", "54.248.0.0/13", "57.180.0.0/14", "58.181.95.0/24", "62.133.34.0/24", "63.32.0.0/14", "63.140.32.0/22", "63.140.36.0/23", "63.140.48.0/22", "63.140.52.0/24", "63.140.55.0/24", "63.140.56.0/23", "63.140.61.0/24", "63.140.62.0/23", "63.246.112.0/24", "64.35.162.0/24", "64.45.129.0/24", "64.45.130.0/23", "64.52.111.0/24", "64.56.212.0/24", "64.65.61.0/24", "64.69.212.0/24", "64.69.223.0/24", "64.186.3.0/24", "64.187.128.0/20", "64.190.110.0/24", "64.190.237.0/24", "64.207.194.0/24", "64.207.196.0/24", "64.207.198.0/23", "64.207.204.0/23", "64.234.115.0/24", "64.238.2.0/24", "64.238.5.0/24", "64.238.6.0/24", "64.238.14.0/24", "64.252.65.0/24", "64.252.70.0/23", "64.252.72.0/21", "64.252.80.0/21", "64.252.88.0/23", "64.252.98.0/23", "64.252.100.0/22", "64.252.104.0/21", "64.252.112.0/23", "64.252.114.0/24", "64.252.118.0/23", "64.252.120.0/22", "64.252.124.0/24", "64.252.129.0/24", "64.252.130.0/23", "64.252.132.0/22", "64.252.136.0/21", "64.252.144.0/23", "64.252.147.0/24", "64.252.148.0/23", "64.252.151.0/24", "64.252.152.0/24", "64.252.154.0/23", "64.252.156.0/24", "64.252.159.0/24", "64.252.161.0/24", "64.252.162.0/23", "64.252.164.0/24", "64.252.166.0/23", "64.252.168.0/22", "64.252.172.0/23", "64.252.175.0/24", "64.252.176.0/22", "64.252.180.0/24", "64.252.182.0/23", "64.252.185.0/24", "64.252.186.0/23", "64.252.188.0/23", "64.252.190.0/24", "65.0.0.0/14", "65.8.0.0/23", "65.8.2.0/24", "65.8.4.0/22", "65.8.8.0/23", "65.8.11.0/24", "65.8.12.0/24", "65.8.14.0/23", "65.8.16.0/20", "65.8.32.0/19", "65.8.64.0/20", "65.8.80.0/21", "65.8.88.0/22", "65.8.92.0/23", "65.8.94.0/24", "65.8.96.0/20", "65.8.112.0/21", "65.8.120.0/22", "65.8.124.0/23", "65.8.129.0/24", "65.8.130.0/23", "65.8.132.0/22", "65.8.136.0/22", "65.8.140.0/23", "65.8.142.0/24", "65.8.146.0/23", "65.8.148.0/23", "65.8.150.0/24", "65.8.152.0/23", "65.8.154.0/24", "65.8.158.0/23", "65.8.160.0/19", "65.8.192.0/18", "65.9.4.0/24", "65.9.6.0/23", "65.9.9.0/24", "65.9.11.0/24", "65.9.14.0/23", "65.9.17.0/24", "65.9.19.0/24", "65.9.20.0/22", "65.9.24.0/21", "65.9.32.0/19", "65.9.64.0/19", "65.9.96.0/20", "65.9.112.0/23", "65.9.129.0/24", "65.9.130.0/23", "65.9.132.0/22", "65.9.136.0/21", "65.9.144.0/20", "65.9.160.0/19", "65.20.48.0/24", "65.37.240.0/24", "65.110.52.0/23", "65.110.54.0/24", "66.22.176.0/24", "66.22.190.0/24", "66.37.128.0/24", "66.51.208.0/24", "66.51.210.0/23", "66.51.212.0/22", "66.51.216.0/23", "66.54.74.0/23", "66.81.8.0/24", "66.81.227.0/24", "66.81.241.0/24", "66.117.20.0/24", "66.117.22.0/23", "66.117.24.0/23", "66.117.26.0/24", "66.117.30.0/23", "66.129.247.0/24", "66.129.248.0/24", "66.159.226.0/24", "66.159.230.0/24", "66.178.130.0/24", "66.178.132.0/23", "66.178.134.0/24", "66.178.136.0/23", "66.178.139.0/24", "66.182.132.0/23", "66.187.204.0/23", "66.206.173.0/24", "66.232.20.0/23", "66.235.151.0/24", "66.235.152.0/22", "67.20.60.0/24", "67.199.239.0/24", "67.219.241.0/24", "67.219.247.0/24", "67.219.250.0/24", "67.220.224.0/19", "67.221.38.0/24", "67.222.249.0/24", "67.222.254.0/24", "67.226.222.0/23", "68.64.5.0/24", "68.66.112.0/20", "68.70.127.0/24", "69.10.24.0/24", "69.58.24.0/24", "69.59.247.0/24", "69.59.248.0/24", "69.59.250.0/23", "69.64.150.0/24", "69.64.152.0/24", "69.72.44.0/22", "69.80.226.0/23", "69.94.8.0/23", "69.166.42.0/24", "69.169.224.0/20", "70.132.0.0/20", "70.132.16.0/22", "70.132.20.0/23", "70.132.23.0/24", "70.132.24.0/23", "70.132.27.0/24", "70.132.28.0/22", "70.132.32.0/21", "70.132.40.0/24", "70.132.42.0/23", "70.132.44.0/24", "70.132.46.0/24", "70.132.48.0/22", "70.132.52.0/23", "70.132.55.0/24", "70.132.58.0/23", "70.132.60.0/22", "70.224.192.0/18", "70.232.64.0/20", "70.232.80.0/21", "70.232.88.0/22", "70.232.96.0/20", "70.232.112.0/21", "70.232.120.0/22", "71.141.0.0/21", "71.152.0.0/22", "71.152.4.0/23", "71.152.7.0/24", "71.152.8.0/24", "71.152.10.0/23", "71.152.13.0/24", "71.152.14.0/23", "71.152.16.0/21", "71.152.24.0/22", 
                                        "71.152.28.0/24", "71.152.30.0/23", "71.152.33.0/24", "71.152.35.0/24", "71.152.36.0/22", "71.152.40.0/23", "71.152.43.0/24", "71.152.46.0/23", "71.152.48.0/22", "71.152.53.0/24", "71.152.55.0/24", "71.152.56.0/22", "71.152.61.0/24", "71.152.62.0/23", "71.152.64.0/21", "71.152.72.0/22", "71.152.76.0/23", "71.152.79.0/24", "71.152.80.0/21", "71.152.88.0/22", "71.152.92.0/24", "71.152.94.0/23", "71.152.96.0/22", "71.152.100.0/24", "71.152.102.0/23", "71.152.105.0/24", "71.152.106.0/23", "71.152.108.0/23", "71.152.110.0/24", "71.152.112.0/21", "71.152.122.0/23", "71.152.124.0/24", "71.152.126.0/23", "72.1.32.0/21", "72.13.121.0/24", "72.13.124.0/24", "72.18.76.0/23", "72.18.222.0/24", "72.21.192.0/19", "72.41.0.0/20", "72.46.77.0/24", "72.167.168.0/24", "74.80.247.0/24", "74.116.145.0/24", "74.116.147.0/24", "74.117.148.0/24", "74.118.105.0/24", "74.118.106.0/23", "74.200.120.0/24", "74.221.129.0/24", "74.221.130.0/24", "74.221.133.0/24", "74.221.135.0/24", "74.221.137.0/24", "74.221.139.0/24", "74.221.141.0/24", "75.2.0.0/17", "75.104.19.0/24", "76.76.17.0/24", "76.76.19.0/24", "76.76.21.0/24", "76.223.0.0/17", "76.223.128.0/22", "76.223.132.0/23", "76.223.160.0/22", "76.223.164.0/23", "76.223.166.0/24", "76.223.172.0/22", "76.223.176.0/21", "76.223.184.0/22", "76.223.188.0/23", "76.223.190.0/24", "77.73.208.0/23", "78.108.124.0/23", "79.125.0.0/17", "79.143.156.0/24", "80.210.95.0/24", "81.20.41.0/24", "81.90.143.0/24", "82.145.126.0/24", "82.192.96.0/23", "82.192.100.0/23", "82.192.108.0/23", "83.97.100.0/22", "83.137.245.0/24", "83.147.240.0/22", "83.151.192.0/23", "83.151.194.0/24", "84.254.134.0/24", "85.92.101.0/24", "85.113.84.0/24", "85.113.88.0/24", "85.158.142.0/24", "85.194.254.0/23", "85.236.136.0/21", "87.236.67.0/24", "87.238.80.0/21", "87.238.140.0/24", "88.202.208.0/23", "88.202.210.0/24", "88.212.156.0/22", "89.37.140.0/24", "89.116.141.0/24", "89.116.244.0/24", "89.117.129.0/24", "89.251.12.0/24", "91.102.186.0/24", "91.193.42.0/24", "91.194.25.0/24", "91.194.104.0/24", "91.198.107.0/24", "91.198.117.0/24", "91.207.12.0/23", "91.208.21.0/24", "91.209.81.0/24", "91.213.115.0/24", "91.213.126.0/24", "91.213.146.0/24", "91.218.37.0/24", "91.223.161.0/24", "91.227.75.0/24", "91.228.72.0/24", "91.228.74.0/24", "91.230.237.0/24", "91.231.35.0/24", "91.233.61.0/24", "91.233.120.0/24", "91.236.18.0/24", "91.236.66.0/24", "91.237.174.0/24", "91.240.18.0/23", "91.241.6.0/23", "93.93.224.0/22", "93.94.3.0/24", "93.191.148.0/23", "93.191.219.0/24", "94.124.112.0/24", "94.140.18.0/24", "94.142.252.0/24", "95.82.16.0/20", "95.130.184.0/23", "96.0.0.0/18", "96.0.64.0/21", "96.0.84.0/22", "96.0.88.0/22", "96.0.92.0/23", "96.0.96.0/22", "96.0.100.0/23", "96.0.104.0/22", "96.9.221.0/24", "98.97.248.0/22", "98.97.253.0/24", "98.97.254.0/23", "98.142.155.0/24", "99.77.0.0/18", "99.77.130.0/23", "99.77.132.0/22", "99.77.136.0/21", "99.77.144.0/23", "99.77.147.0/24", "99.77.148.0/23", "99.77.150.0/24", "99.77.152.0/21", "99.77.160.0/23", "99.77.183.0/24", "99.77.186.0/24", "99.77.188.0/23", "99.77.190.0/24", "99.77.233.0/24", "99.77.234.0/23", "99.77.238.0/23", "99.77.240.0/24", "99.77.242.0/24", "99.77.244.0/22", "99.77.248.0/22", "99.77.252.0/23", "99.78.128.0/19", "99.78.160.0/21", "99.78.168.0/22", "99.78.172.0/24", "99.78.176.0/21", "99.78.192.0/18", "99.79.0.0/16", "99.80.0.0/15", "99.82.128.0/19", "99.82.160.0/20", "99.82.184.0/21", "99.83.72.0/21", "99.83.80.0/21", "99.83.96.0/22", "99.83.100.0/23", "99.83.102.0/24", "99.83.120.0/22", "99.83.128.0/17", "99.84.0.0/19", "99.84.32.0/20", "99.84.48.0/24", "99.84.50.0/23", "99.84.52.0/22", "99.84.56.0/21", "99.84.64.0/18", "99.84.128.0/24", "99.84.130.0/23", "99.84.132.0/22", "99.84.136.0/21", "99.84.144.0/20", "99.84.160.0/19", "99.84.192.0/18", "99.86.0.0/17", "99.86.128.0/21", "99.86.136.0/24", "99.86.144.0/21", "99.86.153.0/24", "99.86.154.0/23", "99.86.156.0/22", "99.86.160.0/20", "99.86.176.0/21", "99.86.185.0/24", "99.86.186.0/23", "99.86.188.0/22", "99.86.192.0/21", "99.86.201.0/24", "99.86.202.0/23", "99.86.204.0/22", "99.86.217.0/24", "99.86.218.0/23", "99.86.220.0/22", "99.86.224.0/20", "99.86.240.0/21", "99.86.249.0/24", "99.86.250.0/23", "99.86.252.0/22", "99.87.0.0/19", "99.87.32.0/22", "99.150.0.0/21", "99.150.16.0/20", "99.150.32.0/19", "99.150.64.0/18", "99.151.64.0/18", "99.151.128.0/19", "99.151.186.0/23", "100.20.0.0/14", "103.4.8.0/21", "103.8.172.0/22", "103.10.127.0/24", "103.16.56.0/24", "103.16.59.0/24", "103.16.101.0/24", "103.19.244.0/22", "103.23.68.0/23", "103.39.40.0/24", "103.43.38.0/23", "103.53.55.0/24", "103.58.192.0/24", "103.70.20.0/22", "103.70.49.0/24", "103.80.6.0/24", "103.85.213.0/24", "103.104.86.0/24", "103.107.56.0/24", "103.119.213.0/24", "103.123.219.0/24", "103.124.134.0/23", "103.127.75.0/24", "103.136.10.0/24", "103.143.45.0/24", "103.145.182.0/24", "103.145.192.0/24", "103.147.71.0/24", 
                                        "103.149.112.0/24", "103.150.47.0/24", "103.150.161.0/24", "103.151.39.0/24", "103.151.192.0/23", "103.152.248.0/24", "103.161.77.0/24", "103.165.160.0/24", "103.166.180.0/24", "103.167.153.0/24", "103.168.156.0/23", "103.168.209.0/24", "103.175.120.0/23", "103.179.36.0/23", "103.180.30.0/24", "103.181.194.0/24", "103.181.240.0/24", "103.182.250.0/23", "103.187.14.0/24", "103.188.89.0/24", "103.190.166.0/24", "103.193.9.0/24", "103.195.60.0/22", "103.196.32.0/24", "103.211.172.0/24", "103.229.8.0/23", "103.229.10.0/24", "103.235.88.0/24", "103.238.120.0/24", "103.246.148.0/22", "103.246.251.0/24", "104.36.33.0/24", "104.153.112.0/23", "104.171.198.0/23", "104.192.136.0/23", "104.192.138.0/24", "104.192.140.0/23", "104.192.143.0/24", "104.193.186.0/24", "104.193.205.0/24", "104.193.207.0/24", "104.207.162.0/24", "104.207.170.0/23", "104.207.172.0/23", "104.207.174.0/24", "104.218.202.0/24", "104.232.45.0/24", "104.234.23.0/24", "104.238.244.0/23", "104.238.247.0/24", "104.249.160.0/23", "104.249.162.0/24", "104.253.192.0/24", "104.255.56.0/22", "104.255.60.0/24", "107.162.252.0/24", "108.128.0.0/13", "108.136.0.0/15", "108.138.0.0/16", "108.139.0.0/19", "108.139.32.0/20", "108.139.48.0/21", "108.139.56.0/24", "108.139.72.0/21", "108.139.80.0/22", "108.139.84.0/23", "108.139.86.0/24", "108.139.102.0/23", "108.139.104.0/21", "108.139.112.0/20", "108.139.128.0/20", "108.139.144.0/23", "108.139.146.0/24", "108.139.162.0/23", "108.139.164.0/22", "108.139.168.0/21", "108.139.176.0/20", "108.139.207.0/24", "108.139.208.0/20", "108.139.224.0/19", "108.156.0.0/17", "108.156.128.0/23", "108.156.130.0/24", "108.156.146.0/23", "108.156.148.0/22", "108.156.152.0/21", "108.156.160.0/19", "108.156.192.0/18", "108.157.0.0/21", "108.157.8.0/23", "108.157.85.0/24", "108.157.86.0/23", "108.157.88.0/21", "108.157.96.0/20", "108.157.112.0/23", "108.157.114.0/24", "108.157.130.0/23", "108.157.132.0/22", "108.157.136.0/21", "108.157.144.0/20", "108.157.160.0/21", "108.157.168.0/22", "108.157.172.0/23", "108.157.174.0/24", "108.157.205.0/24", "108.157.206.0/23", "108.157.208.0/20", "108.157.224.0/21", "108.157.232.0/23", "108.157.234.0/24", "108.158.39.0/24", "108.158.40.0/21", "108.158.48.0/20", "108.158.64.0/22", "108.158.68.0/24", "108.158.114.0/23", "108.158.116.0/22", "108.158.120.0/21", "108.158.128.0/20", "108.158.144.0/21", "108.158.152.0/22", "108.158.156.0/23", "108.158.158.0/24", "108.158.219.0/24", "108.158.220.0/22", "108.158.224.0/19", "108.159.0.0/18", "108.159.64.0/19", "108.159.96.0/23", "108.159.128.0/21", "108.159.136.0/22", "108.159.144.0/23", "108.159.155.0/24", "108.159.156.0/24", "108.159.160.0/23", "108.159.163.0/24", "108.159.164.0/24", "108.159.166.0/23", "108.159.168.0/21", "108.159.181.0/24", "108.159.182.0/23", "108.159.184.0/24", "108.159.188.0/22", "108.159.192.0/24", "108.159.197.0/24", "108.159.198.0/23", "108.159.200.0/21", "108.159.208.0/24", "108.159.213.0/24", "108.159.214.0/23", "108.159.216.0/21", "108.159.224.0/21", "108.159.247.0/24", "108.159.248.0/23", "108.159.250.0/24", "108.159.255.0/24", "108.175.52.0/23", "108.175.54.0/24", "109.68.71.0/24", "109.95.191.0/24", "109.224.233.0/24", "109.232.88.0/21", "116.214.100.0/23", "116.214.120.0/23", "122.248.192.0/18", "122.252.145.0/24", "122.252.146.0/23", "122.252.148.0/22", "129.33.138.0/23", "129.33.243.0/24", "129.41.76.0/23", "129.41.88.0/23", "129.41.167.0/24", "129.41.174.0/23", "129.41.222.0/24", "130.50.35.0/24", "130.137.20.0/24", "130.137.78.0/24", "130.137.81.0/24", "130.137.86.0/24", "130.137.99.0/24", "130.137.112.0/24", "130.137.124.0/24", "130.137.136.0/24", "130.137.150.0/24", "130.137.178.0/24", "130.137.215.0/24", "130.176.0.0/21", "130.176.9.0/24", "130.176.10.0/23", "130.176.13.0/24", "130.176.14.0/24", "130.176.16.0/23", "130.176.24.0/23", "130.176.27.0/24", "130.176.28.0/22", "130.176.32.0/21", "130.176.40.0/24", "130.176.43.0/24", "130.176.45.0/24", "130.176.48.0/24", "130.176.50.0/24", "130.176.53.0/24", "130.176.54.0/24", "130.176.56.0/24", "130.176.65.0/24", "130.176.66.0/23", "130.176.68.0/24", "130.176.71.0/24", "130.176.75.0/24", "130.176.76.0/22", "130.176.80.0/21", "130.176.88.0/22", "130.176.92.0/23", "130.176.96.0/22", "130.176.100.0/24", "130.176.102.0/23", "130.176.104.0/22", "130.176.108.0/23", "130.176.111.0/24", "130.176.112.0/23", "130.176.116.0/24", "130.176.118.0/23", "130.176.120.0/24", "130.176.125.0/24", "130.176.126.0/23", "130.176.129.0/24", "130.176.130.0/23", "130.176.132.0/22", "130.176.136.0/23", "130.176.139.0/24", "130.176.140.0/22", "130.176.144.0/23", "130.176.146.0/24", "130.176.148.0/22", "130.176.152.0/24", "130.176.155.0/24", "130.176.156.0/22", "130.176.160.0/21", "130.176.168.0/24", "130.176.170.0/23", "130.176.172.0/24", "130.176.174.0/23", "130.176.179.0/24", "130.176.182.0/23", "130.176.184.0/21", "130.176.192.0/24", "130.176.194.0/23", "130.176.196.0/22", 
                                        "130.176.200.0/21", "130.176.208.0/21", "130.176.217.0/24", "130.176.218.0/23", "130.176.220.0/22", "130.176.224.0/24", "130.176.226.0/23", "130.176.231.0/24", "130.176.232.0/24", "130.176.254.0/23", "130.193.2.0/24", "131.232.37.0/24", "131.232.76.0/23", "131.232.78.0/24", "132.75.97.0/24", "134.224.0.0/17", "134.224.128.0/18", "134.224.192.0/19", "134.224.224.0/20", "134.224.242.0/23", "134.224.244.0/22", "134.224.248.0/22", "135.84.124.0/24", "136.18.18.0/23", "136.18.20.0/22", "136.175.24.0/23", "136.175.106.0/23", "136.175.113.0/24", "136.184.226.0/23", "136.184.229.0/24", "136.184.230.0/23", "136.184.232.0/23", "136.184.235.0/24", "136.226.219.0/24", "136.226.220.0/23", "137.83.193.0/24", "137.83.195.0/24", "137.83.196.0/22", "137.83.202.0/23", "137.83.204.0/23", "137.83.208.0/22", "137.83.212.0/24", "137.83.214.0/24", "137.83.252.0/22", "138.43.114.0/24", "139.60.2.0/24", "139.60.113.0/24", "139.60.114.0/24", "139.64.232.0/24", "139.138.105.0/24", "139.180.31.0/24", "139.180.242.0/23", "139.180.246.0/23", "139.180.248.0/22", "140.19.64.0/24", "140.99.123.0/24", "140.228.26.0/24", "141.11.12.0/22", "141.163.128.0/20", "141.193.32.0/23", "141.193.208.0/23", "142.0.189.0/24", "142.0.190.0/24", "142.4.160.0/22", "142.4.177.0/24", "142.54.40.0/24", "142.202.20.0/24", "142.202.36.0/22", "142.202.40.0/24", "142.202.42.0/23", "142.202.46.0/24", "143.55.151.0/24", "143.204.0.0/19", "143.204.32.0/21", "143.204.40.0/24", "143.204.57.0/24", "143.204.58.0/23", "143.204.60.0/22", "143.204.64.0/20", "143.204.80.0/21", "143.204.89.0/24", "143.204.90.0/23", "143.204.92.0/22", "143.204.96.0/20", "143.204.112.0/21", "143.204.121.0/24", "143.204.122.0/23", "143.204.124.0/22", "143.204.128.0/18", "143.204.192.0/19", "143.204.224.0/20", "143.204.240.0/21", "143.204.249.0/24", "143.204.250.0/23", "143.204.252.0/22", "143.244.81.0/24", "143.244.82.0/23", "143.244.84.0/22", "144.2.170.0/24"],
    )
            elif group_choice == '7':  
                ip_or_domain_list.extend(["173.245.48.0/20","103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22", "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20", 
                                        "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15", "104.16.0.0/13", "104.24.0.0/14", "172.64.0.0/13", "131.0.72.0/22"])  # Replace with actual IPs
            else:
                print("Invalid group choice.")
                return

        else:
            print("Invalid choice.")
            return

        if not ip_or_domain_list:
            print("No WebSocket domains or IPs provided.")
            return

        output_file_name = input("Enter the name of the output file to save valid connections (or leave blank to skip saving): ")



        successful_connections = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=150) as executor:
            results = [
                executor.submit(establish_websocket_connection, ip_or_domain.strip(), output_file_name)
                for ip_or_domain in ip_or_domain_list
            ]

            for future in concurrent.futures.as_completed(results):
                result = future.result()
                if result:
                    successful_connections += result

        if successful_connections > 0:
            print(f"{Fore.GREEN}Total {successful_connections} valid connections saved to {output_file_name}.")

        if not output_file_name.strip():
            print("No output file specified. Exiting.")
            print(successful_connections)
        else:
            print(f"{Fore.RED}No valid WebSocket connections found.")

        time.sleep(1)

        print("""
        ===================================
                    Menu                
        ===================================
        1. Return to main menu
        2. Proceed to the script
        """)

        while True:
            choice = input("Enter your choice (1): ")
            if choice == '1':
                print("Returning to BUGHUNTERS PRO...")
                time.sleep(1)
                os.system('cls' if os.name == 'nt' else 'clear')
                break
            elif choice == '2':
                k()
            else:
                break
    k()

#===WEBSOCKER SCANNER OLD===#
def websocket_scanner_old():
                    
    import configparser

    bg=''
    #G = bg+'\033[32m'
    OP = bg+'\033[33m'
    GR = bg+'\033[37m'
    R = bg+'\033[31m'

    print(OP+'''  
            
        ██╗    ██╗███████╗██████╗ ███████╗ ██████╗  ██████╗██╗  ██╗███████╗████████╗    
        ██║    ██║██╔════╝██╔══██╗██╔════╝██╔═══██╗██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝    
        ██║ █╗ ██║█████╗  ██████╔╝███████╗██║   ██║██║     █████╔╝ █████╗     ██║       
        ██║███╗██║██╔══╝  ██╔══██╗╚════██║██║   ██║██║     ██╔═██╗ ██╔══╝     ██║       
        ╚███╔███╔╝███████╗██████╔╝███████║╚██████╔╝╚██████╗██║  ██╗███████╗   ██║       
        ╚══╝╚══╝ ╚══════╝╚═════╝ ╚══════╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝       
                                                                                            
            ███████╗ ██████╗ █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗                     
            ██╔════╝██╔════╝██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗                    
            ███████╗██║     ███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝                    
            ╚════██║██║     ██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗                    
            ███████║╚██████╗██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║                    
            ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝                    
                                                                                        '''+GR)
    import socket
    import ssl
    import base64
    import random
    import ipaddress
    import os
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from time import sleep

    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    def check_websocket(host, port, path="/", use_ssl=False):
        global output_file  # Ensure access to global variable

        key = base64.b64encode(bytes(random.getrandbits(8) for _ in range(16))).decode()

        headers = [
            f"GET {path} HTTP/1.1",
            f"Host: {host}:{port}",
            "Upgrade: websocket",
            "Connection: Upgrade",
            f"Sec-WebSocket-Key: {key}",
            "Sec-WebSocket-Version: 13",
            "\r\n"
        ]

        request_data = "\r\n".join(headers)

        try:
            sock = socket.create_connection((host, port), timeout=5)
            if use_ssl:
                context = ssl.create_default_context()
                sock = context.wrap_socket(sock, server_hostname=host)

            sock.sendall(request_data.encode())
            response = sock.recv(2048).decode(errors="ignore")
            sock.close()

            status_line = response.splitlines()[0] if response else ""
            status_code = status_line.split()[1] if len(status_line.split()) >= 2 else "???"

            result = f"{'wss' if use_ssl else 'ws'}://{host}:{port}{path}"

            if status_code == "101" and "upgrade: websocket" in response.lower():
                print(f"{GREEN}[+] {result} — WebSocket Supported (Status: {status_code}){RESET}")
                if output_file:
                    try:
                        with open(output_file, "a", encoding="utf-8") as f:
                            f.write(result + f" (Status: {status_code})\n")
                            f.flush()  # Immediately flush to disk
                            os.fsync(f.fileno())  # Ensure physical write
                    except Exception as write_err:
                        print(f"{RED}[!] Failed to write result: {write_err}{RESET}")
            elif status_code.isdigit():
                print(f"{YELLOW}[-] {result} — WebSocket NOT supported (Status: {status_code}){RESET}")
            else:
                print(f"{RED}[-] {result} — Invalid or Unknown Response (Status: {status_code}){RESET}")
        except Exception as e:
            print(f"{RED}[!] {host}:{port} - Error: {RESET}")


    def process_input(input_data):
        targets = []

        if os.path.isfile(input_data):
            with open(input_data, 'r') as f:
                lines = f.read().splitlines()
                for line in lines:
                    targets.extend(process_input(line.strip()))
        else:
            try:
                net = ipaddress.ip_network(input_data, strict=False)
                for ip in net.hosts():
                    targets.append(str(ip))
            except ValueError:
                # Treat as domain or single IP
                if input_data.startswith("http://") or input_data.startswith("https://"):
                    input_data = input_data.split("//")[1].split("/")[0]
                targets.append(input_data)

        return targets

    def scan_batch(batch, port, path, use_ssl):
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = [executor.submit(check_websocket, ip, port, path, use_ssl) for ip in batch]
            for _ in as_completed(futures):
                pass  # Output is handled inside check_websocket

    def chunked(lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def mj4():
        import os
        import time
        from time import sleep

        global output_file
        output_file = None  # in case it's not set later

        try:
            input_data = input("Enter IP / domain / CIDR / filename: ").strip()
            path = input("Enter WebSocket path (default is '/'): ").strip()
            if not path:
                path = "/"

            save_results = input("Do you want to save successful connections? (yes/no): ").strip().lower()
            if save_results in ["yes", "y", "true", "1"]:
                output_file = input("Enter filename to save (e.g., results.txt): ").strip()
                print(f"[✓] Saving successful WebSocket connections to {output_file}\n")

            targets = process_input(input_data)
            print(f"[+] Total targets: {len(targets)} — scanning ports 80 and 443 in batches of 500...\n")

            for batch in chunked(targets, 500):
                print("[*] Scanning port 80 (ws://)...")
                scan_batch(batch, 80, path, use_ssl=False)

                print("[*] Scanning port 443 (wss://)...")
                scan_batch(batch, 443, path, use_ssl=True)

                sleep(0.5)

        except KeyboardInterrupt:
            print("\n[!] Scan interrupted by user.")
        except Exception as e:
            print(f"[!] An error occurred: {e}")
            if output_file:
                print(f"[!] Results saved to {output_file}")
            else:
                print("[!] No results saved.")
            if output_file and os.path.exists(output_file):
                os.remove(output_file)
                print(f"[!] Temporary file {output_file} removed.")
            else:
                print("[!] No temporary file to remove.")
        finally:
            print("[!] Exiting...")
            time.sleep(1)
    mj4()

#===SUBDOmain TAKEOVER===#
def access_control():

    generate_ascii_banner("ACCESS", "CONTROL")
    THREAD_COUNT = 100

    LOCK = threading.Lock()
    user_input = input("Enter a domain or .txt file: ").strip()
    OUTPUT_FILE = input("Enter output file name (default is x_requested_with_results.txt): ").strip() or "x_requested_with_results.txt"
    def check_domain(domain, progress):
        preflight_headers = {
            'Origin': 'https://yahoo.com/',
            'Access-Control-Request-Method': 'GET',
            'Access-Control-Request-Headers': 'X-Requested-With, X-Online-Host, X-Forwarded-For',
            'User-Agent': 'Mozilla/5.0'
        }

        for protocol in ['http://', 'https://']:
            url = protocol + domain
            try:
                response = requests.options(url, headers=preflight_headers, timeout=5)
                status = response.status_code
                allowed_headers = response.headers.get('Access-Control-Allow-Headers', '').lower()

                allowed = []
                if 'x-requested-with' in allowed_headers:
                    allowed.append('X-Requested-With')
                if 'x-online-host' in allowed_headers:
                    allowed.append('X-Online-Host')
                if 'x-forwarded-for' in allowed_headers:
                    allowed.append('X-Forwarded-For')

                if allowed:
                    server = response.headers.get('Server', 'Unknown')
                    print(f"✅ {url} - ALLOWS: {', '.join(allowed)} | Status: {status}")
                    with LOCK:
                        with open(OUTPUT_FILE, "a") as f:
                            f.write(f"{url} | Status: {status} | Server: {server} | Allowed Headers: {', '.join(allowed)}\n")
                else:
                    print(f"⚠️ {url} - None of the desired X-* headers allowed.")

            except requests.exceptions.RequestException as e:
                print(f"❌ {url} - Request failed: {e}")
            finally:
                with LOCK:
                    progress.update(1)


    def worker(domain_queue, progress):
        while not domain_queue.empty():
            domain = domain_queue.get()
            check_domain(domain, progress)
            domain_queue.task_done()

    def access_main():


        if os.path.isfile(user_input) and user_input.endswith('.txt'):
            with open(user_input, 'r') as file:
                domains = [line.strip() for line in file if line.strip()]
        else:
            domains = [user_input]

        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

        domain_queue = Queue()
        for domain in domains:
            domain_queue.put(domain)

        progress = tqdm(total=len(domains) * 2, desc="Checking", ncols=80)

        threads = []
        for _ in range(THREAD_COUNT):
            t = threading.Thread(target=worker, args=(domain_queue, progress))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        progress.close()
        print(f"\n✅ Finished checking. Results saved to {OUTPUT_FILE}")

    access_main()

#===IP GEN===#
def ipgen():
    
    generate_ascii_banner("IP", "GEN")

    def validate_ip_range(ip_range):
        try:
            ipaddress.ip_network(ip_range)
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid IP range")
        return ip_range

    def calculate_ipv4_addresses(ip_ranges, num_threads, pbar):
        addresses = []

        def calculate_ipv4_addresses_thread(ip_range):
            ip_network = ipaddress.ip_network(ip_range)
            for address in ip_network:
                addresses.append(address)
                pbar.update(1)

        threads = []
        for ip_range in ip_ranges:
            t = threading.Thread(target=calculate_ipv4_addresses_thread, args=(ip_range,))
            threads.append(t)
            t.start()

        # Wait for all threads to finish before returning the addresses
        for t in threads:
            t.join()

        return addresses

    def print_addresses(addresses, output_file):
        with open(output_file, "w") as f:
            for address in addresses:
                f.write(str(address) + "\n")

    def ipgen_main():
        input_choice = input("Enter '1' to input IP ranges or '2' to specify a file containing IP ranges: ")
        
        if input_choice == '1':
            ip_ranges_input = input("Enter a single IP range in CIDR notation or list of IP ranges separated by comma: ")
            ip_ranges = [ip_range.strip() for ip_range in ip_ranges_input.split(",")]

            for ip_range in ip_ranges:
                validate_ip_range(ip_range)
        elif input_choice == '2':
            file_name = input("Enter the name of the file containing IP ranges (must be in the same directory as the script): ")
            try:
                with open(file_name) as f:
                    ip_ranges = [line.strip() for line in f]
            except FileNotFoundError:
                print("Error: File not found.")
                return
        else:
            print("Invalid input.")
            return

        output_file = input("Enter the name of the output file: ")
        num_threads = int(input("Enter the number of threads to use: "))

        total_addresses = sum([2 ** (32 - ipaddress.ip_network(ip_range).prefixlen) for ip_range in ip_ranges])

        with tqdm(total=total_addresses, desc="Calculating addresses") as pbar:
            addresses = calculate_ipv4_addresses(ip_ranges, num_threads, pbar)

        print_addresses(addresses, output_file)

    ipgen_main()

#===OPEN PORT CHECKER===#
def open_port_checker():

    generate_ascii_banner("PORT SCANNER", "")

    def scan_port(target, port, timeout=0.5):
        """Scan a single port for a given target."""
        try:
            if port == 443:  # SSL/TLS port
                context = ssl.create_default_context()
                with context.wrap_socket(socket.socket(socket.AF_INET), server_hostname=target) as sock:
                    sock.settimeout(timeout)
                    sock.connect((target, port))
                    return port, "Open"
            else:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(timeout)
                    result = sock.connect_ex((target, port))
                    if result == 0:
                        return port, "Open"
                    elif result == 11:
                        return port, "Closed"
                    else:
                        return port, "Filtered"
        except Exception as e:
            return port, f"Error: {str(e)}"

    def scan_ports_for_target(target, ports, timeout=0.5):
        """Scan all ports for a given target using ThreadPoolExecutor."""
        results = {}
        with ThreadPoolExecutor(max_workers=len(ports)) as executor:
            future_to_port = {executor.submit(scan_port, target, port, timeout): port for port in ports}
            for future in as_completed(future_to_port):
                port, status = future.result()
                results[port] = status
        return results

    def scan_ports_threaded(targets, ports, num_threads=10, timeout=0.5):
        """Scan ports for multiple targets using multiple threads."""
        results_dict = {}
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            future_to_target = {executor.submit(scan_ports_for_target, target, ports, timeout): target for target in targets}
            for future in as_completed(future_to_target):
                target = future_to_target[future]
                results_dict[target] = future.result()
        return results_dict

    def print_results(results_dict, ports):
        """Print results in a clean table format with color coding."""
        from colorama import init, Fore, Back, Style
        init()  # Initialize colorama
        
        # Table header
        print(f"\n{Fore.YELLOW}Scan Results:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'Target':<25}", end="")
        for port in ports:
            print(f"{port:>8}", end="")
        print(Style.RESET_ALL)
        
        print("-" * (25 + len(ports) * 8))  # Separator line
        
        # Table rows
        for target, results in results_dict.items():
            print(f"{Fore.CYAN}{target:<25}{Style.RESET_ALL}", end="")
            for port in ports:
                status = results.get(port, "N/A")
                if "Open" in status:
                    color = Fore.GREEN
                elif "Closed" in status:
                    color = Fore.RED
                elif "Error" in status:
                    color = Fore.MAGENTA
                else:
                    color = Fore.YELLOW
                print(f"{color}{status[:7]:>8}{Style.RESET_ALL}", end="")
            print()
        
        # Summary
        print(f"\n{Fore.YELLOW}Scan Summary:{Style.RESET_ALL}")
        total_targets = len(results_dict)
        targets_with_open_ports = sum(1 for results in results_dict.values() 
                                    if any("Open" in status for status in results.values()))
        
        print(f"Scanned {total_targets} target(s)")
        print(f"Targets with open ports: {targets_with_open_ports}")
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    def save_to_file(filename, results_dict, ports):
        """Save results to a file in CSV format."""
        with open(filename, "w") as file:
            # Write header
            file.write("Target," + ",".join(str(port) for port in ports) + "\n")
            
            # Write data
            for target, results in results_dict.items():
                file.write(target + ",")
                file.write(",".join(results.get(port, "N/A") for port in ports))
                file.write("\n")
        
        print(f"\nResults saved to {filename} in CSV format")

    def get_user_input(prompt, input_type=str, default=None):
        """Helper function to get user input with validation."""
        while True:
            try:
                user_input = input(prompt)
                if not user_input and default is not None:
                    return default
                return input_type(user_input)
            except ValueError:
                print("Invalid input. Please try again.")

    def open_port_checker_main():

        
        # Common ports to scan
        DEFAULT_PORTS = [80, 8080, 443, 21, 22, 53, 67, 68, 123, 161, 162, 500, 520, 514, 5353, 4500, 1900, 5000, 3000]
        
        try:
            print("\n1. Scan single target")
            print("2. Scan multiple targets from file")
            choice = get_user_input("Select option (1-2): ", int, 1)
            
            if choice == 1:
                target = get_user_input("Enter target domain/IP: ")
                targets = [target.strip()]
            else:
                filename = get_user_input("Enter filename with targets (one per line): ")
                with open(filename, "r") as file:
                    targets = [line.strip() for line in file if line.strip()]
            
            # Let user customize ports if they want
            print(f"\nDefault ports to scan: {', '.join(map(str, DEFAULT_PORTS))}")
            custom_ports = get_user_input("Enter custom ports to scan (comma separated, or press Enter for default): ", str)
            ports = [int(p.strip()) for p in custom_ports.split(",")] if custom_ports else DEFAULT_PORTS
            
            num_threads = get_user_input(f"Enter number of threads (recommended 10-100): ", int, 10)
            timeout = get_user_input("Enter timeout per port (seconds, 0.5 recommended): ", float, 0.5)
            
            print(f"\nStarting scan for {len(targets)} target(s) and {len(ports)} port(s)...")
            
            results_dict = scan_ports_threaded(targets, ports, num_threads, timeout)
            print_results(results_dict, ports)
            
            if get_user_input("Save results to file? (y/n): ", str, "n").lower() == "y":
                default_filename = f"portscan_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                filename = get_user_input(f"Enter filename (or Enter for {default_filename}): ", str, default_filename)
                save_to_file(filename, results_dict, ports)
                
        except Exception as e:
            print(f"\n{Fore.RED}Error occurred: {e}{Style.RESET_ALL}")
        finally:
            print("\nScan completed. Goodbye!\n")


    open_port_checker_main()

#===UDP TCP===#
def udp_tcp():
    
    generate_ascii_banner("UDP", "TCP")

    import socket
    import ssl
    import os
    import re
    import requests
    import dns.resolver
    import ipaddress
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import time

    # Constants
    SAVE_FILE = 'scan_results.txt'
    TIMEOUT = 1.5  # Reduced timeout from 2 to 1.5 seconds
    MAX_THREADS = 100  # Increased thread pool size

    # Optimized port list - focusing on most common ports first
    COMMON_PORTS = [
        80, 443, 22, 21, 25, 53, 110, 143, 465, 587, 993, 995,  # Common web/email
        3389, 3306, 5432, 27017, 1521, 1433,  # Database ports
        8080, 8443, 8888, 8000,  # Alternative web ports
        161, 162, 137, 139, 445,  # Network services
        23, 69, 123, 514,  # Misc services
    ]

    # Dictionary for common UDP ports with payloads (optimized for most common first)
    common_ports_payloads = {
        53: b'\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x07example\x03com\x00\x00\x01\x00\x01',  # DNS
        123: b'\x1b' + 47 * b'\0',  # NTP
        161: b'\x30\x26\x02\x01\x00\x04\x06public\xa0\x19\x02\x04\x13\x79\xf9\xa9\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05\x2b\x06\x01\x02\x01\x05\x00',  # SNMP
        137: b'\x82\x28\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x20\x43\x4B\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x00\x00\x21\x00\x01',  # NetBIOS
        500: b'\x00' * 100,  # ISAKMP
        1900: b'M-SEARCH * HTTP/1.1\r\nHOST:239.255.255.250:1900\r\nMAN:"ssdp:discover"\r\nMX:1\r\nST:ssdp:all\r\n',  # SSDP
        # Removed less common UDP ports to speed up scanning
    }

    def send_udp_packet(ip, port, payload):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(TIMEOUT)
            try:
                sock.sendto(payload, (ip, port))
                data, _ = sock.recvfrom(1024)
                return data
            except (socket.timeout, ConnectionResetError):
                return None
            except Exception as e:
                return None

    def detect_net_server(ip, port):
        try:
            with socket.create_connection((ip, port), timeout=TIMEOUT) as sock:
                sock.settimeout(TIMEOUT)
                sock.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                data = sock.recv(1024)
                return f"Inferred Net Server: {parse_net_server(data)}"
        except Exception:
            return "Unknown Net Server"

    def parse_net_server(data):
        try:
            text = data.decode('utf-8', errors='ignore').lower()
            return "Unknown Net Server"
        except Exception:
            return "Unknown Net Server"


    def service_detection(ip, port):
        try:
            # HTTP
            if port == 80:
                response = requests.head(f'http://{ip}', timeout=TIMEOUT, allow_redirects=True)
                server = response.headers.get('Server', '').strip()
                if not server:
                    return detect_net_server(ip, port)
                return f"HTTP Service: {server}"
            
            # HTTPS
            elif port == 443:
                response = requests.head(f'https://{ip}', timeout=TIMEOUT, verify=False, allow_redirects=True)
                server = response.headers.get('Server', '').strip()
                if not server:
                    return detect_net_server(ip, port)
                return f"HTTPS Service: {server}"
            
            # SSH
            elif port == 22:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(TIMEOUT)
                    s.connect((ip, port))
                    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                    return f"SSH Banner: {banner}"

            # Common TCP services with banners
            elif port in [21, 3306, 5432, 27017]:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(TIMEOUT)
                    s.connect((ip, port))
                    banner = s.recv(1024).decode('utf-8', errors='ignore').strip()
                    return f"Banner: {banner[:100]}"

            # UDP - optional but fragile (SNMP, NTP)
            elif port in [53, 161, 123, 500, 1900]:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                    s.settimeout(TIMEOUT)
                    s.sendto(b'\x00', (ip, port))
                    data, _ = s.recvfrom(1024)
                    if data:
                        return f"UDP Response: {data[:100]}"
            
            # Generic TCP banner grabbing fallback
            elif port in COMMON_PORTS:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(TIMEOUT)
                    s.connect((ip, port))
                    banner = s.recv(1024).decode(errors='ignore').strip()
                    return f"TCP Banner: {banner[:100]}"

        except Exception:
            return "Service detected"

        return "Unknown service"


    def fast_tcp_scan(ip, ports, scan_results):
        def check_port(ip, port):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(TIMEOUT)
                    result = s.connect_ex((ip, port))
                    if result == 0:
                        service = service_detection(ip, port)
                        return port, f"TCP open - {service}"
            except Exception:
                pass
            return None, None

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(check_port, ip, port) for port in ports]
            for future in as_completed(futures):
                port, status = future.result()
                if port:
                    scan_results[port] = status

    def fast_udp_scan(ip, ports, scan_results):
        def check_udp_port(ip, port):
            payload = common_ports_payloads.get(port, b'')
            response = send_udp_packet(ip, port, payload)
            if response is not None:
                service = service_detection(ip, port)
                return port, f"UDP open - {service}"
            return None, None

        with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
            futures = [executor.submit(check_udp_port, ip, port) for port in ports if port in common_ports_payloads]
            for future in as_completed(futures):
                port, status = future.result()
                if port:
                    scan_results[port] = status

    def scan_target(ip):
        scan_results = {}
        print(f"Scanning {ip}...", end='\r')
        
        # Scan TCP ports first (faster)
        fast_tcp_scan(ip, COMMON_PORTS, scan_results)
        
        # Only scan UDP if we found open TCP ports (heuristic to save time)
        if scan_results:
            fast_udp_scan(ip, COMMON_PORTS, scan_results)
        
        # SSL check only if 443 is open
        if 443 in COMMON_PORTS and any(p == 443 for p in scan_results):
            try:
                context = ssl.create_default_context()
                with socket.create_connection((ip, 443), timeout=TIMEOUT) as sock:
                    with context.wrap_socket(sock, server_hostname=ip) as sslsock:
                        cert = sslsock.getpeercert()
                        scan_results['SSL'] = f"Certificate: {cert.get('subject', '')}"
            except Exception:
                pass

        return scan_results

    def batch_scan(targets):
        all_results = {}
        with ThreadPoolExecutor(max_workers=100) as executor:  # Scan multiple IPs in parallel
            future_to_ip = {executor.submit(scan_target, ip): ip for ip in targets}
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                try:
                    results = future.result()
                    if results:
                        all_results[ip] = results
                except Exception as e:
                    print(f"Error scanning {ip}:")
        return all_results



    def get_targets_from_input(input_str):
        targets = set()
        try:
            if os.path.isfile(input_str):
                with open(input_str) as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.strip()
                        targets.update(get_targets_from_input(line))
            elif "/" in input_str:  # CIDR
                net = ipaddress.ip_network(input_str, strict=False)
                targets.update(str(ip) for ip in net.hosts())
            elif re.match(r"^\d{1,3}(\.\d{1,3}){3}$", input_str):  # IP
                targets.add(input_str)
            else:  # Domain
                try:
                    ip = socket.gethostbyname(input_str)
                    targets.add(ip)
                except:
                    print(f"Failed to resolve domain: {input_str}")
        except Exception as e:
            print(f"Error processing input:")
        return list(targets)

    def save_results_to_file(results):
        with open(SAVE_FILE, "w") as f:
            for ip, ports in results.items():
                f.write(f"\n[+] {ip}\n")
                for port, info in ports.items():
                    f.write(f"  {port}: {info}\n")


    def udp_tcp_main098():
        user_input = input("Enter IP/URL/CIDR or file path: ")
        targets = get_targets_from_input(user_input)
        
        if not targets:
            print("No valid targets found.")
            return
        
        start_time = time.time()
        all_results = batch_scan(targets)
        elapsed = time.time() - start_time
        
        save_results_to_file(all_results)
        print(f"\nScanned {len(targets)} targets in {elapsed:.2f} seconds")
        print(f"Results saved to '{SAVE_FILE}'")

    udp_tcp_main098()

#===TCP SSL===#
def tcp_ssl():

    generate_ascii_banner("TCP", "SSL")
    # Supported SSL/TLS versions
    SSL_VERSIONS = {
        "SSLv1": ssl.PROTOCOL_SSLv23,  # Legacy compatibility
        "SSLv2": ssl.PROTOCOL_SSLv23,  # Python removed explicit SSLv2
        "SSLv3": ssl.PROTOCOL_SSLv23,  # Legacy fallback
        "TLSv1.0": ssl.PROTOCOL_TLSv1,
        "TLSv1.1": ssl.PROTOCOL_TLSv1_1,
        "TLSv1.2": ssl.PROTOCOL_TLSv1_2,
    }

    # Parse input for IPs, CIDRs, hostnames, or files
    def parse_input(user_input):
        try:
            if user_input.endswith(".txt"):  # If it's a file
                with open(user_input, 'r') as f:
                    entries = [line.strip() for line in f.readlines()]
                    targets = []
                    for entry in entries:
                        if '/' in entry:  # Handle CIDR
                            targets.extend([str(ip) for ip in ipaddress.IPv4Network(entry, strict=False)])
                        else:
                            targets.append(entry)
                    return targets
            elif '/' in user_input:  # CIDR range
                return [str(ip) for ip in ipaddress.IPv4Network(user_input, strict=False)]
            else:
                socket.gethostbyname(user_input)  # Validate hostname/IP
                return [user_input]
        except Exception as e:
            print(f"Invalid input: {e}")
            return []

    # Check if a port is open via TCP
    def tcp_connect(ip, port, timeout=3):
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                return True
        except Exception:
            return False

    # Save results to a file
    def save_result(result, filename):
        try:
            with open(filename, "a") as f:
                f.write(result + "\n")
        except Exception as e:
            print(f"Error saving result: {e}")

    # Fetch SSL/TLS information
    def check_ssl_versions(ip, port):
        results = []
        for version_name, protocol in SSL_VERSIONS.items():
            try:
                context = ssl.SSLContext(protocol)
                with socket.create_connection((ip, port), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=ip) as ssock:
                        ssock.getpeercert()
                        results.append(f"{version_name} supported")
            except Exception:
                results.append(f"{version_name} not supported")
        return results

    # Extract HTTP status and banner
    def scan_target(ip, ports, output_file):
        for port in ports:
            if tcp_connect(ip, port):
                result = f"[+] {ip}:{port} is open"

                if port in [80, 443]:
                    try:
                        url = f"http://{ip}" if port == 80 else f"https://{ip}"
                        response = requests.get(url, timeout=5)
                        server = response.headers.get('Server', 'Unknown')
                        status = response.status_code

                        ssl_info = ""
                        if port == 443:
                            ssl_results = check_ssl_versions(ip, port)
                            ssl_info = " | ".join(ssl_results)

                        result = f"[+] {ip}:{port} - {server} - HTTP {status} - {ssl_info}"
                        print(result)
                        save_result(result, output_file)
                    except Exception:
                        result = f"[-] {ip}:{port} - Failed to fetch HTTP/HTTPS banner"
                        print(result)
                        save_result(result, output_file)


    # main function
    def tcp_ssl_main():
        user_input = input("Enter IP, CIDR, hostname, or file: ").strip()
        if not user_input:
            print("No input provided.")
            return
        targets = parse_input(user_input)

        if not targets:
            print("No valid targets found.")
            return

        ports = [80, 443, 22, 21, 3389, 53, 5353]  # Common ports to check

        output_file = input("Enter output file name (default: scan_results.txt): ").strip()
        if not output_file:
            output_file = "scan_results.txt"
        #if not output_file:
        #    output_file = "scan_results.txt"

        # Clear output file if it already exists
        if os.path.exists(output_file):
            os.remove(output_file)

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(scan_target, target, ports, output_file) for target in targets]

            for _ in tqdm(as_completed(futures), total=len(futures), desc="Scanning Progress", unit="target"):
                pass

        print(f"Scan completed! Results saved to {output_file}")

    tcp_ssl_main()

#===DORK SCANNER===#
def dork_scanner():
    
    import requests
    from bs4 import BeautifulSoup as bsoup
    from tqdm import tqdm
    import re
    import random
    import time
    import concurrent.futures
    from urllib.parse import urlparse

    class AdvancedDorkScanner:
        # Configuration
        STEALTH_DELAY = (1, 3)
        MAX_THREADS = 15  # Thread pool size
        USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
        CSP_DIRECTIVES = [
            'default-src', 'script-src', 'style-src',
            'img-src', 'connect-src', 'font-src',
            'object-src', 'media-src', 'frame-src'
        ]
        
        DANGEROUS_SOURCES = [
            'data:', 'blob:', 'filesystem:',
            'about:', 'unsafe-inline', 'unsafe-eval'
        ]

        def __init__(self):
            self.session = requests.Session()
            self.session.headers.update(self._random_headers())
            self.found_domains = set()

        def _random_headers(self):
            return {
                'User-Agent': random.choice(self.USER_AGENTS),
                'Accept-Language': 'en-US,en;q=0.9'
            }

        def _extract_domains_from_csp(self, csp_policy):
            """Parse CSP directives for external domains"""
            domains = set()
            for directive in self.CSP_DIRECTIVES:
                if directive in csp_policy:
                    sources = csp_policy[directive].split()
                    for src in sources:
                        if any(d in src for d in self.DANGEROUS_SOURCES):
                            continue
                        if src.startswith(('http://', 'https://')):
                            domain = urlparse(src).netloc
                            if domain: domains.add(domain)
            return domains

        def _crawl_page(self, url, domain):
            """Thread-safe page crawler with CSP analysis"""
            try:
                if not url.startswith(('http://', 'https://')):
                    url = f'http://{url}'
                
                response = self.session.get(url, timeout=15, allow_redirects=True)
                csp_headers = {
                    h: response.headers.get(h, '')
                    for h in ['Content-Security-Policy', 
                            'Content-Security-Policy-Report-Only']
                    if h in response.headers
                }
                
                # Extract domains from CSP
                csp_domains = set()
                for policy in csp_headers.values():
                    csp_domains.update(self._extract_domains_from_csp(
                        {d.split()[0]: ' '.join(d.split()[1:]) 
                        for d in policy.split(';') if d.strip()}
                    ))
                
                # Parse page links
                soup = bsoup(response.text, 'html.parser')
                page_links = {
                    self._clean_url(a['href']) 
                    for a in soup.find_all('a', href=True) 
                    if a['href'].startswith('http') and domain in a['href']
                }
                
                return {
                    'url': response.url,
                    'csp_headers': csp_headers,
                    'csp_domains': list(csp_domains),
                    'links': list(page_links)
                }
                
            except Exception as e:
                return {'url': url, 'error': str(e)}

        def _clean_url(self, url):
            """Normalize URL format"""
            url = re.sub(r'^(https?://|www\.)', '', url, flags=re.I)
            return url.split('?')[0].split('#')[0].strip('/').lower()

        def _process_engine(self, engine, query, pages, domain):
            """Threaded processing for a search engine"""
            found_urls = set()
            
            # Search phase
            for page in range(pages):
                time.sleep(random.uniform(*self.STEALTH_DELAY))
                try:
                    results = engine(query, page)
                    found_urls.update(
                        self._clean_url(url) 
                        for url in results 
                        if domain in url
                    )
                except Exception as e:
                    print(f"[!] Error in {engine.__name__}: {str(e)}")
                    continue
            
            # Threaded crawl phase
            engine_results = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_THREADS) as executor:
                futures = {
                    executor.submit(self._crawl_page, url, domain): url 
                    for url in found_urls
                }
                for future in tqdm(
                    concurrent.futures.as_completed(futures),
                    total=len(futures),
                    desc=f"Crawling {engine.__name__}"
                ):
                    engine_results.append(future.result())
            
            return engine_results

        def scan(self, query, domain, pages=1):
            """Main scanning method with threaded execution"""
            engines = {

                'Bing': self.bing_search,

            }
            
            final_results = {}
            for name, engine in engines.items():
                print(f"\n[+] Processing {name}")
                final_results[name] = self._process_engine(engine, query, pages, domain)
            
            return final_results

        # Search engines (unchanged from previous version)

        def bing_search(self, query, page):
            params = {'q': query, 'first': page*10+1}
            resp = self.session.get('https://www.bing.com/search', params=params)
            return [cite.text for cite in bsoup(resp.text, 'html.parser').find_all('cite')]

    def save_txt_report(results, filename):
        """Generate comprehensive TXT report"""
        with open(filename, 'w') as f:
            for engine, data in results.items():
                f.write(f"\n=== {engine.upper()} RESULTS ===\n")
                for item in data:
                    f.write(f"\nURL: {item.get('url', 'N/A')}\n")
                    
                    if 'error' in item:
                        f.write(f"ERROR: {item['error']}\n")
                        continue

                    # Headers
                    f.write("HEADERS:\n")
                    for header, policy in item.get('csp_headers', {}).items():
                        f.write(f"{header}: {policy}\n")
                    
                    # Extracted CSP Domains
                    if item.get('csp_domains'):
                        f.write("\nCSP DOMAINS:\n")
                        for domain in item['csp_domains']:
                            f.write(f"- {domain}\n")
                    
                    # Page Links
                    if item.get('links'):
                        f.write("\nINTERNAL LINKS:\n")
                        for link in item['links']:
                            f.write(f"- {link}\n")
                    
                    f.write("\n" + "="*50 + "\n")

    def main222():
        print("""
        ██████╗  ██████╗ ██████╗ ██╗  ██╗
        ██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝
        ██║  ██║██║   ██║██████╔╝█████╔╝ 
        ██║  ██║██║   ██║██╔══██╗██╔═██╗ 
        ██████╔╝╚██████╔╝██║  ██║██║  ██╗
        ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
        """)
        
        scanner = AdvancedDorkScanner()
        query = input("[?] Dork query (e.g. 'site:example.com'): ").strip()
        domain = input("[?] Target domain (e.g. example.com): ").strip()
        pages = int(input("[?] Pages per engine (Default 1): ") or 1)
        output_file = input("[?] Output file (e.g. report.txt): ").strip()
        
        results = scanner.scan(query, domain, pages)
        save_txt_report(results, output_file)
        
        print(f"\n[+] Scan complete! Results saved to {output_file}")

    main222()
#===NS LOOKUP===#
def nslookup():
    from requests.exceptions import RequestException, Timeout
    
    generate_ascii_banner("NS", "LOOKUP")

    def generate_url(website, page):
        if page == 1:
            return f"http://www.sitedossier.com/nameserver/{website}/{page}",
        else:
            return f"http://www.sitedossier.com/nameserver/{website}/{(page-1)*100 + 1}"

    def fetch_table_data(url, proxies=None):
        try:
            response = requests.get(url, proxies=proxies, timeout=4)
            response.raise_for_status()
            if response.status_code == 404:
                print("Job done.")
                return False, None
            if "Please enter the unique \"word\" below to confirm" in response.text:
                return False, None
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                table = soup.find('table')
                if table:
                    rows = table.find_all('tr')
                    data = []
                    for row in rows:
                        cells = row.find_all('td')
                        if cells:
                            row_data = [cell.text.strip() for cell in cells if cell.text.strip()]
                            if row_data:
                                data.append('\n'.join(row_data))
                    return True, data
                else:
                    print("No table found on page:")
        except Timeout:
            print("Timeout occurred while fetching data")
        except RequestException as e:
            print("Error occurred while fetching data:")
        return False, None

    def load_domains_from_file(filename):
        domains = []
        with open(filename, 'r') as file:
            for line in file:
                domains.append(line.strip())
        return domains

    def load_proxies_from_file(filename):
        proxies = []
        with open(filename, 'r') as file:
            for line in file:
                proxies.append(line.strip())
        return proxies

    def save_to_file(filename, data):
        with open(filename, 'a') as file:
            for item in data:
                file.write(item.strip())
                file.write('\n')

    def fetch_data(url, proxies, save_file, output_file):
        if proxies:
            proxy_index = 0
            while True:
                success, data = fetch_table_data(url, proxies={'http': proxies[proxy_index], 'https': proxies[proxy_index]})
                if success:
                    print("Data fetched successfully from:", url)
                    for item in data:
                        print(item)
                    if save_file == "yes":
                        save_to_file(output_file, data)
                    break
                else:
                    print("Retrying with a different proxy...")
                    proxy_index = (proxy_index + 1) % len(proxies)
                    if proxy_index == 0:
                        print("No more proxies to try. Moving to the next URL.")
                        break
        else:
            success, data = fetch_table_data(url)
            if success:
                print("Data fetched successfully from:", url)
                for item in data:
                    print(item)
                if save_file == "yes":
                    save_to_file(output_file, data)

    def nslookup_main():
        input_type = input("Choose input type (single/file): ").lower()
        
        if input_type == "single":
            website = input("Enter the website (e.g., ns1.google.com): ")
            num_pages = int(input("Enter the number of pages to fetch: "))
            urls = [generate_url(website, page) for page in range(1, num_pages + 1)]
            
        elif input_type == "file":
            domain_list_file = input("Enter the filename containing list of domains: ")
            domains = load_domains_from_file(domain_list_file)
            num_pages = int(input("Enter the number of pages to fetch per domain: "))
            urls = []
            for domain in domains:
                urls.extend([generate_url(domain, page) for page in range(1, num_pages + 1)])
        else:
            print("Invalid input type. Exiting.")
            return
        
        use_proxy = input("Do you want to use a proxy? (yes/no): ").lower()
        if use_proxy == "yes":
            proxy_list_name = input("Enter the proxy list file name: ")
            proxies = load_proxies_from_file(proxy_list_name)
        else:
            proxies = None
        
        save_file = input("Do you want to save the output data to a file? (yes/no): ").lower()
        if save_file == "yes":
            output_file = input("Enter the filename to save the output data (without extension): ") + ".txt"
        else:
            output_file = None
            print("Output will not be saved to a file.")


        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for url in urls:
                futures.append(executor.submit(fetch_data, url, proxies, save_file, output_file))

        for future in futures:
            future.result()

        print("All tasks completed.")

    nslookup_main()

#===DNSKEY===#
def dnskey():
    generate_ascii_banner("DNS", "KEY")

    def get_nameservers(domain):
        try:
            ns_records = dns.resolver.resolve(domain, 'NS')
            return [ns.target.to_text() for ns in ns_records]
        except Exception:
            return []

    def resolve_ns_to_ips(ns_list):
        ns_ips = []
        for ns in ns_list:
            try:
                answers = dns.resolver.resolve(ns, 'A')
                ns_ips.extend([ip.address for ip in answers])
            except dns.resolver.NoAnswer:
                try:
                    answers = dns.resolver.resolve(ns, 'AAAA')
                    ns_ips.extend([ip.address for ip in answers])
                except Exception:
                    pass
        return ns_ips

    def run_dns_query(server_ip, domain):
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = [server_ip]
            resolver.lifetime = resolver.timeout = 5
            answer = resolver.resolve(domain, dns.rdatatype.DNSKEY, raise_on_no_answer=False)
            return answer.response.to_text()
        except Exception:
            return None

    def extract_dnskey(output):
        keys = []
        for line in output.splitlines():
            if "DNSKEY" in line and not line.strip().startswith(';'):
                keys.append(line.strip())
        return keys

    def process_target(target, result_queue):
        try:
            ipaddress.ip_address(target)
            is_ip = True
        except ValueError:
            is_ip = False

        if not is_ip and not any(c.isdigit() for c in target.split('.')[-1]):
            # Domain processing
            ns_list = get_nameservers(target)
            if not ns_list:
                result_queue.put(('no_ns', target))
                return
            
            ns_ips = resolve_ns_to_ips(ns_list)
            if not ns_ips:
                result_queue.put(('no_ns_ip', target))
                return
            
            found_keys = False
            for ns_ip in ns_ips:
                result = run_dns_query(ns_ip, target)
                if not result:
                    continue
                
                keys = extract_dnskey(result)
                if keys:
                    found_keys = True
                    result_queue.put(('success', f"{target} | {ns_ip} | Found {len(keys)} DNSKEY(s)"))
                    for key in keys:
                        result_queue.put(('key', key))
            
            if not found_keys:
                result_queue.put(('no_keys', target))
        else:
            # IP processing
            result = run_dns_query(target, "com")
            if not result:
                result_queue.put(('query_failed', target))
                return
            
            keys = extract_dnskey(result)
            if keys:
                result_queue.put(('success', f"{target} | Found {len(keys)} DNSKEY(s)"))
                for key in keys:
                    result_queue.put(('key', key))
            else:
                result_queue.put(('no_keys', target))

    def main777():
        user_input = input("Enter IP / domain / CIDR / filename: ").strip()
        save_file = input("Enter output filename (default: dnskey_results.txt): ") or "dnskey_results.txt"
        targets = []
        result_queue = queue.Queue()
        max_threads = 20
        stats = {
            'total': 0,
            'with_keys': 0,
            'no_keys': 0,
            'no_ns': 0,
            'query_failed': 0
        }

        if os.path.isfile(user_input):
            with open(user_input) as f:
                targets = [line.strip() for line in f if line.strip()]
        else:
            try:
                ip_net = ipaddress.ip_network(user_input, strict=False)
                targets = [str(ip) for ip in ip_net.hosts()]
            except ValueError:
                targets = [user_input]

        stats['total'] = len(targets)
        print(f"Processing {stats['total']} targets with {max_threads} threads...")

        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(process_target, target, result_queue): target for target in targets}
            
            with tqdm(total=len(futures), desc="Processing") as pbar:
                for future in as_completed(futures):
                    pbar.update(1)

        # Process results
        output_lines = []
        while not result_queue.empty():
            result_type, data = result_queue.get()
            
            if result_type == 'success':
                output_lines.append(data)
                stats['with_keys'] += 1
            elif result_type == 'key':
                output_lines.append(data)
            elif result_type == 'no_keys':
                stats['no_keys'] += 1
            elif result_type == 'no_ns':
                stats['no_ns'] += 1
            elif result_type == 'query_failed':
                stats['query_failed'] += 1

        # Display results
        for line in output_lines:
            print(line)

        # File handling - always create but only write if we have results
        if output_lines:
            with open(save_file, "w") as f_out:
                f_out.write("\n".join(output_lines))
            print(f"\n✅ Results saved to {save_file}")
        else:
            # Create empty file to confirm path is valid
            open(save_file, "a").close()
            print(f"\n❌ No DNSKEY records found - created empty file {save_file}")

        # Show statistics
        print("\n=== Statistics ===")
        print(f"Total targets processed: {stats['total']}")
        print(f"Targets with DNSKEYs: {stats['with_keys']}")
        print(f"Targets without DNSKEYs: {stats['no_keys']}")
        print(f"Targets with no nameservers: {stats['no_ns']}")
        print(f"Failed queries: {stats['query_failed']}")

    main777()

#===PAYLOAD HUNTER===#
def payloadhunter():

    generate_ascii_banner("PAYLOAD", "HUNTER")

    import subprocess
    import re
    import os
    import ipaddress
    import socket
    from pathlib import Path
    from urllib.parse import urlparse
    from colorama import Fore, Style, init
    from datetime import datetime
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import uuid
    import atexit
    import signal
    import sys

    init(autoreset=True)

    # Global temp file tracker
    temp_files = []

    def cleanup_temp_files():
        for file in temp_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except Exception:
                pass

    # Register cleanup on exit
    atexit.register(cleanup_temp_files)

    interrupted = False

    def signal_handler(signum, frame):
        global interrupted
        interrupted = True
        print(f"\n{Fore.RED}Received interrupt signal. Cleaning up and returning to menu...{Style.RESET_ALL}")
        cleanup_temp_files()
        
        # Set a short delay to allow cleanup
        time.sleep(1)
        clear_screen()
        
        # Exit any ongoing operations and return to menu
        sys.exit(0)

    def is_ip(address):
        try:
            ipaddress.ip_address(address)
            return True
        except ValueError:
            return False

    def is_cidr(address):
        try:
            ipaddress.ip_network(address, strict=False)
            return True
        except ValueError:
            return False

    def is_domain(address):
        try:
            socket.gethostbyname(address)
            return True
        except socket.gaierror:
            return False

    def is_file(path):
        return Path(path).is_file()

    def read_targets_from_file(file_path):
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            print(f"{Fore.RED}Error reading file: {str(e)}")
            return []

    def expand_cidr(cidr):
        try:
            network = ipaddress.ip_network(cidr, strict=False)
            return [str(host) for host in network.hosts()]
        except Exception as e:
            print(f"{Fore.RED}Error expanding CIDR: {str(e)}")
            return []

    def get_targets(prompt):
        while True:
            target = input(f"{Fore.YELLOW}{prompt}{Style.RESET_ALL}").strip()
            if not target:
                print(f"{Fore.RED}Input cannot be empty")
                continue
            if is_file(target):
                targets = read_targets_from_file(target)
                if targets:
                    print(f"{Fore.GREEN}Loaded {len(targets)} targets from file")
                    return targets
                continue
            if is_cidr(target):
                targets = expand_cidr(target)
                if targets:
                    print(f"{Fore.GREEN}Expanded to {len(targets)} IPs from CIDR")
                    return targets
                continue
            if is_ip(target) or is_domain(target):
                return [target]
            print(f"{Fore.RED}Invalid input - must be IP, domain, CIDR, or file path")

    def get_proxy():
        while True:
            proxy = input(f"{Fore.YELLOW}Enter your proxy (e.g., proxy:port or http://proxy:port): {Style.RESET_ALL}").strip()
            if not proxy.startswith(('http://', 'https://')):
                proxy = 'http://' + proxy
            try:
                parsed = urlparse(proxy)
                if all([parsed.scheme, parsed.netloc]):
                    return proxy
                print(f"{Fore.RED}Invalid format. Use proxy:port or http://proxy:port")
            except:
                print(f"{Fore.RED}Invalid proxy format")

    def build_payloads(ssh, host):
        return [
            f"CONNECT /cdn-cgi/trace HTTP/1.1[crlf]Host: {host}[crlf][crlf]CF-RAY / HTTP/1.1[crlf]Host: {ssh}[crlf]Upgrade: Websocket[crlf]Connection: Keep-Alive[crlf]User-Agent: [ua][crlf]Upgrade: websocket[crlf][crlf]",
            f"POST / HTTP/1.1[crlf]Host: {host}[crlf]Expect: 100-continue[crlf][crlf]GET- / HTTP/1.1[crlf]Host: {ssh}[crlf]Upgrade: Websocket[crlf][crlf]",
            f"POST / HTTP/1.1[crlf]Host: {host}[crlf][crlf]CF-RAY / HTTP/1.1[crlf]Host: {ssh}[crlf]Upgrade: websocket[crlf]Connection: Keep-Alive[crlf]User-Agent: [ua][crlf]Upgrade: websocket[crlf][crlf]",
            f"CONNECT {host} HTTP/1.1[crlf]Host: {ssh}[crlf]X-Forward-Host: {ssh}[crlf]X-Forwarded-For: 1.1.1.1[crlf]Connection: Keep-Alive[crlf]User-Agent: Mozilla/5.0 (Linux; Android 10)[crlf]Proxy-Connection: Keep-Alive[crlf][crlf]",
            f"CONNECT {host} HTTP/1.1[crlf]Host: {ssh}[crlf]X-Real-IP: 192.168.1.1[crlf]Connection: Keep-Alive[crlf][crlf]",
            f"CONNECT {host} HTTP/1.1[crlf]Host: {ssh}[crlf]Upgrade: websocket[crlf]Connection: Upgrade[crlf]CF-RAY: 8a1b2c3d4e5f6g7h[crlf]User-Agent: [ua][crlf][crlf]",
            f"CONNECT {host} HTTP/1.1[crlf]Host: {ssh}[crlf]X-Forwarded-Host: {ssh}[crlf]X-Forwarded-For: 1.1.1.1[crlf]Front-End-Https: on[crlf]User-Agent: Mozilla/5.0[crlf][crlf]",
            f"CONNECT / HTTP/1.1[crlf]Host: {host}[crlf]X-Forward-Host: {ssh}[crlf]X-Forwarded-For: 1.1.1.1[crlf]Connection: Keep-Alive[crlf]User-Agent: Mozilla/5.0 (Linux; Android 10)[crlf]Proxy-Connection: Keep-Alive[crlf][crlf]",
            f"CONNECT / HTTP/1.1[crlf]Host: {host}[crlf]X-Real-IP: {ssh}[crlf]Connection: Keep-Alive[crlf][crlf]",
            f"CONNECT / HTTP/1.1[crlf]Host: {host}[crlf]Upgrade: websocket[crlf]Connection: Upgrade[crlf]CF-RAY: 8a1b2c3d4e5f6g7h[crlf]User-Agent: [ua][crlf][crlf]",
            f"CONNECT / HTTP/1.1[crlf]Host: {host}[crlf]X-Forwarded-Host: {ssh}[crlf]X-Forwarded-For: 1.1.1.1[crlf]Front-End-Https: on[crlf]User-Agent: Mozilla/5.0[crlf][crlf]",

        ]

    def test_payload(proxy, target, payload, payload_num, results_file=None):
        try:
            curl_payload = payload.replace("[crlf]", "\r\n")
            temp_file = f"temp_payload_{uuid.uuid4().hex}.txt"
            temp_files.append(temp_file)
            with open(temp_file, "w") as f:
                f.write(curl_payload)
            cmd = [
                "curl", "-s", "-i", "-x", proxy,
                "--max-time", "3",
                "--data-binary", f"@{temp_file}",
                f"http://{target}"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if os.path.exists(temp_file):
                os.remove(temp_file)
                temp_files.remove(temp_file)

            status_line = result.stdout.splitlines()[0] if result.stdout else ""

            if any(status_line.startswith(f"HTTP/1.1 {code}") for code in ("200", "403")):
                result_data = {
                    "target": target,
                    "payload_num": payload_num,
                    "payload": payload,
                    "response": result.stdout,
                    "status": "SUCCESS"
                }
                
                # Save successful result immediately if results_file is specified
                if results_file:
                    try:
                        with open(results_file, 'a') as f:
                            f.write(f"\n=== Target: {result_data['target']} ===\n")
                            f.write(f"=== Payload {result_data['payload_num']} ===\n")
                            f.write(f"Status: {result_data['status']}\n")
                            f.write(f"\nPayload Used:\n{result_data['payload']}\n")
                            f.write(f"\nResponse:\n{result_data['response']}\n")
                            f.write("\n" + "="*40 + "\n")
                    except Exception as e:
                        print(f"{Fore.RED}Failed to save result to file: {str(e)}")
                
                return result_data
            else:
                return {
                    "target": target,
                    "payload_num": payload_num,
                    "payload": payload,
                    "response": result.stdout,
                    "status": "NON_200"
                }

        except Exception as e:
            return {
                "target": target,
                "payload_num": payload_num,
                "payload": payload,
                "response": str(e),
                "status": "ERROR"
            }

    def get_results_filename():
        while True:
            filename = input(f"{Fore.CYAN}Enter filename to save successful results (e.g., results.txt): {Style.RESET_ALL}").strip()
            if not filename:
                print(f"{Fore.RED}Filename cannot be empty.")
                continue
            try:
                # Create/clear the file and write header
                with open(filename, 'w') as f:
                    f.write(f"=== Proxy Test Results ===\n")
                    f.write(f"Test Time: {datetime.now()}\n\n")
                return filename
            except Exception as e:
                print(f"{Fore.RED}Failed to create results file: {str(e)}")

    def main111():
        from math import ceil
        from tqdm import tqdm

        def chunked(iterable, size):
            for i in range(0, len(iterable), size):
                yield iterable[i:i + size]

        try:
            proxy = get_proxy()
            ssh = get_targets("Enter SSH server (e.g us1.vip.xyz): ")[0]
            bug_hosts = get_targets("Enter bug host(s) (domain/IP/CIDR/file.txt): ")
            
            results_file = get_results_filename()
            print(f"{Fore.GREEN}Successful results will be saved to: {results_file}")

            all_results = []
            max_threads = 2
            batch_size = 50

            print(f"{Fore.CYAN}\n[~] Processing in batches of {batch_size} hosts using {max_threads} threads each...{Style.RESET_ALL}")

            for batch_num, batch in enumerate(chunked(bug_hosts, batch_size), 1):
                if interrupted:
                    raise KeyboardInterrupt()
                    
                print(f"\n{Fore.YELLOW}=== Batch {batch_num} ({len(batch)} targets) ==={Style.RESET_ALL}")
                with ThreadPoolExecutor(max_workers=max_threads) as executor:
                    futures = []
                    for host in batch:
                        if interrupted:
                            raise KeyboardInterrupt()
                            
                        for i, payload in enumerate(build_payloads(ssh, host), 1):
                            futures.append(executor.submit(test_payload, proxy, host, payload, i, results_file))

                    batch_success = 0
                    for future in tqdm(as_completed(futures), total=len(futures), desc=f"Batch {batch_num} progress", leave=True):
                        if interrupted:
                            raise KeyboardInterrupt()
                            
                        result = future.result()
                        if result['status'] == "SUCCESS":
                            all_results.append(result)
                            batch_success += 1

                print(f"{Fore.GREEN}[✓] Batch {batch_num} complete — {batch_success} successful{Style.RESET_ALL}")

            print(f"\n{Fore.CYAN}=== Summary ==={Style.RESET_ALL}")
            print(f"Total successful: {Fore.GREEN}{len(all_results)}{Style.RESET_ALL}")
            print(f"Results saved to: {results_file}")

        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Operation interrupted by user.{Style.RESET_ALL}")
            cleanup_temp_files()
            time.sleep(1)
            clear_screen()
            return
    main111()

#===PAYLOAD HUNTER 2===#
def payloadhunter2():

    generate_ascii_banner("PAYLOAD", "HUNTER 2")
    import subprocess
    import random
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from tqdm import tqdm
    import tempfile
    import os
    import socket
    import tldextract
    import uuid
    import re
    import threading

    # Configuration
    PROXY_TIMEOUT = 3
    THREADS = 50
    DNS_THREADS = 50
    TARGET_STATUS_CODES = {101, 200, 301, 405, 409}  # Only these status codes will be saved
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
    ]
    COMMON_PORTS = [80, 443]
    TARGET_HOST = "us7.ws-tun.me"
    SUCCESS_KEYWORDS = ["websocket", "cloudflare", "cf-ray", "200", "101", "connection established"]
    FAIL_KEYWORDS = ["forbidden", "blocked", "error", "invalid", "bad request"]
    DNS_TIMEOUT = 3

    # Payload templates
    PAYLOADS = [
        "GET http://[host]/ HTTP/1.1\r\nHost: us7.ws-tun.me\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nUser-Agent: [user_agent]\r\nSec-WebSocket-Version: 13\r\nSec-WebSocket-Key: [random_key]\r\n\r\n",
        "POST http://[host]/ HTTP/1.1\r\nHost: us7.ws-tun.me\r\nUser-Agent: [user_agent]\r\nContent-Length: 0\r\nExpect: 100-continue\r\n\r\n",
        "GET / HTTP/1.1\r\nHost: [host]\r\n\r\nCF-RAY / HTTP/1.1\r\nHost: us7.ws-tun.me\r\nUpgrade: Websocket\r\nConnection: Keep-Alive\r\nUser-Agent: [user_agent]\r\nUpgrade: websocket\r\n\r\n",
    ]

    class ResultSaver:
        def __init__(self, filename):
            self.filename = filename
            self.lock = threading.Lock()
            with open(self.filename, 'w', encoding='utf-8') as f:
                f.write("=== WORKING PROXIES (Filtered by Status Code) ===\n\n")
            
        def save_result(self, result):
            if result['status'] in TARGET_STATUS_CODES:  # Only save if status matches
                with self.lock:
                    with open(self.filename, 'a', encoding='utf-8') as f:
                        f.write(f"Proxy: {result['proxy']}\n")
                        f.write(f"Status: {result['status']} | Tested Against: {result['tested_against']}\n")
                        f.write(f"Reason: {result['reason']}\n")
                        f.write(f"Payload: {result['payload']}\n\n")

    def get_root_domain(domain):
        ext = tldextract.extract(domain)
        return f"{ext.domain}.{ext.suffix}" if ext.suffix else domain

    def resolve_domain(domain):
        try:
            socket.setdefaulttimeout(DNS_TIMEOUT)
            ips = set()
            try:
                addrinfo = socket.getaddrinfo(domain, None)
                for info in addrinfo:
                    ip = info[4][0]
                    ips.add(ip)
                return list(ips)
            except (socket.gaierror, socket.herror, socket.timeout):
                return []
        except Exception:
            return []

    def resolve_domains_parallel(domains):
        resolved = {}
        with ThreadPoolExecutor(max_workers=DNS_THREADS) as executor:
            future_to_domain = {executor.submit(resolve_domain, domain): domain for domain in domains}
            for future in as_completed(future_to_domain):
                domain = future_to_domain[future]
                try:
                    ips = future.result()
                    if ips:
                        resolved[domain] = ips
                except Exception:
                    continue
        return resolved

    def generate_proxy_urls(ip_or_domain):
        urls = []
        for port in COMMON_PORTS:
            urls.extend([
                f"http://{ip_or_domain}:{port}",
                f"https://{ip_or_domain}:{port}",

            ])
        return urls

    def generate_random_key():
        return ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(16))

    def generate_payloads(host):
        payload_list = []
        user_agent = random.choice(USER_AGENTS)
        random_key = generate_random_key()
        
        for payload in PAYLOADS:
            formatted_payload = payload.replace("[host]", host)
            formatted_payload = formatted_payload.replace("[host_port]", f"{host}:443")
            formatted_payload = formatted_payload.replace("[user_agent]", user_agent)
            formatted_payload = formatted_payload.replace("[random_key]", random_key)
            
            if "?" in formatted_payload:
                formatted_payload = formatted_payload.replace("?", f"?_cachebust={uuid.uuid4()}&")
            elif "HTTP/1.1" in formatted_payload:
                parts = formatted_payload.split("\r\n")
                first_line = parts[0]
                if " " in first_line:
                    path = first_line.split(" ")[1]
                    new_path = f"{path}?_cachebust={uuid.uuid4()}"
                    parts[0] = first_line.replace(path, new_path)
                    formatted_payload = "\r\n".join(parts)
            
            payload_list.append(formatted_payload)
        
        return payload_list

    def analyze_response(response_text):
        if not response_text:
            return False, "Empty response", 0
        
        status_match = re.search(r'HTTP/\d\.\d (\d{3})', response_text)
        status_code = int(status_match.group(1)) if status_match else 0
        
        if "connection established" in response_text.lower():
            return True, "Connection established", 200
        
        if "upgrade: websocket" in response_text.lower() and "101" in response_text:
            return True, "WebSocket upgrade", 101
        
        if status_code in TARGET_STATUS_CODES:  # Only consider our target status codes
            return True, f"Status: {status_code}", status_code
        
        return False, f"Status: {status_code}", status_code

    def test_proxy(proxy_url, target_host, result_saver):
        payloads = generate_payloads(target_host)
        
        for payload in payloads:
            try:
                with tempfile.NamedTemporaryFile(mode='w+', delete=False, encoding='utf-8') as tmp:
                    tmp.write(payload)
                    tmp_path = tmp.name

                cmd = [
                    "curl", "-s", "-i",
                    "-x", proxy_url,
                    "--connect-timeout", str(PROXY_TIMEOUT),
                    "--max-time", str(PROXY_TIMEOUT),
                    "-H", f"User-Agent: {random.choice(USER_AGENTS)}",
                    "-H", "Accept: */*",
                    "--data-binary", f"@{tmp_path}",
                    target_host
                ]
                
                if "socks" in proxy_url:
                    cmd.extend(["--socks5-gssapi-nec"])
                
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=PROXY_TIMEOUT+2)
                except subprocess.TimeoutExpired:
                    continue
                
                try:
                    os.remove(tmp_path)
                except:
                    pass

                response_text = result.stdout
                is_success, reason, status_code = analyze_response(response_text)
                
                if is_success and status_code in TARGET_STATUS_CODES:
                    result_data = {
                        'proxy': proxy_url,
                        'status': status_code,
                        'size': len(response_text),
                        'payload': payload.replace("\r\n", "[crlf]"),
                        'response': response_text[:500] + "..." if len(response_text) > 500 else response_text,
                        'reason': reason,
                        'tested_against': target_host
                    }
                    result_saver.save_result(result_data)
                    return result_data
                    
            except Exception:
                continue
        
        return {'proxy': proxy_url, 'error': 'No matching responses', 'tested_against': target_host}

    def load_targets(input_str):
        if os.path.isfile(input_str) and input_str.lower().endswith(".txt"):
            with open(input_str, "r", encoding="utf-8") as f:
                targets = [line.strip() for line in f if line.strip()]
        else:
            targets = [input_str.strip()]
        
        domains_to_resolve = set()
        for target in targets:
            domain = target.split(':')[0]
            domains_to_resolve.add(domain)
            root_domain = get_root_domain(domain)
            if root_domain != domain:
                domains_to_resolve.add(root_domain)
        
        resolved_domains = resolve_domains_parallel(domains_to_resolve)
        
        expanded_targets = []
        domain_to_ips = {}
        
        for target in targets:
            domain = target.split(':')[0]
            expanded_targets.append(domain)
            
            if domain in resolved_domains:
                domain_to_ips[domain] = resolved_domains[domain]
                for ip in resolved_domains[domain]:
                    if ip not in expanded_targets:
                        expanded_targets.append(ip)
            
            root_domain = get_root_domain(domain)
            if root_domain != domain and root_domain in resolved_domains and root_domain not in domain_to_ips:
                domain_to_ips[root_domain] = resolved_domains[root_domain]
                if root_domain not in expanded_targets:
                    expanded_targets.append(root_domain)
                for ip in resolved_domains[root_domain]:
                    if ip not in expanded_targets:
                        expanded_targets.append(ip)
        
        return expanded_targets, domain_to_ips

    def process_target(target, domain_to_ips, result_saver):
        test_matrix = []
        matching_results = []

        all_test_targets = set()
        for domain, ips in domain_to_ips.items():
            all_test_targets.add(domain)
            all_test_targets.update(ips)

        if target.replace('.', '').isdigit() or ':' in target:
            ip_proxies = generate_proxy_urls(target)
            for proxy in ip_proxies:
                for test_target in all_test_targets:
                    if test_target != target:
                        test_matrix.append((proxy, test_target))
        else:
            root_domain = get_root_domain(target)
            is_subdomain = (root_domain != target)

            target_ips = domain_to_ips.get(target, [])
            root_ips = domain_to_ips.get(root_domain, []) if is_subdomain else []

            target_proxies = generate_proxy_urls(target)
            root_proxies = generate_proxy_urls(root_domain) if is_subdomain else []

            for proxy in target_proxies:
                if is_subdomain:
                    test_matrix.append((proxy, root_domain))
                    for root_ip in root_ips:
                        test_matrix.append((proxy, root_ip))
                else:
                    test_matrix.append((proxy, target))
                    for target_ip in target_ips:
                        test_matrix.append((proxy, target_ip))

            if is_subdomain:
                for proxy in root_proxies:
                    test_matrix.append((proxy, target))
                    for target_ip in target_ips:
                        test_matrix.append((proxy, target_ip))

        print(f"\n[+] Testing {len(test_matrix)} combos for {target}")

        with tqdm(total=len(test_matrix), desc=f"Testing {target}") as pbar:
            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                futures = {
                    executor.submit(test_proxy, proxy, test_target, result_saver): (proxy, test_target)
                    for proxy, test_target in test_matrix
                }
                for future in as_completed(futures):
                    proxy, test_target = futures[future]
                    res = future.result()
                    if not res.get('error'):
                        print(f"[+] MATCH FOUND: {res['proxy']} → {res['tested_against']} (Status: {res['status']})")
                        matching_results.append(res)
                    pbar.update(1)

        return matching_results

    def main334455():
        print("=== Status-Specific Proxy Tester ===")
        print(f"Target Status Codes: {TARGET_STATUS_CODES}")
        print(f"Threads: {THREADS}, Timeout: {PROXY_TIMEOUT}s\n")
        
        user_input = input("Enter IP/domain or .txt file: ").strip()
        output_file = input("Enter output file name (default: filtered_results.txt): ").strip() or "filtered_results.txt"
        
        result_saver = ResultSaver(output_file)
        targets, domain_to_ips = load_targets(user_input)
        matching_results = []
        
        for target in targets:
            results = process_target(target, domain_to_ips, result_saver)
            matching_results.extend(results)

        print(f"\n[+] Total matching proxies found: {len(matching_results)}")
        print(f"[+] Filtered results saved to {output_file}")


    main334455()

#===ZONE WALK===#
def zonewalk():
    import dns.resolver
    from dns.resolver import Resolver
    from ipaddress import ip_network, ip_address
    import concurrent.futures as futures
    import time
    import os

    def configure_resolver():
        # Create resolver with no automatic configuration
        resolver = dns.resolver.Resolver(configure=False)  # Use full module path
        
        # Termux-specific configuration
        termux_resolv_conf = '/data/data/com.termux/files/usr/etc/resolv.conf'
        
        if os.path.exists(termux_resolv_conf):
            try:
                # Read Termux's resolv.conf manually
                with open(termux_resolv_conf) as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('nameserver'):
                            resolver.nameservers = [line.split()[1]]
                            break
            except:
                # Fallback to Android system DNS properties
                try:
                    dns_servers = []
                    for i in range(1, 3):
                        dns_server = os.popen(f'getprop net.dns{i}').read().strip()  # Changed variable name
                        if dns_server:
                            dns_servers.append(dns_server)
                    
                    resolver.nameservers = dns_servers if dns_servers else ['8.8.8.8', '8.8.4.4']
                except:
                    resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        else:
            # Standard Linux fallback
            resolver.nameservers = ['8.8.8.8', '8.8.4.4']
        
        resolver.timeout = 5
        resolver.lifetime = 5
        return resolver

    generate_ascii_banner("ZONE", "WALK")

    def check_wildcard(resolver, domain):
        """Check if wildcard resolution is configured for a domain."""
        testname = generate_testname(12, domain)
        ips = resolver.get_a(testname)
        
        if not ips:
            return None

        wildcard_ips = set()
        print_debug("Wildcard resolution is enabled on this domain")
        
        for ip in ips:
            print_debug(f"It is resolving to {ip[2]}")
            wildcard_ips.add(ip[2])
        
        print_debug("All queries will resolve to this list of addresses!")
        return wildcard_ips

    def check_nxdomain_hijack(nameserver, test_domain="com"):
        """Check if a nameserver performs NXDOMAIN hijacking."""
        testname = generate_testname(20, test_domain)
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [nameserver]
        resolver.timeout = 5.0

        addresses = []
        record_types = ('A', 'AAAA')

        for record_type in record_types:
            try:
                answers = resolver.resolve(testname, record_type, tcp=True)
            except (dns.resolver.NoNameservers, dns.resolver.NXDOMAIN,
                    dns.exception.Timeout, dns.resolver.NoAnswer,
                    socket.error, dns.query.BadResponse):
                continue

            for answer in answers.response.answer:
                for rdata in answer:
                    if rdata.rdtype == 5:  # CNAME record
                        target = rdata.target.to_text().rstrip('.')
                        addresses.append(target)
                    else:
                        addresses.append(rdata.address)

        if not addresses:
            return False

        address_list = ", ".join(addresses)
        print_error(f"Nameserver {nameserver} performs NXDOMAIN hijacking")
        print_error(f"It resolves nonexistent domains to {address_list}")
        print_error("This server has been removed from the nameserver list!")
        return True

    def brute_tlds(resolver, domain, tld_lists=None, verbose=False, threads=10):
        """
        Perform TLD brute-forcing for a given domain.
        
        Args:
            resolver: DNS resolver object
            domain: Domain to test (e.g., "example")
            tld_lists: Dictionary of TLD categories (optional)
            verbose: Show verbose output
            threads: Number of threads to use (default: 10)
            
        Returns:
            List of found records
        """
        if tld_lists is None:
            tld_lists = {
                'itld': ['arpa'],
                'gtld': ['com', 'net', 'org', 'info', 'co'],
                'grtld':  ['biz', 'name', 'online', 'pro', 'shop', 'site', 'top', 'xyz'],

                'stld': ['aero', 'app', 'asia', 'cat', 'coop', 'dev', 'edu', 'gov', 'int', 'jobs', 'mil', 'mobi', 'museum', 'post',
                            'tel', 'travel', 'xxx'],

                'cctld': ['ac', 'ad', 'ae', 'af', 'ag', 'ai', 'al', 'am', 'an', 'ao', 'aq', 'ar', 'as', 'at', 'au', 'aw', 'ax', 'az',
                            'ba', 'bb', 'bd', 'be', 'bf', 'bg', 'bh', 'bi', 'bj', 'bl', 'bm', 'bn', 'bo', 'bq', 'br', 'bs', 'bt', 'bv',
                            'bw', 'by', 'bz', 'ca', 'cc', 'cd', 'cf', 'cg', 'ch', 'ci', 'ck', 'cl', 'cm', 'cn', 'co', 'cr', 'cu', 'cv',
                            'cw', 'cx', 'cy', 'cz', 'de', 'dj', 'dk', 'dm', 'do', 'dz', 'ec', 'ee', 'eg', 'eh', 'er', 'es', 'et', 'eu',
                            'fi', 'fj', 'fk', 'fm', 'fo', 'fr', 'ga', 'gb', 'gd', 'ge', 'gf', 'gg', 'gh', 'gi', 'gl', 'gm', 'gn', 'gp',
                            'gq', 'gr', 'gs', 'gt', 'gu', 'gw', 'gy', 'hk', 'hm', 'hn', 'hr', 'ht', 'hu', 'id', 'ie', 'il', 'im', 'in',
                            'io', 'iq', 'ir', 'is', 'it', 'je', 'jm', 'jo', 'jp', 'ke', 'kg', 'kh', 'ki', 'km', 'kn', 'kp', 'kr', 'kw',
                            'ky', 'kz', 'la', 'lb', 'lc', 'li', 'lk', 'lr', 'ls', 'lt', 'lu', 'lv', 'ly', 'ma', 'mc', 'md', 'me', 'mf',
                            'mg', 'mh', 'mk', 'ml', 'mm', 'mn', 'mo', 'mp', 'mq', 'mr', 'ms', 'mt', 'mu', 'mv', 'mw', 'mx', 'my', 'mz',
                            'na', 'nc', 'ne', 'nf', 'ng', 'ni', 'nl', 'no', 'np', 'nr', 'nu', 'nz', 'om', 'pa', 'pe', 'pf', 'pg', 'ph',
                            'pk', 'pl', 'pm', 'pn', 'pr', 'ps', 'pt', 'pw', 'py', 'qa', 're', 'ro', 'rs', 'ru', 'rw', 'sa', 'sb', 'sc',
                            'sd', 'se', 'sg', 'sh', 'si', 'sj', 'sk', 'sl', 'sm', 'sn', 'so', 'sr', 'ss', 'st', 'su', 'sv', 'sx', 'sy',
                            'sz', 'tc', 'td', 'tf', 'tg', 'th', 'tj', 'tk', 'tl', 'tm', 'tn', 'to', 'tp', 'tr', 'tt', 'tv', 'tw', 'tz',
                            'ua', 'ug', 'uk', 'um', 'us', 'uy', 'uz', 'va', 'vc', 've', 'vg', 'vi', 'vn', 'vu', 'wf', 'ws', 'yt', 'za',
                            'zm', 'zw']  # truncated for brevity
            }

        domain_main = domain.split(".")[0] if "." in domain else domain
        total_tlds = list(set(tld_lists['itld'] + tld_lists['gtld'] + 
                            tld_lists['grtld'] + tld_lists['stld']))
        
        # Calculate estimated duration
        total_queries = len(total_tlds) + len(tld_lists['cctld']) + min(len(tld_lists['cctld']), len(total_tlds))
        duration = time.strftime('%H:%M:%S', time.gmtime(total_queries / 3))
        print(f"[+] The operation could take up to: {duration}")

        found_records = []
        
        try:
            with futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures_map = {}
                
                # Single TLD queries (example.com, example.org, etc.)
                for tld in total_tlds:
                    query = f"{domain_main}.{tld}"
                    if verbose:
                        print(f"[*] Trying: {query}")
                    futures_map[executor.submit(resolver.resolve, query, 'A')] = ('A', query)
                    futures_map[executor.submit(resolver.resolve, query, 'AAAA')] = ('AAAA', query)
                    
                # Country code TLD queries (example.co.uk, example.com.br, etc.)
                for cc in tld_lists['cctld']:
                    query = f"{domain_main}.{cc}"
                    if verbose:
                        print(f"[*] Trying: {query}")
                    futures_map[executor.submit(resolver.resolve, query, 'A')] = ('A', query)
                    futures_map[executor.submit(resolver.resolve, query, 'AAAA')] = ('AAAA', query)
                    
                    # Country code + TLD combinations
                    for tld in total_tlds:
                        query = f"{domain_main}.{cc}.{tld}"
                        if verbose:
                            print(f"[*] Trying: {query}")
                        futures_map[executor.submit(resolver.resolve, query, 'A')] = ('A', query)
                        futures_map[executor.submit(resolver.resolve, query, 'AAAA')] = ('AAAA', query)

                # Process results
                for future in futures.as_completed(futures_map):
                    record_type, query = futures_map[future]
                    try:
                        answer = future.result()
                        for rrset in answer.response.answer:
                            for rdata in rrset:
                                if rdata.rdtype in (dns.rdatatype.A, dns.rdatatype.AAAA):
                                    print(f"[+] Found: {query} {rdata.address}")
                                    found_records.append({
                                        "type": "A" if rdata.rdtype == dns.rdatatype.A else "AAAA",
                                        "name": query,
                                        "address": rdata.address
                                    })
                    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                        continue
                    except Exception as e:
                        if verbose:
                            print(f"[!] Error processing {query}: {e}")

        except Exception as e:
            print(f"[!] Error in brute_tlds: {e}")

        print(f"[+] Found {len(found_records)} records")
        return found_records

    def brute_srv(resolver, domain, srv_records=None, verbose=False, threads=None):
        """
        Brute-force SRV records for a domain.
        
        Args:
            resolver: DNS resolver object
            domain: Domain to test
            srv_records: List of SRV record prefixes to test
            verbose: Show verbose output
            threads: Number of threads to use
            
        Returns:
            List of found SRV records
        """
        if srv_records is None:
            srv_records = [
            '_gc._tcp.', '_kerberos._tcp.', '_kerberos._udp.', '_ldap._tcp.',
            '_test._tcp.', '_sips._tcp.', '_sip._udp.', '_sip._tcp.', '_aix._tcp.',
            '_aix._tcp.', '_finger._tcp.', '_ftp._tcp.', '_http._tcp.', '_nntp._tcp.',
            '_telnet._tcp.', '_whois._tcp.', '_h323cs._tcp.', '_h323cs._udp.',
            '_h323be._tcp.', '_h323be._udp.', '_h323ls._tcp.', '_https._tcp.',
            '_h323ls._udp.', '_sipinternal._tcp.', '_sipinternaltls._tcp.',
            '_sip._tls.', '_sipfederationtls._tcp.', '_jabber._tcp.',
            '_xmpp-server._tcp.', '_xmpp-client._tcp.', '_imap.tcp.',
            '_certificates._tcp.', '_crls._tcp.', '_pgpkeys._tcp.',
            '_pgprevokations._tcp.', '_cmp._tcp.', '_svcp._tcp.', '_crl._tcp.',
            '_ocsp._tcp.', '_PKIXREP._tcp.', '_smtp._tcp.', '_hkp._tcp.',
            '_hkps._tcp.', '_jabber._udp.', '_xmpp-server._udp.', '_xmpp-client._udp.',
            '_jabber-client._tcp.', '_jabber-client._udp.', '_kerberos.tcp.dc._msdcs.',
            '_ldap._tcp.ForestDNSZones.', '_ldap._tcp.dc._msdcs.', '_ldap._tcp.pdc._msdcs.',
            '_ldap._tcp.gc._msdcs.', '_kerberos._tcp.dc._msdcs.', '_kpasswd._tcp.', '_kpasswd._udp.',
            '_imap._tcp.', '_imaps._tcp.', '_submission._tcp.', '_pop3._tcp.', '_pop3s._tcp.',
            '_caldav._tcp.', '_caldavs._tcp.', '_carddav._tcp.', '_carddavs._tcp.',
            '_x-puppet._tcp.', '_x-puppet-ca._tcp.', '_autodiscover._tcp.']

        found_records = []
        
        try:
            with futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures_map = {}
                
                for srv_prefix in srv_records:
                    query = srv_prefix + domain
                    if verbose:
                        print_status(f"Trying {query}...")
                    futures_map[executor.submit(resolver.get_srv, query)] = query

                for future in futures.as_completed(futures_map):
                    try:
                        result = future.result()
                        if result:
                            for record in result:
                                print_good(f"\t {record[0]} {record[1]} {record[2]} {record[3]} {record[4]}")
                                found_records.append({
                                    "type": record[0],
                                    "name": record[1],
                                    "target": record[2],
                                    "address": record[3],
                                    "port": record[4]
                                })
                    except Exception as e:
                        if verbose:
                            print_error(f"Error processing {futures_map[future]}: {e}")

        except Exception as e:
            print_error(f"Error in brute_srv: {e}")

        if not found_records:
            print_error(f"No SRV Records Found for {domain}")

        print_good(f"{len(found_records)} Records Found")
        return found_records

    def brute_reverse(resolver, ip_list, verbose=False, threads=10):
        """
        Perform reverse DNS lookups for a list of IP addresses.
        
        Args:
            resolver: DNS resolver object
            ip_list: List of IP addresses to check
            verbose: Show verbose output
            threads: Number of threads to use
            
        Returns:
            List of found PTR records
        """
        print(f"[+] Performing Reverse Lookup on {len(ip_list)} IPs")
        found_records = []
        
        try:
            with futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures_map = {}
                
                for ip in ip_list:
                    ip_str = str(ip)
                    if verbose:
                        print(f"[*] Trying {ip_str}")
                    futures_map[executor.submit(resolver.resolve, 
                                            f"{ip_str.split('.')[3]}.{ip_str.split('.')[2]}.{ip_str.split('.')[1]}.{ip_str.split('.')[0]}.in-addr.arpa", 
                                            'PTR')] = ip_str

                for future in futures.as_completed(futures_map):
                    ip_str = futures_map[future]
                    try:
                        answer = future.result()
                        for rrset in answer.response.answer:
                            for rdata in rrset:
                                if rdata.rdtype == dns.rdatatype.PTR:
                                    hostname = rdata.target.to_text().rstrip('.')
                                    print(f"[+] Found: {ip_str} -> {hostname}")
                                    found_records.append({
                                        "type": "PTR",
                                        "ip": ip_str,
                                        "hostname": hostname
                                    })
                    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                        continue
                    except Exception as e:
                        if verbose:
                            print(f"[!] Error processing {ip_str}: {e}")

        except Exception as e:
            print(f"[!] Error in brute_reverse: {e}")

        print(f"[+] Found {len(found_records)} PTR records")
        return found_records

    def brute_domain(resolver, wordlist_path, domain, 
                    filter_wildcard=True, verbose=False, 
                    ignore_wildcard=False, threads=10):
        """
        Brute-force subdomains for a given domain using a wordlist.
        
        Args:
            resolver: DNS resolver object
            wordlist_path: Path to wordlist file
            domain: Domain to test (e.g., "example.com")
            filter_wildcard: Filter out wildcard records
            verbose: Show verbose output
            ignore_wildcard: Continue even if wildcard is detected
            threads: Number of threads to use (default: 10)
            
        Returns:
            List of found records or None if aborted
        """
        # Check for wildcard resolution
        wildcard_ips = check_wildcard(resolver, domain)
        if wildcard_ips and not ignore_wildcard:
            print("[!] Wildcard DNS detected. These IPs will be filtered:")
            print("\n".join(f"    {ip}" for ip in wildcard_ips))
            print("Continue anyway? [y/N]")
            if input().lower().strip() not in ['y', 'yes']:
                print("[!] Subdomain brute force aborted")
                return None

        if not os.path.isfile(wordlist_path):
            print(f"[!] Wordlist file not found: {wordlist_path}")
            return None

        found_records = []
        
        try:
            with open(wordlist_path) as fd:
                targets = [f"{line.strip()}.{domain.strip()}" for line in fd]
                
            with futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures_map = {executor.submit(resolver.resolve, target, 'A'): ('A', target) for target in targets}
                futures_map.update({executor.submit(resolver.resolve, target, 'AAAA'): ('AAAA', target) for target in targets})
                
                for future in futures.as_completed(futures_map):
                    record_type, target = futures_map[future]
                    try:
                        answer = future.result()
                        for rrset in answer.response.answer:
                            for rdata in rrset:
                                if rdata.rdtype in (dns.rdatatype.A, dns.rdatatype.AAAA, dns.rdatatype.CNAME):
                                    record = {
                                        "type": "A" if rdata.rdtype == dns.rdatatype.A else 
                                            "AAAA" if rdata.rdtype == dns.rdatatype.AAAA else 
                                            "CNAME",
                                        "name": target
                                    }
                                    
                                    if rdata.rdtype in (dns.rdatatype.A, dns.rdatatype.AAAA):
                                        ip = rdata.address
                                        if not filter_wildcard or ip not in wildcard_ips:
                                            record["address"] = ip
                                            print(f"[+] Found: {target} {ip} ({record['type']})")
                                            found_records.append(record)
                                    else:  # CNAME
                                        target_name = rdata.target.to_text().rstrip('.')
                                        record["target"] = target_name
                                        print(f"[+] Found: {target} → {target_name} (CNAME)")
                                        found_records.append(record)
                    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                        continue
                    except Exception as e:
                        if verbose:
                            print(f"[!] Error processing {target}: {e}")

        except Exception as e:
            print(f"[!] Error in brute_domain: {e}")

        print(f"[+] Found {len(found_records)} records")
        return found_records

    def check_dns_cache(resolver, wordlist_path, nameserver, verbose=False):
        """
        Check DNS server cache for records from a wordlist.
        
        Args:
            resolver: DNS resolver object
            wordlist_path: Path to domain wordlist file
            nameserver: Nameserver IP to check
            verbose: Show verbose output
            
        Returns:
            List of cached records found
        """
        if not os.path.isfile(wordlist_path):
            print(f"[!] Wordlist file not found: {wordlist_path}")
            return []

        found_records = []
        
        try:
            # Validate nameserver is an IP address
            if not nameserver.replace('.', '').isdigit():
                print("[!] Nameserver must be an IP address (e.g., 8.8.8.8)")
                return []
                
            resolver.nameservers = [nameserver]
            resolver.timeout = 3
            resolver.lifetime = 3
            
            with open(wordlist_path) as f:
                domains = [line.strip() for line in f if line.strip()]
                
                for domain in domains:
                    try:
                        # Create query with RD (recursion desired) flag disabled
                        query = dns.message.make_query(domain, dns.rdatatype.ANY)
                        query.flags ^= dns.flags.RD  # Disable recursion
                        
                        if verbose:
                            print(f"[*] Checking cache for: {domain}")
                            
                        response = resolver.query(query)
                        
                        for rrset in response.answer:
                            for rdata in rrset:
                                record = {
                                    "domain": domain,
                                    "type": dns.rdatatype.to_text(rdata.rdtype),
                                    "ttl": rrset.ttl
                                }
                                
                                if rdata.rdtype == dns.rdatatype.A:
                                    record["address"] = rdata.address
                                    print(f"[+] Cached A record: {domain} -> {rdata.address} (TTL: {rrset.ttl})")
                                elif rdata.rdtype == dns.rdatatype.CNAME:
                                    record["target"] = rdata.target.to_text().rstrip('.')
                                    print(f"[+] Cached CNAME: {domain} -> {record['target']} (TTL: {rrset.ttl})")
                                elif rdata.rdtype == dns.rdatatype.MX:
                                    record["exchange"] = rdata.exchange.to_text().rstrip('.')
                                    record["preference"] = rdata.preference
                                    print(f"[+] Cached MX: {domain} -> {record['exchange']} (Pref: {rdata.preference}, TTL: {rrset.ttl})")
                                    
                                found_records.append(record)
                                
                    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                        if verbose:
                            print(f"[-] Not in cache: {domain}")
                        continue
                    except dns.exception.DNSException as e:
                        if verbose:
                            print(f"[!] Error checking {domain}: {e}")
                        continue
                        
        except Exception as e:
            print(f"[!] Error in check_dns_cache: {e}")

        print(f"[+] Found {len(found_records)} cached records")
        return found_records


    def process_search_engine_results(resolver, domains, threads=10):
        """
        Process domains from search engine results by resolving them.
        
        Args:
            resolver: DNS resolver object
            domains: List of domains to process
            threads: Number of threads to use (default: 10)
            
        Returns:
            List of resolved records
        """
        if not domains:
            print("[!] No domains provided")
            return []

        resolved_records = []
        
        try:
            with futures.ThreadPoolExecutor(max_workers=threads) as executor:
                futures_map = {}
                
                for domain in domains:
                    domain = domain.strip()
                    if not domain:
                        continue
                        
                    # Query both A and AAAA records
                    futures_map[executor.submit(resolver.resolve, domain, 'A')] = ('A', domain)
                    futures_map[executor.submit(resolver.resolve, domain, 'AAAA')] = ('AAAA', domain)
                    futures_map[executor.submit(resolver.resolve, domain, 'CNAME')] = ('CNAME', domain)

                for future in futures.as_completed(futures_map):
                    record_type, domain = futures_map[future]
                    try:
                        answer = future.result()
                        for rrset in answer.response.answer:
                            for rdata in rrset:
                                record = {
                                    "domain": domain,
                                    "type": record_type,
                                    "ttl": rrset.ttl
                                }
                                
                                if rdata.rdtype == dns.rdatatype.A:
                                    record["address"] = rdata.address
                                    print(f"[+] {domain} A {rdata.address}")
                                    resolved_records.append(record)
                                elif rdata.rdtype == dns.rdatatype.AAAA:
                                    record["address"] = rdata.address
                                    print(f"[+] {domain} AAAA {rdata.address}")
                                    resolved_records.append(record)
                                elif rdata.rdtype == dns.rdatatype.CNAME:
                                    target = rdata.target.to_text().rstrip('.')
                                    record["target"] = target
                                    print(f"[+] {domain} CNAME {target}")
                                    resolved_records.append(record)
                                    
                    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                        print(f"[-] {domain} {record_type} - No record found")
                        continue
                    except Exception as e:
                        print(f"[!] Error processing {domain} {record_type}: {e}")
                        continue
                        
        except Exception as e:
            print(f"[!] Error in process_search_engine_results: {e}")

        print(f"[+] Processed {len(domains)} domains, found {len(resolved_records)} records")
        return resolved_records

    # Helper functions (assuming these are defined elsewhere)
    def generate_testname(num, domain):
        """Generate a test domain name."""
        pass

    def print_debug(msg):
        """Print debug message."""
        pass

    def print_error(msg):
        """Print error message."""
        pass

    def print_status(msg):
        """Print status message."""
        pass

    def print_good(msg):
        """Print success message."""
        pass
    from dns.resolver import Resolver

    def check_wildcard(resolver, domain):
        """Check if wildcard resolution is configured for a domain."""
        # Generate a random subdomain that shouldn't exist
        testname = f"thisshouldnotexist.{domain}"
        
        wildcard_ips = set()
        
        try:
            # Query for A records
            answers = resolver.resolve(testname, 'A')
            print("[!] Wildcard resolution is enabled on this domain")
            
            for rdata in answers:
                ip = rdata.address
                print(f"[!] Resolves to: {ip}")
                wildcard_ips.add(ip)
                
            return wildcard_ips if wildcard_ips else None
            
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            print("[+] No wildcard DNS detected")
            return None
        except dns.exception.DNSException as e:
            print(f"[!] DNS Error: {e}")
            return None
        
    def check_nxdomain_hijack(nameserver):
        """
        Check if a nameserver performs NXDOMAIN hijacking.
        
        Args:
            nameserver: IP address of the nameserver to check (e.g., '8.8.8.8')
        
        Returns:
            bool: True if NXDOMAIN hijacking is detected, False otherwise
        """
        # Generate a test domain that shouldn't exist
        test_domain = "thisshouldnotexist123456.com"
        
        resolver = dns.resolver.Resolver(configure=False)
        
        try:
            # Validate it's an IP address
            if not nameserver.replace('.', '').isdigit():
                print("[!] Error: Nameserver must be an IP address (e.g., 8.8.8.8)")
                return False
                
            resolver.nameservers = [nameserver]
            resolver.timeout = 5
            resolver.lifetime = 5
            
            addresses = []
            
            for record_type in ('A', 'AAAA'):
                try:
                    answers = resolver.resolve(test_domain, record_type)
                    for answer in answers.response.answer:
                        for rdata in answer:
                            if rdata.rdtype == dns.rdatatype.CNAME:
                                target = rdata.target.to_text().rstrip('.')
                                addresses.append(target)
                            elif rdata.rdtype in (dns.rdatatype.A, dns.rdatatype.AAAA):
                                addresses.append(rdata.address)
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                    continue
                except dns.exception.DNSException as e:
                    print(f"[!] DNS Error: {e}")
                    continue
            
            if addresses:
                print(f"[!] NXDOMAIN hijacking detected! Resolves to: {', '.join(addresses)}")
                return True
            else:
                print("[+] No NXDOMAIN hijacking detected")
                return False
                
        except Exception as e:
            print(f"[!] Error checking nameserver: {e}")
            return False
        
    def mainia():
        print("""
        ██████╗ ███╗   ██╗███████╗██████╗ ██████╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
        ██╔══██╗████╗  ██║██╔════╝██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔═══██╗████╗  ██║
        ██║  ██║██╔██╗ ██║███████╗██████╔╝██████╔╝██████╔╝█████╗  ██║   ██║██╔██╗ ██║
        ██║  ██║██║╚██╗██║╚════██║██╔═══╝ ██╔══██╗██╔══██╗██╔══╝  ██║   ██║██║╚██╗██║
        ██████╔╝██║ ╚████║███████║██║     ██║  ██║██║  ██║███████╗╚██████╔╝██║ ╚████║
        ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
        """)
        
        # Initialize DNS resolver
        resolver = configure_resolver()

        
        while True:
            print("\nMain Menu:")
            print("1. Check Wildcard DNS")
            print("2. Check for NXDOMAIN Hijacking")
            print("3. Brute Force TLDs")
            print("4. Brute Force SRV Records")
            print("5. Reverse DNS Lookup")
            print("6. Subdomain Brute Force")
            print("7. DNS Cache Snooping")
            print("8. Process Search Engine Results")
            print("9. Exit")
            
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == "1":
                domain = input("Enter domain to check for wildcard DNS: ").strip()
                wildcard_ips = check_wildcard(resolver, domain)
                if wildcard_ips:
                    print(f"[!] Wildcard DNS enabled. Resolves to: {', '.join(wildcard_ips)}")
                else:
                    print("[+] No wildcard DNS detected")
                    
            elif choice == "2":
                nameserver = input("Enter nameserver IP to check: ").strip()
                if check_nxdomain_hijack(nameserver):
                    print("[!] NXDOMAIN hijacking detected!")
                else:
                    print("[+] No NXDOMAIN hijacking detected")
                    
            elif choice == "3":
                domain = input("Enter base domain (without TLD, e.g., 'example'): ").strip()
                verbose = input("Show verbose output? (y/n): ").lower() == 'y'
                threads = int(input("Number of threads to use (default 10): ") or 10)
                
                print("\n[+] Starting TLD brute force...")
                results = brute_tlds(resolver, domain, verbose=verbose, threads=threads)
                print(f"\n[+] Found {len(results)} records")
                
            elif choice == "4":
                domain = input("Enter domain to check SRV records (e.g., example.com): ").strip()
                if not domain:
                    print("[!] Please enter a valid domain")
                    continue
                    
                verbose = input("Show verbose output? (y/n): ").lower() == 'y'
                threads = int(input("Number of threads to use (default 10): ") or 10)
                
                print("\n[+] Starting SRV brute force...")
                results = brute_srv(resolver, domain, verbose=verbose, threads=threads)
                print(f"\n[+] Found {len(results)} SRV records")
                
            elif choice == "5":
                ip_range = input("Enter IP range (e.g., 104.16.53.0/24 or 104.16.53.1-104.16.53.50): ").strip()
                verbose = input("Show verbose output? (y/n): ").lower() == 'y'
                threads = int(input("Number of threads to use (default 10): ") or 10)
                
                try:
                    if '-' in ip_range:
                        start_ip, end_ip = ip_range.split('-')
                        start = ip_address(start_ip.strip())
                        end = ip_address(end_ip.strip())
                        ip_list = [ip_address(ip) for ip in range(int(start), int(end)+1)]
                    else:
                        ip_list = list(ip_network(ip_range, strict=False).hosts())
                        
                    print("\n[+] Starting reverse DNS lookup...")
                    results = brute_reverse(resolver, ip_list, verbose=verbose, threads=threads)
                    print(f"\n[+] Found {len(results)} PTR records")
                except ValueError as e:
                    print(f"[!] Invalid IP range: {e}")
                    
            elif choice == "6":
                domain = input("Enter domain to brute force (e.g., example.com): ").strip()
                wordlist = input("Enter path to subdomain wordlist: ").strip()
                ignore_wildcard = input("Ignore wildcard warnings? (y/n): ").lower() == 'y'
                verbose = input("Show verbose output? (y/n): ").lower() == 'y'
                threads = int(input("Number of threads to use (default 10): ") or 10)
                
                print("\n[+] Starting subdomain brute force...")
                results = brute_domain(resolver, wordlist, domain, 
                                    verbose=verbose, ignore_wildcard=ignore_wildcard,
                                    threads=threads)
                if results is not None:
                    print(f"\n[+] Found {len(results)} subdomains")
                    
            elif choice == "7":
                nameserver = input("Enter nameserver IP to check (e.g., 8.8.8.8): ").strip()
                if not nameserver.replace('.', '').isdigit():
                    print("[!] Nameserver must be an IP address")
                    continue
                    
                wordlist = input("Enter path to domain wordlist: ").strip()
                verbose = input("Show verbose output? (y/n): ").lower() == 'y'
                
                print("\n[+] Starting DNS cache snooping...")
                results = check_dns_cache(resolver, wordlist, nameserver, verbose=verbose)
                print(f"\n[+] Found {len(results)} cached records")

                
            elif choice == "8":
                print("Enter domains from search engine (one per line, blank line to finish):")
                domains = []
                while True:
                    domain = input("> ").strip()
                    if not domain:
                        break
                    domains.append(domain)
                    
                if not domains:
                    print("[!] No domains entered")
                    continue
                    
                threads = int(input("Number of threads to use (default 10): ") or 10)
                
                print("\n[+] Processing search engine results...")
                results = process_search_engine_results(resolver, domains, threads=threads)
                print(f"\n[+] Found {len(results)} records")
                    
            elif choice == "9":
                print("\n[+] Exiting...")
                break
                
            else:
                print("[!] Invalid choice, please select a valid option.")
                input("Press Enter to continue...")
                try:
                    # You need some code here that might raise KeyboardInterrupt
                    pass  # Placeholder for actual code
                except KeyboardInterrupt:
                    print(f"{Fore.RED} Going Back")

    mainia()

#================ File Processing Menu ============================#
def Processing_menu():
    while True:
        clear_screen()
        banner()
        print(MAGENTA +"==============================="+ ENDC)
        print(MAGENTA +"               Menu            "+ ENDC)    
        print (MAGENTA +"=============================="+ ENDC)
        print("1. File Processing")
        print("2. File Explorer")
        print("Hit enter to return to the main menu",'\n')
        choice = input("Enter your choice: ")
        if choice == '':
            randomshit("Returning to BUGHUNTERS PRO...")
            time.sleep(2)
            return

        elif choice == '1':
            clear_screen()
            file_proccessing() 
        elif choice == '2':
            clear_screen()
            file_explorer()                                                                                        
        else:
            randomshit("Returning to BUGHUNTERS PRO...")
            return
    
def file_proccessing():
    
    generate_ascii_banner("FP", "")

    print("""
        ============================
        File Processing Script   
        ============================
        """)

    def split_input_file(filename, output_base):
        split_files = []  # List to store the names of split files
        with open(filename, 'r') as file:
            lines = file.readlines()
            num_lines = len(lines)
            print(f"The file '{filename}' has {num_lines} lines.")
            
            while True:
                try:
                    parts = int(input("How many parts do you want to split the file into? "))
                    if parts <= 0:
                        raise ValueError("Number of parts must be a positive integer.")
                    break
                except ValueError as e:
                    print("Error:", e)

            lines_per_part = num_lines // parts
            remainder = num_lines % parts

            start = 0
            for i in range(parts):
                end = start + lines_per_part + (1 if i < remainder else 0)
                part_filename = f"{output_base}_part_{i + 1}.txt"
                with open(part_filename, 'w') as out_file:
                    out_file.writelines(lines[start:end])
                split_files.append(part_filename)
                print(f"Wrote {end - start} lines to {part_filename}")
                start = end

        return split_files  # Return the list of split file names

    def calculate_cidr_blocks(ip_ranges):
        ipv4_cidr_blocks = []
        ipv6_cidr_blocks = []
        for start, end in ip_ranges:
            try:
                start_ip = ipaddress.ip_address(start)
                end_ip = ipaddress.ip_address(end)
                cidr = ipaddress.summarize_address_range(start_ip, end_ip)
                for block in cidr:
                    if block.version == 4:
                        ipv4_cidr_blocks.append(str(block))
                    elif block.version == 6:
                        ipv6_cidr_blocks.append(str(block))
            except ValueError:
                continue  # Skip invalid ranges
        return ipv4_cidr_blocks, ipv6_cidr_blocks

    def extract_ip_ranges(lines):
        ip_ranges = []
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                ip_ranges.append((parts[0], parts[1]))
        return ip_ranges

    def save_cidr_blocks(output_file, cidr_blocks):
        with open(output_file, 'w') as file:
            for block in cidr_blocks:
                file.write(block + '\n')

    def remove_duplicates(lines):
        return list(set(lines))  # Remove duplicate lines


    def extract_domains(lines, output_file):
        domains = []
        for line in lines:
            # Extract full domains + paths/queries/fragments (but strip protocols and *. prefixes)
            domain_matches = re.findall(
                r'(?:(?:https?:\/\/)|(?:\*\.))?(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,63}(?:\/[^\s?#]*)?(?:[?#][^\s]*)?)',
                line
            )
            domains.extend(domain_matches)
        
        domains = list(set(domains))  # Remove duplicates

        if domains:
            with open(output_file, 'w') as out_file:
                for domain in domains:
                    out_file.write(f"{domain}\n")
            print(f"Domains saved to {output_file}")
        else:
            print(f"No domains found. Skipping file creation for {output_file}.")


    def extract_ips(lines, output_file):
        ips = []
        for line in lines:
            ip_matches = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
            ips.extend(ip_matches)
        
        ips = list(set(ips))  # Remove duplicate IPs

        if ips:  # Only write if there are IPs to save
            with open(output_file, 'w') as out_file:
                for ip in ips:
                    out_file.write(f"{ip}\n")

            print(f"IPs saved to {output_file}")
        else:
            print(f"No IPs found. Skipping file creation for {output_file}.")


    def process_file(input_filename):
        if not os.path.exists(input_filename):
            print("Error: File does not exist.")
            return

        base_filename, _ = os.path.splitext(input_filename)

        # Step 1: Read and remove duplicates from the entire file before splitting
        with open(input_filename, 'r') as f:
            lines = f.readlines()

        if not lines:  # Check if file is empty
            print("Error: File is empty.")
            return

        unique_lines = remove_duplicates(lines)  # Remove duplicates here

        if not unique_lines:  # If no unique lines remain, stop processing
            print("Error: No unique data found in the file.")
            return

        # Step 2: Write back the unique lines to a temporary file for splitting
        temp_file = f"{base_filename}_unique_temp.txt"
        with open(temp_file, 'w') as f:
            f.writelines(unique_lines)

        split_option = input("Do you want to split the file? (yes/no): ").lower()
        if split_option in ('yes', 'y'):
            split_output_files = split_input_file(temp_file, base_filename)
            print(f"Split output files: {split_output_files}")
        else:
            split_output_files = [temp_file]  # Use the unique temp file if no splitting

        # Process each split file (or the original if not split) as before
        for split_file in split_output_files:
            with open(split_file, 'r') as f:
                lines = f.readlines()

            if not lines:  # Skip empty split files
                continue

            unique_lines = remove_duplicates(lines)

            if not unique_lines:  # If after deduplication nothing remains, skip
                continue

            ip_ranges = extract_ip_ranges(unique_lines)
            ipv4_cidr_blocks, ipv6_cidr_blocks = calculate_cidr_blocks(ip_ranges)

            # Only save files if they have data
            if ipv4_cidr_blocks:
                ipv4_output_file = f"{base_filename}_ipv4_cidr.txt"
                save_cidr_blocks(ipv4_output_file, ipv4_cidr_blocks)

            if ipv6_cidr_blocks:
                ipv6_output_file = f"{base_filename}_ipv6_cidr.txt"
                save_cidr_blocks(ipv6_output_file, ipv6_cidr_blocks)

            if unique_lines:
                domain_output_file = f"{base_filename}_domains.txt"
                extract_domains(unique_lines, domain_output_file)

                ip_output_file = f"{base_filename}_ips.txt"
                extract_ips(unique_lines, ip_output_file)

        time.sleep(2)
        print("All operations completed.")

        # Cleanup: Optionally delete the temporary unique file
        if os.path.exists(temp_file):
            os.remove(temp_file)

    input_filename = input("Enter the name of the file to be processed:(Hit Enter to return) ")
    if not input_filename:
        return 
    process_file(input_filename)

def file_explorer():

    generate_ascii_banner("File Explorer", "")

    import os
    import shutil
    from InquirerPy import prompt
    from InquirerPy.validator import PathValidator


    def list_files(directory="."):
        try:
            return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        except Exception:
            return []


    def list_dirs(directory="."):
        try:
            return [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
        except Exception:
            return []


    def navigate_directories(start_dir="."):
        clear_screen()
        current_dir = os.path.abspath(start_dir)

        while True:
            dirs = list_dirs(current_dir)
            choices = [".. (Go Up)", "✔ Select this directory", "⬅ Back to Main Menu"] + dirs

            answer = prompt([
                {
                    "type": "list",
                    "message": f"Current directory:\n{current_dir}",
                    "choices": choices,
                    "name": "selection",
                    "qmark": "📂"
                }
            ])["selection"]

            if answer == ".. (Go Up)":
                current_dir = os.path.dirname(current_dir)
            elif answer == "✔ Select this directory":
                return current_dir
            elif answer == "⬅ Back to Main Menu":
                return None
            else:
                current_dir = os.path.join(current_dir, answer)


    def select_file(start_dir="."):
        clear_screen()
        current_dir = os.path.abspath(start_dir)

        while True:
            files = list_files(current_dir)
            dirs = list_dirs(current_dir)
            choices = [".. (Go Up)", "⬅ Back to Main Menu"] + dirs + files

            if not choices:
                print("No files or directories found.")
                return None

            answer = prompt([
                {
                    "type": "list",
                    "message": f"Current directory:\n{current_dir}",
                    "choices": choices,
                    "name": "selection",
                    "qmark": "📁",
                    "amark": " ",
                }
            ])["selection"]

            if answer == ".. (Go Up)":
                current_dir = os.path.dirname(current_dir)
            elif answer == "⬅ Back to Main Menu":
                return None
            elif os.path.isdir(os.path.join(current_dir, answer)):
                current_dir = os.path.join(current_dir, answer)
            else:
                return os.path.join(current_dir, answer)


    def open_file():
        clear_screen()
        selected = select_file()
        if not selected or not os.path.isfile(selected):
            return

        try:
            with open(selected, 'r', encoding="utf-8") as file:
                print(f"\n📄 Contents of {selected}:\n")
                print(file.read())
        except Exception as e:
            print(f"❌ Error reading file: {e}")

        input("\nPress Enter to return to menu...")


    def move_file():
        clear_screen()
        src = select_file()
        if not src:
            return

        dst = navigate_directories()
        if not dst:
            return

        try:
            shutil.move(src, dst)
            print(f"✅ Moved '{src}' to '{dst}'")
        except Exception as e:
            print(f"❌ Failed to move file: {e}")
        input("\nPress Enter to return to menu...")


    def rename_file():
        clear_screen()
        file = select_file()
        if not file:
            return

        new_name = prompt([
            {
                "type": "input",
                "message": f"Rename '{os.path.basename(file)}' to:",
                "name": "newname",
                "validate": lambda x: len(x.strip()) > 0
            }
        ])["newname"]

        new_path = os.path.join(os.path.dirname(file), new_name)
        try:
            os.rename(file, new_path)
            print(f"✅ Renamed to {new_path}")
        except Exception as e:
            print(f"❌ Failed to rename: {e}")
        input("\nPress Enter to return to menu...")


    def remove_file():
        clear_screen()
        file = select_file()
        if not file:
            return

        confirm = prompt([
            {
                "type": "confirm",
                "message": f"Are you sure you want to delete:\n{file}?",
                "name": "confirm",
                "default": False
            }
        ])["confirm"]

        if confirm:
            try:
                os.remove(file)
                print(f"✅ Deleted {file}")
            except Exception as e:
                print(f"❌ Error deleting file: {e}")
        input("\nPress Enter to return to menu...")


    def mainman():
        while True:
            clear_screen()
            answer = prompt([
                {
                    "type": "list",
                    "message": "🛠 File Manager - Choose an action:",
                    "choices": ["📂 Move", "🗑 Remove", "✏ Rename", "📖 Open", "❌ Exit"],
                    "name": "action",
                    "qmark": ""
                }
            ])["action"]

            if "Move" in answer:
                move_file()
            elif "Remove" in answer:
                remove_file()
            elif "Rename" in answer:
                rename_file()
            elif "Open" in answer:
                open_file()
            elif "Exit" in answer:
                clear_screen()
                print("👋 Goodbye!")
                break

    mainman()

#================ V2ray configs menu ==============================#
def Configs_V2ray_menu():
    while True:
        clear_screen()
        banner()
        print(MAGENTA +"=================================="+ ENDC)
        print(MAGENTA +"               Menu            "+ ENDC)    
        print (MAGENTA +"=================================="+ ENDC)

        print("1. [new]Vmess/Trojan/Vless       2. [old]Vmess/Trojan/Vless")
        print("Hit enter to return to the main menu",'\n')
        choice = input("Enter your choice: ")
        if choice == '':
            randomshit("Returning to BUGHUNTERS PRO...")
            time.sleep(1)
            clear_screen()
            banner()
            main_menu()
            main()

        elif choice == '1':
            clear_screen()
            teamerror_new() 
        elif choice == 'help' or choice == '?':
            clear_screen()
            print(MAGENTA + "This menu allows you to generate V2Ray configurations." + ENDC)
            print(MAGENTA + "1. [new]Vmess/Trojan/Vless: This option allows you to generate new V2Ray configurations for Vmess, Trojan, and Vless protocols." + ENDC)
            print(MAGENTA + "2. [old]Vmess/Trojan/Vless: This option allows you to generate old V2Ray configurations for Vmess, Trojan, and Vless protocols." + ENDC)
            print(MAGENTA + "You can enter a new host or IP address to update the configurations." + ENDC)
            print(MAGENTA + "You can also choose to fetch configurations from predefined URLs." + ENDC)
            print(MAGENTA + "After generating the configurations, you can save them to files." + ENDC)
            print(MAGENTA + "You can also modify the configurations to replace old server IPs with new ones." + ENDC)
            print(MAGENTA + "Press Enter to return to the menu." + ENDC) 
            time.sleep(10)
        elif choice == '2':
            clear_screen()
            teamerror()                                                                                  
        else:
            randomshit("Returning to BUGHUNTERS PRO...")
            time.sleep(2)
            return  # Return to the main men
    
def teamerror_new():
    
    generate_ascii_banner("404", "ERROR")

    class V2RayConfigUpdater:
        def __init__(self):
            self.cache_timeout = 300
            self.timeout_duration = 10
            self.subscription_urls = {
                "vless": "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/vless.txt",
                "vmess": "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/vmess.txt",
                "trojan": "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/trojan.txt"
            }
            self.new_server_ips = self.prompt_for_ip()
            self.last_fetch_time = 0
            self.cached_configs = None
            self.modified_configs = {'vmess': [], 'vless': [], 'trojan': []}

        def prompt_for_ip(self):
            new_ips = []
            while True:
                ip = input("Enter a new host or IP address (or type 'done' to finish): ").strip()
                if ip.lower() == 'done':
                    break
                elif ip.lower() == 'help' or ip.lower() == '?':
                    print(MAGENTA + "This option allows you to enter a new host or IP address." + ENDC)
                    print(MAGENTA + "You can enter multiple IPs or hosts, and they will be used to update the configurations." + ENDC)
                    print(MAGENTA + "After entering the IPs, you can choose to fetch configurations from predefined URLs." + ENDC)
                    time.sleep(10)
                    clear_screen()
                    continue  # This will make the loop continue and reprompt the user
                new_ips.append(ip)
            return new_ips

        def prompt_for_configuration_choice(self):
            print(MAGENTA + "Available configuration types:" + ENDC)
            for i, key in enumerate(self.subscription_urls.keys(), start=1):
                print(CYAN + f"{i}. {key.upper()}" + ENDC)
            
            while True:
                user_input = input("Enter the number corresponding to the configuration type you want to fetch (or type 'help'/?): ").strip()
                
                # Check for help first, before trying to convert to int
                if user_input.lower() == 'help' or user_input.lower() == '?':
                    print(MAGENTA + "This option allows you to choose a configuration type to fetch." + ENDC)
                    print(MAGENTA + "You can select from Vless, Vmess, or Trojan protocols." + ENDC)
                    print(MAGENTA + "After selecting a configuration type, the script will fetch the configurations from the predefined URLs." + ENDC)
                    print(MAGENTA + "You can then modify the configurations to replace old server IPs with new ones." + ENDC)
                    time.sleep(10)
                    clear_screen()
                    # Reprint the options after help
                    print(MAGENTA + "Available configuration types:" + ENDC)
                    for i, key in enumerate(self.subscription_urls.keys(), start=1):
                        print(CYAN + f"{i}. {key.upper()}" + ENDC)
                    continue
                
                try:
                    choice = int(user_input)
                    if 1 <= choice <= len(self.subscription_urls):
                        selected_key = list(self.subscription_urls.keys())[choice - 1]
                        return selected_key
                    else:
                        print(FAIL + f"Invalid choice. Please enter a number between 1 and {len(self.subscription_urls)}.")
                except ValueError:
                    print(FAIL + "Invalid input. Please enter a valid number or 'help' or '?' for assistance.")

        def extract_vless_server_ip(self, vless_url):
            try:
                at_symbol_index = vless_url.index('vless://') + len('vless://')
                server_ip_start = vless_url.index('@', at_symbol_index) + 1
                server_ip_end = vless_url.index(':', server_ip_start)
                return vless_url[server_ip_start:server_ip_end]
            except (ValueError, IndexError):
                return None

        def remove_duplicates(self, configs):
            return list(set(configs))

        def fetch_configs(self, url, methods=('GET',)):
            current_time = time.time()
            if current_time - self.last_fetch_time < self.cache_timeout and self.cached_configs:
                print(YELLOW + "USING CACHED CONFIGURATIONS." + ENDC)
                return self.cached_configs

            for method in methods:
                print(random.choice([FAIL, LIME, BLUE]) + f"TRYING {method} METHOD..." + ENDC)
                try:
                    response = requests.request(method, url, timeout=self.timeout_duration)
                    response.raise_for_status()
                    content = response.content.strip()
                    decoded_content = None
                    for encoding in ('utf-8', 'ISO-8859-1'):
                        try:
                            decoded_content = content.decode(encoding)
                            break
                        except UnicodeDecodeError:
                            continue
                    if decoded_content:
                        print(LIME+ "SUCCESSFULL" + ENDC)
                        self.cached_configs = decoded_content
                        self.last_fetch_time = current_time
                        return decoded_content
                except requests.RequestException as err:
                    print(FAIL + "ERROR" + ENDC)
                    continue

            print(FAIL + "FAILED." + ENDC)
            return None

        def modify_vless_configurations(self, configs):
            unique_configs = self.remove_duplicates(configs)
            for config in unique_configs:
                if config.startswith('vless://'):
                    old_server_ip = self.extract_vless_server_ip(config)
                    if old_server_ip:
                        if ':8080' not in config:
                            if ':80' in config or ':443' in config:
                                for new_ip in self.new_server_ips:
                                    new_config = config.replace(f'@{old_server_ip}', f'@{new_ip}')
                                    self.modified_configs['vless'].append(new_config)
                            else:
                                print(FAIL + "SKIPPING" + ENDC)
                        else:
                            print(FAIL + "SKIPPING" + ENDC)
                    else:
                        print(FAIL + "SKIPPING" + ENDC)

        def modify_vmess_configurations(self, configs):
            unique_configs = self.remove_duplicates(configs)
            for config in unique_configs:
                if config.startswith('vmess://'):
                    try:
                        base64_content = config.split('://', 1)[1]
                        config_dict = json.loads(base64.b64decode(base64_content).decode('utf-8'))
                        for new_ip in self.new_server_ips:
                            updated_config_dict = config_dict.copy()
                            updated_config_dict['add'] = new_ip
                            new_config = f"vmess://{base64.b64encode(json.dumps(updated_config_dict).encode()).decode('utf-8')}"
                            self.modified_configs['vmess'].append(new_config)
                    except Exception as e:
                        print("Error processing configuration:")
                        print(FAIL + "CONFIGURATION ERROR:" + ENDC)

        def modify_trojan_configurations(self, configs):
            unique_configs = self.remove_duplicates(configs)
            for config in unique_configs:
                if config.startswith('trojan://'):
                    parts = config.split('@')
                    if len(parts) == 2:
                        header = parts[0]
                        address = parts[1].split('/')[0]
                        if ':8080' not in address:
                            if ':80' in address or ':443' in address:
                                for new_ip in self.new_server_ips:
                                    new_config = f"{header}@{new_ip}:{address.split(':')[1]}/"
                                    self.modified_configs['trojan'].append(new_config)
                            else:
                                print(FAIL + "SKIPPING" + ENDC)
                        else:
                            print(FAIL + "SKIPPING" + ENDC)
                    else:
                        print(FAIL + "SKIPPING" + ENDC)

        def save_modified_configs(self):
            for protocol, configs in self.modified_configs.items():
                if configs:
                    file_path = f"{protocol}_configurations.txt"
                    try:
                        all_configs = '\n'.join(configs)
                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(all_configs)
                        print(CYAN + "MODIFIED {protocol.upper()} CONFIGURATIONS HAVE BEEN SAVED IN '{file_path}'." + ENDC)
                    except Exception as e:
                        print(FAIL + "ERROR SAVING MODIFIED" + ENDC)

        def main(self):
            try:
                print(MAGENTA + "CONFIGURATIONS UPDATE..." + ENDC)
                
                # Prompt user to choose configuration type
                config_choice = self.prompt_for_configuration_choice()
                url = self.subscription_urls[config_choice]
                
                print(MAGENTA + "FETCHING CONFIGURATIONS FROM SELECTED URL..." + ENDC)
                initial_configs = self.fetch_configs(url, methods=('GET', 'POST', 'PUT'))
                if initial_configs is None:
                    print(FAIL + "FAILED TO FETCH INITIAL CONFIGURATIONS. EXITING..." + ENDC)
                    return

                try:
                    decoded_content = base64.b64decode(initial_configs).decode('utf-8')
                    print(LIME + "CONTENT IS ENCODED FORMAT." + ENDC)
                except Exception:
                    decoded_content = initial_configs
                    print(LIME + "CONTENT IS IN PLAIN TEXT FORMAT." + ENDC)

                initial_protocols = {'vmess': [], 'vless': [], 'trojan': []}
                for line in decoded_content.splitlines():
                    if line.strip().startswith(('vmess://', 'vless://', 'trojan://')):
                        protocol = line.strip().split('://', 1)[0]
                        initial_protocols[protocol].append(line.strip())

                print(YELLOW + "INITIAL CONFIGURATIONS:" + ENDC)
                for protocol, configs in initial_protocols.items():
                    print(random.choice([FAIL, LIME, BLUE]) + f"{protocol.upper()}  ➤ {len(configs)}" + ENDC)

                print(MAGENTA + "PLEASE WAIT... UPDATING CONFIGURATIONS...." + ENDC)
                time.sleep(3)

                updated_configs = self.fetch_configs(url, methods=('GET', 'POST', 'PUT'))
                if updated_configs is None:
                    print(FAIL + "FAILED TO UPDATE CONFIGURATIONS. EXITING..." + ENDC)
                    return

                try:
                    decoded_content = base64.b64decode(updated_configs).decode('utf-8')
                    print(LIME + "CONTENT IS IN BASE-64 FORMAT." + ENDC)
                except Exception:
                    decoded_content = updated_configs
                    print(LIME + "CONTENT IS IN PLAIN TEXT FORMAT." + ENDC)

                updated_protocols = {'vmess': [], 'vless': [], 'trojan': []}
                for line in decoded_content.splitlines():
                    if line.strip().startswith(('vmess://', 'vless://', 'trojan://')):
                        protocol = line.strip().split('://', 1)[0]
                        updated_protocols[protocol].append(line.strip())

                print(YELLOW + "UPDATED CONFIGURATIONS:" + ENDC)
                for protocol, configs in updated_protocols.items():
                    print(random.choice([FAIL, LIME, BLUE]) + f"{protocol.upper()}  ➤ {len(configs)}" + ENDC)

                self.modify_vless_configurations(updated_protocols['vless'])
                self.modify_vmess_configurations(updated_protocols['vmess'])
                self.modify_trojan_configurations(updated_protocols['trojan'])

                self.save_modified_configs()

            except Exception as e:
                print(FAIL + "ERROR:" + ENDC)

    updater = V2RayConfigUpdater()
    updater.main()

    time.sleep(2)
        
def teamerror():
    import requests
    import time
    import base64
    import os
    from tqdm import tqdm
    import json
    from concurrent.futures import ThreadPoolExecutor
    
    os.system('cls' if os.name == 'nt' else 'clear')
    
    banner = [
        "██╗  ██╗ ██████╗ ██╗  ██╗    ███████╗██████╗ ██████╗  ██████╗ ██████╗ ",
        "██║  ██║██╔═████╗██║  ██║    ██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗",
        "███████║██║██╔██║███████║    █████╗  ██████╔╝██████╔╝██║   ██║██████╔╝",
        "╚════██║████╔╝██║╚════██║    ██╔══╝  ██╔══██╗██╔══██╗██║   ██║██╔══██╗",
        "     ██║╚██████╔╝     ██║    ███████╗██║  ██║██║  ██║╚██████╔╝██║  ██║",
        "     ╚═╝ ╚═════╝      ╚═╝    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝",
    ]

    def print_banner_seamless_horizontal(banner):
        for row in banner:
            for char in row:
                print(char, end='', flush=True)
                time.sleep(0.001)
            print()
            time.sleep(0.05)

    print_banner_seamless_horizontal(banner)


    def script001():

        def fetch_and_save_data(urls, output_filename):
            unique_contents = set()  # Using a set to automatically handle duplicates
            
            for url in urls:
                response = requests.get(url)
                if response.status_code == 200:
                    content = response.text
                    # Split content by lines and add to set to remove duplicates
                    for line in content.splitlines():
                        if line.strip():  # Only add non-empty lines
                            unique_contents.add(line.strip())
                else:
                    print(f"Failed to retrieve content from {url}. Status code: {response.status_code}")

            if unique_contents:
                # First write to a temporary file
                with NamedTemporaryFile(mode='w', delete=False, encoding="utf-8") as temp_file:
                    temp_filename = temp_file.name
                    temp_file.write('\n'.join(unique_contents))
                
                # Then move the temp file to the final destination
                try:
                    if os.path.exists(output_filename):
                        os.remove(output_filename)
                    os.rename(temp_filename, output_filename)
                    print(f"Data saved to {output_filename} (removed duplicates)")
                except Exception as e:
                    print(f"Error while finalizing file: {str(e)}")
                    if os.path.exists(temp_filename):
                        os.remove(temp_filename)
            else:
                print("No data retrieved. Output file not created.")

        def decode_base64_file(input_file):
            try:
                # Read the original content
                with open(input_file, "r", encoding="utf-8") as file:
                    original_data = file.read().splitlines()
                
                # Process each line to decode base64 if needed
                decoded_lines = set()  # Again using a set to avoid duplicates
                for line in original_data:
                    decoded_lines.add(line)  # Add original line
                    try:
                        # Try to decode each line as base64
                        decoded_data = base64.urlsafe_b64decode(line).decode('utf-8')
                        # Add decoded lines if they're different
                        for decoded_line in decoded_data.splitlines():
                            if decoded_line.strip():
                                decoded_lines.add(decoded_line.strip())
                    except:
                        # If it's not base64, just continue
                        continue
                
                # Write to a temporary file first
                with NamedTemporaryFile(mode='w', delete=False, encoding="utf-8") as temp_file:
                    temp_filename = temp_file.name
                    temp_file.write('\n'.join(decoded_lines))
                
                # Replace the original file with the temp file
                os.replace(temp_filename, input_file)
                print(f"Decoded data saved to {input_file} (removed duplicates)")

            except FileNotFoundError:
                print("Input file not found.")
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                if 'temp_filename' in locals() and os.path.exists(temp_filename):
                    os.remove(temp_filename)
            except KeyboardInterrupt:
                print(f"{Fore.RED} Going Back")

        def a1():
            link_groups = {
                "Vless Configurations": [
                    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/vless.txt",
                ],
                "Vmess Configurations": [
                    "https://github.com/Epodonios/v2ray-configs/raw/main/Splitted-By-Protocol/vmess.txt",
                ],
                "Trojan Configurations": [
                    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/trojan.txt",

                ],
                "Shadowsocks Configurations": [
                    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/Splitted-By-Protocol/ss.txt"
                ],
                "Hysteria Configurations": [
                    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/subscribe/protocols/hysteria",
                    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/channels/protocols/hysteria",
                    "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/hysteria",
                ],
            }

            while True:
                print("Choose a group of links:")
                for i, group_name in enumerate(link_groups.keys(), start=1):
                    print(f"{i}: {group_name}")

                user_input = input("Enter the number of the group you want to select (or type 'help'/?): ").strip()

                # Check for help first
                if user_input.lower() in ('help', '?'):
                    print("This script allows you to fetch and decode V2Ray configurations from predefined URLs.")
                    print("1. First select a group of links from the available options")
                    print("2. Then provide an output filename (e.g., output.txt)")
                    print("3. The script will fetch the configurations and decode them")
                    time.sleep(5)
                    clear_screen()
                    continue  # Show the menu again after help

                try:
                    group_choice = int(user_input)
                    if 1 <= group_choice <= len(link_groups):
                        selected_group = list(link_groups.keys())[group_choice - 1]
                        output_filename = input("Enter the name of the output file (e.g., output.txt): ").strip()
                        if not output_filename:
                            print("Filename cannot be empty. Please try again.")
                            continue
                        
                        fetch_and_save_data(link_groups[selected_group], output_filename)
                        decode_base64_file(output_filename)
                        break  # Exit after successful operation
                    else:
                        print(f"Invalid choice. Please enter a number between 1 and {len(link_groups)}.")
                        time.sleep(0.5)
                except ValueError:
                    print("Invalid input. Please enter a valid number or 'help'/? for assistance.")
                    time.sleep(0.5)

        try:
            a1()
        except KeyboardInterrupt as e:
            print(f"returning to main menu")
        finally:
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
            teamerror()
                    
    def script002():

                    
        def decode_v2ray(vmess_url):
            if not vmess_url.startswith("vmess://"):
                return None
            try:
                base64_data = vmess_url.replace("vmess://", "").strip()
                padded_data = base64_data + '=' * (-len(base64_data) % 4)  # Add padding if needed
                decoded_bytes = base64.urlsafe_b64decode(padded_data)
                decoded_str = decoded_bytes.decode('utf-8', errors='ignore')  # ignore decode errors
                return json.loads(decoded_str)
            except Exception as e:
                print(f"Failed to decode a vmess line:")
                return None

        def decode_vmess_file(input_file, output_file):
            try:
                with open(input_file, 'r', encoding='utf-8', errors='ignore') as file:
                    lines = file.readlines()

                decoded_v2ray_data_list = []

                for line in lines:
                    decoded_data = decode_v2ray(line.strip())
                    if decoded_data:
                        decoded_v2ray_data_list.append(decoded_data)

                if decoded_v2ray_data_list:
                    with open(output_file, 'w', encoding='utf-8') as out:
                        json.dump(decoded_v2ray_data_list, out, indent=2)
                    print(f"Decoded data saved to '{output_file}'")
                else:
                    print(f"No valid V2Ray data found in '{input_file}'.")

            except FileNotFoundError:
                print(f"File '{input_file}' not found. Please provide a valid input file name.")
            except Exception as e:
                print(f"An error occurred:")

        def a2():
            clear_screen()
            generate_ascii_banner("Vmess Decoder", "Tool")
            input_file = input("Enter the name of the input text file containing Vmess data (e.g., input.txt): ")
            if input_file == 'help' or input_file == '?':
                print("This script allows you to decode Vmess configurations from a text file.")
                print("You need to provide the name of the input text file containing Vmess data.")
            if not input_file:
                print("No input file provided. Returning to main menu.")
                time.sleep(0.5)
                a2()
            output_file = input("Enter the name of the output text file (e.g., decoded_output.txt): ")
            if not output_file:
                print("No output file provided.")
                time.sleep(0.5)
                a2()

            decode_vmess_file(input_file, output_file)


        try:
            a2()
        except Exception as e:
            print(f"Vmess ONLY!!! Done!!")
        except KeyboardInterrupt:
            print(f"{Fore.RED} Going Back")
        finally:
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
            teamerror()
        
    def script003():
        
        def z1():
            print("Select an operation:")
            print("1. Replace host, sni or addr in vmess file")
            print("2. Update IP addresses in ss/vless/hyst file")
            print("3. SNI/Host Replacement for Vless/ Trojan etc...")
            print("4. Decode Vless configs")
            print("5. Go back to teamerror")

        
        def replace_fields_in_json(input_file, output_file, replace_host, replace_sni, replace_host_in_json):
            try:
                with open(input_file, 'r') as f:
                    data = json.load(f)

                print("Original data:", data)  # Debugging output

                for entry in data:
                    # Update the 'add' field if present and user provided a value
                    if 'add' in entry and replace_host:
                        print(f"Updating address from {entry['add']} to {replace_host}")  # Debugging output
                        entry['add'] = replace_host
                    
                    # Update the 'sni' field if present and user provided a value
                    if 'sni' in entry and replace_sni:
                        print(f"Updating SNI from {entry['sni']} to {replace_sni}")  # Debugging output
                        entry['sni'] = replace_sni
                    
                    # Update the 'host' field if present and user provided a value
                    if 'host' in entry and replace_host_in_json:
                        print(f"Updating host from {entry['host']} to {replace_host_in_json}")  # Debugging output
                        entry['host'] = replace_host_in_json

                with open(output_file, 'w') as f:
                    json.dump(data, f, indent=4)

                print("Update complete.")  # Debugging output
            except Exception as e:
                print(f"An error occurred: {e}")
                        
        def update_ip_addresses_in_file(file_name, new_ip):
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                modified_lines = []
                with tqdm(total=len(lines), position=0, leave=True) as pbar:
                    for line in lines:
                        ip_match = re.search(r'@(\d+\.\d+\.\d+\.\d+)', line)
                        if ip_match:
                            current_ip = ip_match.group(1)
                            modified_line = line.replace(f'@{current_ip}', f'@{new_ip}')
                            modified_lines.append(modified_line)
                        else:
                            modified_lines.append(line)
                        pbar.update(1)
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.writelines(modified_lines)
                print("IP addresses updated successfully in", file_name)

            except FileNotFoundError:
                print(f"File '{file_name}' not found in the current directory. Please provide a valid file name.")
            except Exception as e:
                print(f"An error occurred:")
                return None
        

        def split_and_decode_vless(file_name):
            output_decoded = f"{file_name}_decoded.txt"

            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

                decoded_vless_lines = []

                # Silent mode - only show the progress bar
                for line in tqdm(lines, desc="Decoding", unit="line"):
                    encoded_match = re.search(r'([A-Za-z0-9+/=]+)', line)
                    if encoded_match:
                        encoded_str = encoded_match.group(0)
                        
                        try:
                            decoded_bytes = base64.b64decode(encoded_str)
                            decoded_str = decoded_bytes.decode('utf-8')
                            decoded_vless_lines.append(decoded_str.strip())
                        except Exception:
                            continue  # Silently skip errors

                with open(output_decoded, 'w', encoding='utf-8') as decoded_file:
                    decoded_file.write('\n'.join(decoded_vless_lines))

            except Exception:
                pass  # Silently handle all errors
             
        def update_addresses_in_file(file_name, new_sni=None, new_host=None):
            """
            Updates SNI and/or host addresses in the file based on the specified new values.

            Parameters:
            - file_name (str): The path to the file to update.
            - new_sni (str or None): The new SNI address, if replacing SNI.
            - new_host (str or None): The new host address, if replacing host.
            """
            try:
                with open(file_name, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                
                modified_lines = []
                with tqdm(total=len(lines), position=0, leave=True, desc="Updating addresses") as pbar:
                    for line in lines:
                        # Replace SNI if new_sni is provided
                        if new_sni:
                            sni_match = re.search(r'sni=([\w\.-]+)', line)
                            if sni_match:
                                current_sni = sni_match.group(1)
                                line = line.replace(f'sni={current_sni}', f'sni={new_sni}')
                        
                        # Replace host if new_host is provided
                        if new_host:
                            host_match = re.search(r'ws&host=([\w\.-]+)', line)
                            if host_match:
                                current_host = host_match.group(1)
                                line = line.replace(f'ws&host={current_host}', f'ws&host={new_host}')
                        
                        modified_lines.append(line)
                        pbar.update(1)

                # Write modified lines back to the file
                with open(file_name, 'w', encoding='utf-8') as file:
                    file.writelines(modified_lines)
                
                print("SNI and host addresses updated successfully in", file_name)

            except FileNotFoundError:
                print(f"File '{file_name}' not found in the current directory. Please provide a valid file name.")
            except Exception as e:
                print(f"An error occurred: {e}")

        try:
            while True:
                z1()
                operation = input("Enter your choice: ")

                if operation == '1':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    input_file = input("Enter the name of the input text file: ")
                    output_file = input("Enter the name of the output text file: ")
                    replace_host = input("Enter the Addr to replace with: ")
                    replace_sni = input("Enter the new SNI to replace with: ")
                    replace_host_in_json = input("Enter the new host value to replace with: ")
                    
                    replace_fields_in_json(input_file, output_file, replace_host, replace_sni, replace_host_in_json)
                    print("Job done!")
                    time.sleep(2)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    script003()  # Call the function again to continue the loop
                        
                elif operation == '2':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    file_name = input("Enter the name of the text file in the current directory: ")
                    new_ip = input("Enter the new IP address: ")
                    update_ip_addresses_in_file(file_name, new_ip)
                    print("Job done!")
                    time.sleep(2)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    script003()

                elif operation == '3':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    
                    # Prompt for the file and new SNI
                    file_name = input("Enter the vless/trojan file for update: ")
                    new_sni = input("New SNI Name (leave blank if no change): ")
                    new_host = input("New Host Name (leave blank if no change): ")
                    
                    # Call the combined function, only updating provided fields
                    update_addresses_in_file(file_name, new_sni=new_sni if new_sni else None, new_host=new_host if new_host else None)
                    
                    print("Job done!")
                    time.sleep(2)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    script003()

                elif operation == '4':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    input_file = input("Enter the name of the input text file: ")
                    
                    split_and_decode_vless(input_file)
                    print("Decoded Vless configurations saved to:", input_file + "_decoded.txt")
                    time.sleep(2)
                    os.system('cls' if os.name == 'nt' else 'clear')
                    script003()  # Call the function again to continue the loop
                    
                elif operation == '5':
                    os.system('cls' if os.name == 'nt' else 'clear')
                    teamerror()
                    # Exit the loop to return to teamerror()
                    break

        except Exception as e:
            print(f"An error occurred: {e}")
        except KeyboardInterrupt:
            print(f"{Fore.RED} Going Back")

        finally:
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
            return
                     # Assuming you want to call teamerror() after the loop exits
            
    def script004():
        import base64
        import json

        def reencode_v2ray_data():
            input_file_name = input("Enter the name of the input file (e.g., v2ray_data.txt): ")
            protocol_prefix = "vmess://"

            try:
                with open(input_file_name, 'r') as file:
                    data = json.load(file)
            except FileNotFoundError:
                print(f"File '{input_file_name}' not found.")
                return

            output_file_name = input("Enter the name of the output file (e.g., reencoded_v2ray_data.txt): ")

            reencoded_data_list = []
            for v2ray_data in data:
                reencoded_data = encode_v2ray(v2ray_data, protocol_prefix)
                if reencoded_data:
                    reencoded_data_list.append(reencoded_data)

            with open(output_file_name, 'w') as output_file:
                for reencoded_data in reencoded_data_list:
                    output_file.write(reencoded_data + '\n')
            print(f"Re-encoded data saved to '{output_file_name}'")

        def encode_v2ray(v2ray_data, protocol_prefix):
            try:
                json_str = json.dumps(v2ray_data, ensure_ascii=False)
                encoded_data = base64.urlsafe_b64encode(json_str.encode('utf-8')).decode('utf-8')
                return protocol_prefix + encoded_data
            except Exception as e:
                return None

        def a3():
            reencode_v2ray_data()
        try:
            a3()
        except Exception as e:
            print(f"An error occurred: {e}")
        except KeyboardInterrupt:
            print(f"{Fore.RED} Going Back")
        finally:
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
            teamerror()
                    
    def script005():

        from bs4 import BeautifulSoup
     
        def decode_vmess(vmess_url):
            try:
                # Extract base64 part
                base64_str = vmess_url.split("://")[1]
                # Add padding if needed
                padding = len(base64_str) % 4
                if padding:
                    base64_str += "=" * (4 - padding)
                decoded_bytes = base64.urlsafe_b64decode(base64_str)
                return decoded_bytes.decode('utf-8')
            except Exception as e:
                print(FAIL + f"Error decoding VMess URL {vmess_url[:50]}...: {e}" + ENDC)
                return None

        def test_vmess_url(vmess_url):
            try:
                decoded_str = decode_vmess(vmess_url)
                if not decoded_str:
                    return vmess_url, 0
                    
                vmess_data = json.loads(decoded_str)
                server_address = vmess_data.get("add", "")
                server_port = vmess_data.get("port", "")
                
                if not server_address or not server_port:
                    return vmess_url, 0
                    
                # Test connection
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((server_address, int(server_port)))
                    s.sendall(b"GET / HTTP/1.1\r\nHost: cp.cloudflare.com\r\n\r\n")
                    response = s.recv(1024)
                    
                if b"HTTP/1.1" in response or b"cloudflare" in response.lower():
                    return vmess_url, 1
                return vmess_url, 0
            
            except Exception as e:
                return vmess_url, 0

        def test_vless_url(vless_url):
            try:
                # Improved regex to handle various VLESS URL formats
                match = re.match(r'vless://([^@]+)@([^:]+):(\d+)(?:/\?.*)?', vless_url)
                if not match:
                    return vless_url, 0
                    
                uuid, server_address, server_port = match.groups()
                
                # Test connection
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(5)
                    s.connect((server_address, int(server_port)))
                    s.sendall(b"GET / HTTP/1.1\r\nHost: cp.cloudflare.com\r\n\r\n")
                    response = s.recv(1024)
                    
                if b"HTTP/1.1" in response or b"cloudflare" in response.lower():
                    return vless_url, 1
                return vless_url, 0
            
            except Exception as e:
                return vless_url, 0

        def a4():

            file_path = input("Enter the name of the text file containing proxy URLs: ")

            try:
                # Open with UTF-8 encoding and error handling
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    urls = [line.strip() for line in file if line.strip()]

                vmess_urls = [url for url in urls if url.startswith("vmess://")]
                vless_urls = [url for url in urls if url.startswith("vless://")]
                
                print(f"Found {len(vmess_urls)} VMess URLs and {len(vless_urls)} VLESS URLs")

                connected_urls = []

                # Test VMess URLs
                if vmess_urls:
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        results = list(tqdm(executor.map(test_vmess_url, vmess_urls), 
                                    total=len(vmess_urls), 
                                    desc="Testing VMess URLs"))
                        connected_urls.extend(url for url, status in results if status == 1)

                # Test VLESS URLs
                if vless_urls:
                    with ThreadPoolExecutor(max_workers=10) as executor:
                        results = list(tqdm(executor.map(test_vless_url, vless_urls), 
                                    total=len(vless_urls), 
                                    desc="Testing VLESS URLs"))
                        connected_urls.extend(url for url, status in results if status == 1)

                print(CYAN + f"\nTotal working proxy URLs: {len(connected_urls)}" + ENDC)
                
                if connected_urls:
                    save_file = input("Do you want to save working URLs to a file? (yes/no): ").lower()
                    if save_file == 'yes':
                        output_file_path = input("Enter the name of the output text file: ")
                        # Use UTF-8 encoding for output file as well
                        with open(output_file_path, 'w', encoding='utf-8') as output_file:
                            output_file.write("\n".join(connected_urls))
                        print(CYAN + f"Working URLs saved to '{output_file_path}'." + ENDC)

            except FileNotFoundError:
                print(FAIL + f"File '{file_path}' not found. Please provide a valid file name." + ENDC)
            except Exception as e:
                print(FAIL + f"An unexpected error occurred: {e}" + ENDC)
                
        try:
            a4()
        except Exception as e:
            print(FAIL + f"An error occurred: {e} " + ENDC)
        except KeyboardInterrupt:
            print(f"{Fore.RED} Going Back")
        finally:
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
            teamerror()
              
    def script006():
        import re
        import os
        import base64
        import json
        import urllib.parse
        from urllib.parse import parse_qs, unquote
        import yaml
        from tqdm import tqdm
        import time

        FAIL = '\033[91m'
        ENDC = '\033[0m'

        def clean_remark(remark):
            """Clean and decode the remark portion of the link"""
            if not remark:
                return ""
            try:
                decoded = unquote(remark)
                if '\\u' in decoded or '\\U' in decoded:
                    decoded = decoded.encode('utf-8').decode('unicode-escape')
                return decoded.strip()
            except:
                return remark.strip()

        def parse_vless(link):
            """Parse VLESS link into Clash Meta config"""
            try:
                decoded_link = unquote(link)
                pattern = r'vless://([^@]+)@([^:]+):(\d+)(?:/\?|\?)([^#]+)#?(.*)'
                match = re.match(pattern, decoded_link)
                if not match:
                    return None
                    
                uuid, server, port, params, remark = match.groups()
                remark = clean_remark(remark)
                
                query = parse_qs(params)
                
                config = {
                    "name": f"VLESS-{remark if remark else f'{server}:{port}'}",
                    "type": "vless",
                    "server": server,
                    "port": int(port),
                    "uuid": uuid,
                    "udp": True,
                    "tls": False,
                    "network": "tcp"
                }
                
                if 'security' in query:
                    config['tls'] = query['security'][0] in ['tls', 'reality']
                elif 'encryption' in query:
                    config['tls'] = query['encryption'][0] in ['tls', 'reality']
                
                if 'type' in query:
                    config['network'] = query['type'][0]
                
                host = query.get('host', [None])[0] or query.get('sni', [None])[0]
                if host:
                    if config['network'] == 'ws':
                        config['ws-opts'] = {"headers": {"Host": host}}
                    else:
                        config['servername'] = host
                
                if 'path' in query:
                    path = unquote(query['path'][0])
                    if config['network'] == 'ws':
                        if 'ws-opts' not in config:
                            config['ws-opts'] = {}
                        config['ws-opts']['path'] = path
                
                if 'flow' in query:
                    config['flow'] = query['flow'][0]
                
                if 'pbk' in query:
                    config['reality-opts'] = {
                        "public-key": query['pbk'][0],
                        "short-id": query.get('sid', [''])[0]
                    }
                
                return config
                
            except Exception as e:
                print(f"\n⚠️ Error parsing VLESS: {str(e)}")
                print(f"Problematic link: {link[:100]}...")
                return None

        def parse_vmess(link):
            """Parse VMess link into Clash Meta config"""
            try:
                decoded = base64.b64decode(link[8:]).decode('utf-8')
                config = json.loads(decoded)
                
                return {
                    "name": f"VMess-{config.get('ps', '').strip() or f'{config['add']}:{config['port']}'}",
                    "type": "vmess",
                    "server": config['add'],
                    "port": int(config['port']),
                    "uuid": config['id'],
                    "alterId": int(config.get('aid', 0)),
                    "cipher": config.get('scy', 'auto'),
                    "udp": True,
                    "tls": config.get('tls') == 'tls',
                    "network": config.get('net', 'tcp'),
                    "ws-opts": {
                        "path": config.get('path', ''),
                        "headers": {"Host": config.get('host', '')}
                    } if config.get('net') == 'ws' else None,
                    "servername": config.get('sni')
                }
            except KeyboardInterrupt:
                print(f"{Fore.RED} Going Back")
            except Exception as e:
                print(f"\n⚠️ Error parsing VMess: {str(e)}")
                return None

        def sanitize_filename(filename):
            """Make sure filename is safe and consistent"""
            # Remove special characters except basic ones
            filename = re.sub(r'[^\w\-_ .]', '', filename)
            # Replace spaces with underscores
            filename = filename.replace(' ', '_')
            # Ensure it doesn't start/end with dots or spaces
            filename = filename.strip(' .')
            # Make sure extension is lowercase
            if '.' in filename:
                name, ext = filename.rsplit('.', 1)
                filename = f"{name}.{ext.lower()}"
            return filename

        def save_individual_config(proxy, output_dir, index):
            """Save config with touch-based workaround"""
            try:
                os.makedirs(output_dir, exist_ok=True)
                
                config = {
                    "proxies": [proxy],
                    "proxy-groups": [{
                        "name": "PROXY",
                        "type": "select",
                        "proxies": [proxy["name"]]
                    }],
                    "rules": [
                        "GEOIP,CN,DIRECT",
                        "MATCH,PROXY"
                    ]
                }
                
                # Generate filename (with sanitization)
                filename = f"{index}_{proxy['type']}.yaml"
                filename = sanitize_filename(filename)  # Use your existing function
                output_path = os.path.join(output_dir, filename)
                
                # ANDROID FIX: Create empty file first with touch
                os.system(f'touch "{output_path}"')
                
                # Write content normally
                with open(output_path, 'w', encoding='utf-8') as f:
                    yaml.dump(config, f, sort_keys=False, allow_unicode=True)
                
                return output_path
            except Exception as e:
                print(f"⚠️ Touch workaround failed: {str(e)}")
                return None
            
        def bs4():
            print("🔧 Individual Proxy Config Generator")
            print("----------------------------------")
            print("Creates numbered Clash config files (001_vless.yaml, 002_vmess.yaml, etc.)")
            print("----------------------------------")
            
            input_file = input("Enter file name or path: ").strip()
            if not os.path.exists(input_file):
                print(f"❌ File not found: {input_file}")
                return
            
            output_dir = os.path.join(os.path.dirname(input_file), "configs")
            os.makedirs(output_dir, exist_ok=True)
            
            with open(input_file, 'r', encoding='utf-8') as f:
                links = [line.strip() for line in f if line.strip()]
            
            if not links:
                print("❌ No valid links found")
                return
            
            successful = 0
            print("\n🔄 Processing links...")
            for i, link in enumerate(tqdm(links, desc="Converting", unit="link"), start=1):
                try:
                    if link.startswith('vless://'):
                        config = parse_vless(link)
                    elif link.startswith('vmess://'):
                        config = parse_vmess(link)
                    else:
                        continue
                    
                    if config:
                        saved_path = save_individual_config(config, output_dir, i)
                        if saved_path:
                            successful += 1
                    else:
                        print(f"\n⚠️ Failed to parse link: {link[:100]}...")
                except Exception as e:
                    print(f"\n⚠️ Failed to process link: {str(e)}")
                    print(f"Problematic link: {link[:100]}...")
            
            print(f"\n✅ Successfully created {successful} individual configs")
            print(f"📁 Output directory: {os.path.abspath(output_dir)}")

        try:
            bs4()
        except KeyboardInterrupt:
            print(f"{Fore.RED} Going Back")
        except Exception as e:
            print(FAIL + f"An error occurred: {e} " + ENDC)
        finally:
            time.sleep(2)
            os.system('cls' if os.name == 'nt' else 'clear')
            teamerror()

    def Configs_V2ray_menu():

        print("1.""\033[32mGRAB CONFIGS\033[0m""                       2.)""\033[32mDECODE VMESS!! \033[0m")                       
        print("3.""\033[95mDecode VLESS/ Replace all host/ip\033[0m""  4.)""\033[33mRe-encode VMESS !!\033[0m")
        print("5.""\033[32mTEST Configs \033[0m""                       6.)""\033[32m Convert vmess/vless to clash configs\033[0m")
        print("0.""\033[34mPrevious Menu\033[0m")

        choice = input("Hit Enter To Return BUGHUNTERS PRO or 0 for v2ray Menu: ")
        if choice == '0':
            time.sleep(1)
            os.system('cls' if os.name == 'nt' else 'clear')
            return  # Return to the main menu
        elif choice == '':
            clear_screen()
            main_menu()
            main()

        elif choice == '1':
            os.system('cls' if os.name == 'nt' else 'clear')
            script001() 
        elif choice == '2':
            os.system('cls' if os.name == 'nt' else 'clear')
            script002() 
        elif choice == '3':
            os.system('cls' if os.name == 'nt' else 'clear')
            script003() 
        elif choice == '4':
            os.system('cls' if os.name == 'nt' else 'clear')
            script004()
        elif choice == '5':
            os.system('cls' if os.name == 'nt' else 'clear')
            script005() 
        elif choice == '6':
            os.system('cls' if os.name == 'nt' else 'clear')
            print(GREEN + "Please test your configs before using this option..." + ENDC)
            time.sleep(0.5)
            print(YELLOW + "Please test your configs before using this option..." + ENDC)
            time.sleep(0.5)
            print(RED + "Please test your configs before using this option..." + ENDC)
            time.sleep(0.5)
            clear_screen()
            script006() 
        else:
            os.system('cls' if os.name == 'nt' else 'clear')
            try:
                # You need some code here that might raise KeyboardInterrupt
                pass  # Placeholder for actual code
            except KeyboardInterrupt:
                print(f"{Fore.RED} Going Back")

    Configs_V2ray_menu()

#============= Help Menu =================#
def help_menu():

    def sub_domain_finder():
        subdomainfinder1 = GREEN + """
        SUBDOmain FINDER
        
        This is a web scraping tool that scans a 
        specific domain for subdomains and IPS
        The user is prompted to enter a domain 
        name for which they want to find subdomains or IPs
        e.g google.com, the script will then prompt 
        the user to save the results (y/n). 
        Then it will ask the user to input the name 
        of txt file they want to save their results as...
        The script will then ask the user if they 
        want to save the ips only to a txt file (y/n)
        it will then scan for subdomains and 
        save the found results to your txt files
        scan time 1hr - 5 mins
        """ + ENDC + ("\n")
        print(subdomainfinder1)
        

    def urlscan_io():
        urlscan_text = GREEN + """
        URLSCAN.IO
        
        This script takes a URL as input and sends a GET request to the
        URLScan.io API to retrieve information about the URL.
        It then parses the JSON response to extract various details such as
        the domain, subdomains, IP addresses, and more.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(urlscan_text)
        

    def dr_access():
        dr_access_text = GREEN + """
        DR ACCESS
        
        This script takes a URL as input and sends a GET request to the
        Domain Reputation API to retrieve information about the URL.
        It then parses the JSON response to extract various details such as
        the domain, subdomains, IP addresses, and more.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(dr_access_text)
        

    def host_checker():
        host_checker_text = GREEN + """
        HOST CHECKER
        
        This script scans all the domains and
        subdomains in a given list and
        writes them to a specified output file.
        It checks the status of each domain and subdomain
        and reports whether they are reachable or not.
        
        """ + ENDC + ("\n")
        print(host_checker_text)
        

    def free_proxies():
        free_proxies_text = GREEN + """
        FREE PROXIES
        
        This script fetches a list of free proxies from a specified URL.
        It then filters the proxies based on their type (HTTP, HTTPS, SOCKS4, SOCKS5)
        and saves them to separate text files.
        The user can choose which types of proxies to save.
        
        """ + ENDC + ("\n")
        print(free_proxies_text)
        

    def stat():
        stat_text = GREEN + """
        STAT
        
        This script takes a URL as input and sends a GET request to the
        URLScan.io API to retrieve information about the URL.
        It then parses the JSON response to extract various details such as
        the domain, subdomains, IP addresses, and more.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(stat_text)
             

    def tls_checker():
        tls_checker_text = GREEN + """
        TLS CHECKER

        This script checks the TLS/SSL configuration of a given domain.
        It verifies the certificate validity, supported protocols, and ciphers.
        The results are printed to the console.
        """ + ENDC + ("\n")
        print(tls_checker_text)
       

    def web_crawler():
        web_crawler_text = GREEN + """
        WEB CRAWLER
        
        This script crawls a given website and extracts links from it.
        It can follow links to a specified depth and save the results to a file.
        The user can specify the starting URL and the depth of crawling.
        """ + ENDC + ("\n")
        print(web_crawler_text)
        

    def hacker_target():
        hacker_target_text = GREEN + """
        HACKER TARGET
        
        This script takes a domain as input and retrieves information about it
        from the HackerTarget API. It provides details such as subdomains,
        IP addresses, and other relevant data.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(hacker_target_text)
        

    def url_redirect():
        usr_redirect_text = GREEN + """
        USER REDIRECT
        
        This script takes a URL as input and redirects the user to that URL.
        It can be used to test URL redirection or to access specific web pages.
        The user is prompted to enter the URL they want to redirect to.
        
        """ + ENDC + ("\n")
        print(usr_redirect_text)
        

    def dossier():
        dossier_text = GREEN + """
        DOSSIER
        
        This script takes a domain as input and retrieves information about it
        from the Dossier API. It provides details such as subdomains,
        IP addresses, and other relevant data.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(dossier_text)
        

    def asn2():
        asn2_text = GREEN + """
        ASN2
        
        This script takes an ASN (Autonomous System Number)  or Company name as input
        and retrieves information about it from the ASN2 API.
        It provides details such as associated IP ranges, organizations,
        and other relevant data.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(asn2_text)
       

    def websocket_scanner():
        websocket_scanner_text = GREEN + """
        WEBSOCKET SCANNER
        
        This script scans a given website for WebSocket endpoints.
        It retrieves the WebSocket URLs and checks their status.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(websocket_scanner_text)
        

    def nslookup():
        nslookup_text = GREEN + """
        NSLOOKUP
        
        This script performs a lookup for a given Net Server.
        It retrieves various records such as A, AAAA, MX, TXT, and more.
        
        """ + ENDC + ("\n")
        print(nslookup_text)
        

    def dork_scanner():
        dork_scanner_text = GREEN + """
        DORK SCANNER
        
        This script takes a search query (dork) as input and performs a Google search
        to find relevant results. It retrieves the URLs of the search results and
        saves them to a file.
        
        """ + ENDC + ("\n")
        print(dork_scanner_text)
        

    def tcp_udp_scan():
        tcp_udp_scan_text = GREEN + """
        TCP/UDP SCAN
        
        This script performs a TCP and UDP port scan on a given IP address or domain.
        It checks for open ports and services running on those ports.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(tcp_udp_scan_text)
        

    def dns_key():
        dns_key_text = GREEN + """
        DNS KEY
        
        This script retrieves DNSKEY records for a given domain.
        It checks the DNSSEC configuration and prints the results to the console.
        
        """ + ENDC + ("\n")
        print(dns_key_text)
       

    def tcp_ssl():
        tcp_ssl_text = GREEN + """
        TCP SSL
        
        This script performs a TCP SSL scan on a given IP address or domain.
        It checks for open SSL ports and retrieves SSL certificate information.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(tcp_ssl_text)
        

    def open_port_checker():
        open_port_checker_text = GREEN + """
        OPEN PORT CHECKER
        
        This script checks for open ports on a given IP address or domain.
        It scans a range of ports and reports which ones are open.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(open_port_checker_text)
        

    def access_control():
        access_control_text = GREEN + """
        ACCESS CONTROL
        
        This script checks the access control settings of a given URL.
        It verifies if the URL is accessible and retrieves relevant information.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(access_control_text)
         

    def casper():
        casper_text = GREEN + """
        CASPER
        
        This script takes a URL as input and sends a GET request to the
        Casper API to retrieve information about the URL.
        It then parses the JSON response to extract various details such as
        the domain, subdomains, IP addresses, and more.
        The results are printed to the console.
        
        """ + ENDC + ("\n")
        print(casper_text)
        

    def subdomain_enum():
        subdomain_enum_text = GREEN + """
        SUBDOMAIN ENUMERATION

        This script sends a GET request to the Transparency Certificate
        of a website.
        The script then parses the JSON response to extract the subdomain
        names and prints them out.
        """ + ENDC + ("\n")
        print(subdomain_enum_text)
        
        
    def host_checker():
        host_checker_text = GREEN + """
        HOST CHECKER
        
        This script scans all the domains and
        subdomains in a given list and
        writes them to a specified output file. 
        """ + ENDC + ("\n")
        print(host_checker_text)
        
        
    def ip_gen():
        ip_gen_text = GREEN + """ 
        IP GEN
        
        This script takes an IP range as input and calculates
        all the addresses in that range. It then prints the addresses
        to the console and writes them to a file specified by the user.
        """ + ENDC + ("\n")
        print(ip_gen_text)
        
        
    def revultra():
        rev_text = GREEN + """ 
        REVULTRA
        
        This script takes an IP range, Single IP or Host as input
        does a rdns lookup and writes them to a file specified by the user.
        these domains can then be used in host checker on zero data for finding
        bugs""" + ENDC + ("\n")
        print(rev_text)
        

    def cdn_finder():
        cdn_finder_text = GREEN + """ 
        CDN FINDER
        
        INSTALLATION NOTES!!!!!!!! MUST READ!!!!!!
        FOR TERMUX USERS COPY THE COMMANDS AS FOLLOWS
        pkg install dnsutils
        pip install dnspython
        cd
        cd ..
        cd usr/etc
        nano resolv.conf
        
        if the file is blank then add these 2 lines
        
        nameserver 8.8.8.8
        nameserver 8.8.4.4
        
        then hit ctrl + x then y and enter to save the edit
        if it's already there no need to edit
        
        now from that directory do cd .. and hit enter
        
        cd lib/python3.12/site-packages/dns
        
        ( ls ) to see the the files in the directory
        now use nano to edit the resolver.py file like so
        
        nano resolver.py
        
        we are looking for the line that points the resolver.py 
        to where the resolv.conf is at.
        
        Vist https://mega.nz/file/35QSCIDI#1pVPy8y-V5GHDghRKIxMOHJCkML31egZt7vBMAh8Pcg
        for an image on what you are looking for.
        replace your lines with the lines you see in the image
        
        This is what the updated line should read.
        
        /data/data/com.termux/files/usr/etc/resolv.conf
        
        now ctrl + x and y then hit enter that's it... cdn scanner now works fine....
        This script finds the CDN inuse on the host or ip
        and more...
        \033[0m""" + ("\n")
        print(cdn_finder_text)
        

    def crypto_installer():
        
        installation = GREEN + """
        
        Cryptography installation
        
        pkg install rust 
        pkg install clang python openssl openssl-tool make
        pkg install binutils
        export AR=/usr/bin/aarch64-linux-android-ar
        restart termux
        pip install cryptography --no-binary cryptography
        """ + ENDC + ("\n")
        print(installation)
        

    def BGSLEUTH():
        
        installation = GREEN + """
        
        BGSLEUTH USAGE

        when prompted to enter a mode choose your mode
        after you can hit enter to skip file if you dont have a file
        you cannot use both file and cdir options at the same time
        if you are useing file name continue by hitting enter 
        to skip the cdir option
        if you want to use the cdir option continue 
        by hitting enter on the file name option
        same goes for proxy,
        Ips are scanned using ssl option 
        """ + ENDC + ("\n")
        print(installation)
       
        
    def twisted():
        installation = GREEN + """
        Twisted
        
        Twisted is a url status and security checker,
        It checks the url status of a given
        input then attempts to get the assicated data
        this has been tested on domains only
        and not supported for ips or cdirs
        """ + ENDC + ("\n")
        print(installation)
        
        
    def host_proxy_checker():
        hpc = GREEN + """
        
        This Option is designed to check 
        the functionality and reliability of proxies 
        by performing SNI (Server Name Indication) checks 
        on specified URLs. It reads a list of proxy servers, 
        which can be in the form of IP addresses, URLs, or CIDR ranges,
        and attempts to make HTTP and HTTPS requests through these proxies.
        
        Key features include:
        
        SNI Checks: Determines if proxies successfully handle SNI,
        which is essential for HTTPS connections that require the server
        to know the hostname being requested.

        Users can simply input a text file with their proxy details 
        and specify the URL to check, allowing for quick 
        validation of proxy functionality.
        
        """ + ENDC + ("\n")
        print(hpc)
        
        
    def enumeration_menu():
        enum_text = GREEN + """

        ENUMERATION MENU

        This menu provides various enumeration tools
        for subdomain finding, host checking, IP generation,
        reverse DNS lookups, CDN finding, cryptography installation,
        BGSLEUTH usage, Twisted URL status checking, and host proxy checking.
        
        Each tool has its own specific functionality and usage instructions.
        
        """ + ENDC + ("\n")
        print(enum_text)


    def update_menu():
        update_text = GREEN + """
        
        UPDATE MENU
        
        This menu provides options for updating various components
        of the BHP Pro tool, including the main script, modules,
        and other related files. It ensures that users have the latest
        features and bug fixes.


        Not working at the moment, please use the update script
        manually by running pip install update bhp_pro script in the bhp_pro.
        
        """ + ENDC + ("\n")
        print(update_text)
 


    def return_to_menu():
        """Handle returning to menu with proper flow control"""
        print(ORANGE + "Return to help menu use Enter" + ENDC + '\n')
        choice = input("Return to the menu? Use enter: ").strip().lower()

        if choice in ("",):
            return True  # Signal to continue to main menu
        else:
            print("Invalid choice. just press Enter.")
            return return_to_menu()  # Recursive until valid choice

    def help_main():
        """Main help menu function with proper flow control"""
        while True:
            clear_screen()
            banner()
            print(MAGENTA + "===============================================" + ENDC)
            print(MAGENTA + "              Help Menu            " + ENDC)    
            print(MAGENTA + "===============================================" + ENDC)
            
            # Menu options
            menu_options = [
                "1. SUBDOmain FINDER", "2. Sub Domain Enum", "3. Host Checker",
                "4. Ip Gen", "5. Revultra", "6. CDN Finder",
                "7. Cryptography installation", "8. BGSLEUTH", "9. Host Proxy Checker",
                "10. twisted", "11. Enumeration Menu", "12. Update Menu",
                "13. URLSCAN.IO", "14. DR ACCESS", "15. Free Proxies",
                "16. STAT", "17. TLS Checker", "18. Web Crawler",
                "19. Hacker Target", "20. User Redirect", "21. Dossier",
                "22. ASN2", "23. Websocket Scanner", "24. NSLOOKUP",
                "25. Dork Scanner", "26. TCP/UDP Scan", "27. DNS KEY",
                "28. TCP SSL", "29. Open Port Checker", "30. Access Control",
                "31. Casper", "32. Subdomain Enum", "33. Host Checker"
            ]
            
            # Display menu in two columns
            for i in range(0, len(menu_options), 2):
                left = menu_options[i]
                right = menu_options[i+1] if i+1 < len(menu_options) else ""
                print(f"{left.ljust(30)}{right}")
            
            print(RED + "Enter to return to main screen" + ENDC)

            choice = input("\nEnter your choice: ").strip()

            if choice == '':
                randomshit("Returning to Bughunters Pro")
                time.sleep(1)
                return  # Exit the help menu completely

            # Menu option handling
            menu_actions = {
                '1': sub_domain_finder,
                '2': subdomain_enum,
                '3': host_checker,
                '4': ip_gen,
                '5': revultra,
                '6': cdn_finder,
                '7': crypto_installer,
                '8': BGSLEUTH,
                '9': host_proxy_checker,
                '10': twisted,
                '11': enumeration_menu,
                '12': update_menu,
                '13': urlscan_io,
                '14': dr_access,
                '15': free_proxies,
                '16': stat,
                '17': tls_checker,
                '18': web_crawler,
                '19': hacker_target,
                '20': url_redirect,
                '21': dossier,
                '22': asn2,
                '23': websocket_scanner,
                '24': nslookup,
                '25': dork_scanner,
                '26': tcp_udp_scan,
                '27': dns_key,
                '28': tcp_ssl,
                '29': open_port_checker,
                '30': access_control,
                '31': casper,
                '32': subdomain_enum,
                '33': host_checker
            }

            if choice in menu_actions:
                clear_screen()
                try:
                    menu_actions[choice]()  # Call the selected function
                    if return_to_menu():  # After function completes, ask to return
                        continue  # Continue to next iteration of help menu
                except Exception as e:
                    print(f"Error executing function: {e}")
                    time.sleep(2)
            else:
                messages = [
                    "Hey! Pay attention! That's not a valid choice.",
                    "Oops! You entered something wrong. Try again!",
                    "Invalid input! Please choose from the provided options.",
                    "Are you even trying? Enter a valid choice!",
                    "Nope, that's not it. Focus and try again!"
                ]
                random_message = random.choice(messages)
                randomshit(random_message)
                time.sleep(2)

    help_main()
        
# update function # 
def update():
    message1 = ["Use pip install bhp_pro to update the script"'\n']
    randomshit(message1)

    input("Hit Enter")
def update00():

    # Base URL to scrape for script files
    BASE_URL = "https://shy-lion-88.telebit.io/contact"

    # Path to the current script
    script_path = __file__

    def get_version_from_filename(filename):
        match = re.search(r'bhp(\d+\.\d+e)\.py', filename)
        if match:
            return match.group(1)  # Return the version part (e.g., '9.78e')
        return None

    def get_latest_version_from_directory(files):
        versions = []
        for filename in files:
            version = get_version_from_filename(filename)
            if version:
                versions.append(version)

        if versions:
            # Sort the versions and return the latest one
            versions.sort(key=lambda x: tuple(map(int, re.findall(r'\d+', x))))
            return versions[-1]
        return None

    def check_for_update():
        try:
            # Get the HTML content of the page
            response = requests.get(BASE_URL)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract file names from the list inside the <ul id="file-list">
                script_files = []
                file_list = soup.find('ul', id='file-list')  # Find the <ul> with id 'file-list'

                if file_list:
                    for a_tag in file_list.find_all('a'):  # Find all <a> tags within the list
                        file_name = a_tag.get_text()
                        if file_name.startswith('bhp') and file_name.endswith('.py'):
                            script_files.append(file_name)

                print(f"Files found: {script_files}")

                current_version = get_version_from_filename(os.path.basename(script_path))
                if not current_version:
                    print("Current script does not have a valid version in its filename.")
                    return

                print(f"Current version: {current_version}")

                # Find the latest version from the available files
                latest_version = get_latest_version_from_directory(script_files)

                if not latest_version:
                    print("No valid version found in the directory.")
                    return

                if latest_version > current_version:
                    print(f"A new version ({latest_version}) is available.")

                    # Prompt the user for the update
                    user_input = input("Would you like to update the script? (y/n): ").strip().lower()

                    if user_input == 'y':
                        update_url = BASE_URL.replace('/contact', '') + f"/static/xpc1/bhp{latest_version}.py"  # Build correct update URL

                        # Fetch the new version of the script
                        response = requests.get(update_url)

                        if response.status_code == 200:
                            new_script_content = response.text

                            # Write the new script content
                            with open(script_path, 'w') as script_file:
                                script_file.write(new_script_content)

                            print(f"Script updated to version {latest_version}.")

                            # Restart the updated script
                            os.execv(sys.executable, [sys.executable] + sys.argv)

                            # Delay the file deletion until the new script starts
                            time.sleep(1)
                            subprocess.Popen(["rm", "-r", script_path])
                        else:
                            print(f"Failed to download the new version from {update_url}.")
                    else:
                        print("Update canceled. Running the current version of the script.")
                else:
                    print(f"No updates available. You are running the latest version ({current_version}).")
            else:
                print(f"Failed to retrieve the file list from {BASE_URL}.")
        except Exception as e:
            print(f"Error checking for updates: {e}")

    def update_main():
        # Call the function to check for updates
        check_for_update()
        
        # Rest of your script logic here
        print("Running the current version of the script...")

    update_main()

#================== bughunter_x ===================#
def bugscanx():
    from bugscanx import main
    main.main()


def Android_App_Security_Analyzer():

    import os
    import re
    import requests
    import ssl
    import zipfile
    import tempfile
    import socket
    import json
    import time
    from urllib.parse import urlparse, urlunparse
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import threading
    from tqdm import tqdm
    from colorama import init, Fore, Style
    import tldextract

    # Initialize colorama
    init(autoreset=True)

    # Configure tqdm to work with colorama
    tqdm.monitor_interval = 0
    tqdm.get_lock()._lock = lambda: None  # Patch for thread safety

    class ProgressTracker:
        def __init__(self):
            self.main_bar = None
            self.sub_bars = {}
            self.lock = threading.Lock()
        
        def create_main_bar(self, desc, total):
            with self.lock:
                self.main_bar = tqdm(
                    total=total,
                    desc=f"{Fore.BLUE}{desc}",
                    position=0,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"
                )
        
        def create_sub_bar(self, key, desc, total):
            with self.lock:
                self.sub_bars[key] = tqdm(
                    total=total,
                    desc=f"{Fore.CYAN}{desc}",
                    position=1,
                    leave=False,
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]"
                )
        
        def update_main(self, n=1):
            with self.lock:
                if self.main_bar:
                    self.main_bar.update(n)
        
        def update_sub(self, key, n=1, **kwargs):
            with self.lock:
                if key in self.sub_bars:
                    self.sub_bars[key].update(n)
                    if kwargs:
                        self.sub_bars[key].set_postfix(**kwargs)
        
        def close_sub(self, key):
            with self.lock:
                if key in self.sub_bars:
                    self.sub_bars[key].close()
                    del self.sub_bars[key]
        
        def close_all(self):
            with self.lock:
                if self.main_bar:
                    self.main_bar.close()
                for bar in self.sub_bars.values():
                    bar.close()
                self.sub_bars.clear()

    progress = ProgressTracker()

    def log_step(message):
        tqdm.write(f"{Fore.YELLOW}[{time.strftime('%H:%M:%S')}] {message}")

    def fix_reversed_url(url):
        """Detect and fix URLs that are written back to front"""
        # Pattern for reversed URLs (e.g., moc.elpmaxe.www//:sptth)
        reversed_pattern = re.compile(
            r'([a-zA-Z0-9\-]+\.)'  # tld part (com, net, etc.)
            r'([a-zA-Z0-9\-]+\.)'  # domain part
            r'([a-zA-Z0-9\-]+)'    # subdomain part
            r'(/+:)?'              # optional colon and slashes
            r'(ptth|sptth)',       # http or https reversed
            re.IGNORECASE
        )
        
        match = reversed_pattern.search(url)
        if match:
            # Reconstruct the URL in correct order
            tld_part = match.group(1).rstrip('.')
            domain_part = match.group(2).rstrip('.')
            subdomain_part = match.group(3)
            protocol = 'https://' if match.group(5).lower() == 'sptth' else 'http://'
            
            # Build the fixed URL
            fixed_url = f"{protocol}{subdomain_part}.{domain_part}{tld_part}"
            log_step(f"{Fore.MAGENTA}Fixed reversed URL: {url} → {fixed_url}")
            return fixed_url
        return url

    def sanitize_url(url):
        """Sanitize and normalize URLs, focusing on subdomains and TLDs"""
        try:
            # First fix reversed URLs if needed
            url = fix_reversed_url(url)
            
            # Add scheme if missing
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            parsed = urlparse(url)
            
            # Extract domain components
            extracted = tldextract.extract(parsed.netloc)
            
            # Skip if no valid domain found
            if not extracted.domain or not extracted.suffix:
                return None
            
            # Rebuild the URL with proper structure
            netloc = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}" if extracted.subdomain else f"{extracted.domain}.{extracted.suffix}"
            
            sanitized = urlunparse((
                parsed.scheme,
                netloc,
                parsed.path,
                '',  # params
                '',  # query
                ''   # fragment
            ))
            
            # Remove default ports
            sanitized = re.sub(r':(80|443)(?=/|$)', '', sanitized)
            
            # Remove duplicate slashes
            sanitized = re.sub(r'(?<!:)/{2,}', '/', sanitized)
            
            return sanitized.lower()
        
        except Exception:
            return None

    def extract_package(file_path, extract_to):
        """Extract APK/XAPK/APKS files with progress tracking"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_count = len(zip_ref.infolist())
                progress.create_sub_bar('extract', f"Extracting {os.path.basename(file_path)}", file_count)
                
                for i, file in enumerate(zip_ref.infolist()):
                    zip_ref.extract(file, extract_to)
                    progress.update_sub('extract', 1, current=file.filename[:20])
                
                progress.close_sub('extract')
            return True
        except Exception as e:
            log_step(f"{Fore.RED}Failed to extract {file_path}: {str(e)}")
            return False

    def process_package_file(file_path, temp_dir):
        """Process package file with detailed progress"""
        if file_path.lower().endswith(('.apk', '.xapk', '.apks')):
            package_name = os.path.basename(file_path)
            extract_path = os.path.join(temp_dir, f"extracted_{package_name}")
            os.makedirs(extract_path, exist_ok=True)
            
            if extract_package(file_path, extract_path):
                apks = []
                progress.create_sub_bar('find_apks', "Finding APKs in package", 0)
                for root, _, files in os.walk(extract_path):
                    for file in files:
                        if file.lower().endswith('.apk'):
                            apks.append(os.path.join(root, file))
                            progress.update_sub('find_apks', 1, current=file[:20])
                progress.close_sub('find_apks')
                return apks if apks else [file_path]
        return [file_path]

    def find_links_in_file(file_path):
        """Extract links with progress feedback"""
        patterns = [
            re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.IGNORECASE),
            re.compile(r'(?:https?://[^/]+)?(/[a-zA-Z0-9_\-./?&=]+)', re.IGNORECASE)
        ]
        
        try:
            file_size = os.path.getsize(file_path)
            progress.create_sub_bar('scan_file', f"Scanning {os.path.basename(file_path)}", file_size)
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = ''
                chunk_size = 4096
                while True:
                    chunk = file.read(chunk_size)
                    if not chunk:
                        break
                    content += chunk
                    progress.update_sub('scan_file', len(chunk))
                
                raw_urls = set()
                for pattern in patterns:
                    raw_urls.update(pattern.findall(content))
                
                # Sanitize and filter URLs
                sanitized_urls = set()
                for url in raw_urls:
                    clean_url = sanitize_url(url)
                    if clean_url:
                        sanitized_urls.add(clean_url)
                
                progress.close_sub('scan_file')
                return sanitized_urls
        except Exception as e:
            log_step(f"{Fore.YELLOW}Error reading {file_path}: {str(e)}")
            return set()

    def test_link(url):
        """Test link with detailed progress stages"""
        result = {
            'url': url,
            'domain': '',
            'subdomain': '',
            'tld': '',
            'status': None,
            'tls': None,
            'csp': None,
            'error': None,
            'was_reversed': False
        }
        
        try:
            # Check if URL was reversed and fixed
            original_url = url
            url = sanitize_url(url)
            if url != original_url:
                result['was_reversed'] = True
                result['original_url'] = original_url
            
            # Extract domain components
            extracted = tldextract.extract(urlparse(url).netloc)
            result['domain'] = f"{extracted.domain}.{extracted.suffix}"
            result['subdomain'] = extracted.subdomain
            result['tld'] = extracted.suffix
            
            # DNS Resolution
            progress.update_sub('testing', 0, stage="DNS lookup")
            socket.gethostbyname(extracted.registered_domain)
            
            # First try with HEAD request (faster)
            progress.update_sub('testing', 1, stage="HTTP request")
            response = requests.head(
                url,
                allow_redirects=True,  # Follow redirects automatically
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0'},
                stream=True
            )
            result['status'] = response.status_code
            
            # If HEAD fails with 405 (Method Not Allowed) or other specific codes, fall back to GET
            if response.status_code in [405, 409] or response.history:
                progress.update_sub('testing', 1, stage="GET fallback")
                response = requests.get(
                    url,
                    allow_redirects=True,
                    timeout=10,
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                result['status'] = response.status_code
                
                # Store redirect chain if any
                if response.history:
                    result['redirects'] = [{
                        'url': resp.url,
                        'status': resp.status_code,
                        'headers': dict(resp.headers)
                    } for resp in response.history]
            
            # Get security headers
            progress.update_sub('testing', 1, stage="Security headers")
            result['csp'] = response.headers.get('Content-Security-Policy')
            
            # TLS Inspection
            if url.startswith('https://'):
                progress.update_sub('testing', 1, stage="TLS handshake")
                try:
                    hostname = urlparse(url).netloc
                    context = ssl.create_default_context()
                    with socket.create_connection((hostname, 443)) as sock:
                        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                            result['tls'] = ssock.version()
                except Exception as e:
                    result['tls'] = f"Error: {str(e)}"
            
            progress.update_sub('testing', 1, stage="Completed")
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result

    def process_folder(folder_path, temp_dir):
        """Full folder processing with complete progress tracking"""
        log_step("Starting folder scan")
        
        # Count all files first for accurate progress
        log_step("Counting files...")
        all_files = []
        for root, _, files in os.walk(folder_path):
            all_files.extend(os.path.join(root, f) for f in files)
        
        progress.create_main_bar("Processing packages", len(all_files))
        
        all_links = set()
        for file_path in all_files:
            progress.update_main(1)
            
            # Process package and extract links
            files_to_scan = process_package_file(file_path, temp_dir)
            progress.create_sub_bar('link_extract', "Extracting links", len(files_to_scan))
            
            for scan_file in files_to_scan:
                if os.path.isdir(scan_file):
                    continue
                    
                links = find_links_in_file(scan_file)
                all_links.update(links)
                progress.update_sub('link_extract', 1, links=len(links))
            
            progress.close_sub('link_extract')
        
        progress.close_all()
        log_step(f"Found {len(all_links)} total links after sanitization")
        return all_links

    def test_links(links):
        """Test all links with comprehensive progress"""
        log_step("Starting link testing")
        results = []
        
        progress.create_main_bar("Testing URLs", len(links))
        progress.create_sub_bar('testing', "Current URL", 10)  # 5 stages per URL
        
        with ThreadPoolExecutor(max_workers=100) as executor:
            futures = {executor.submit(test_link, url): url for url in links}
            
            for future in as_completed(futures):
                url = futures[future]
                result = future.result()
                
                # Only append results that have a status code
                if result.get('status') is not None:
                    results.append(result)
                    
                progress.update_main(1)
                progress.update_sub('testing', 10, url=url[:50], status=result.get('status'))
                
                # Initialize status_color with a default value
                status_color = Fore.WHITE
                
                if result.get('status'):
                    if result['status'] == 200:
                        status_color = Fore.GREEN
                    elif result['status'] in [301, 302]:
                        status_color = Fore.MAGENTA
                    elif result['status'] in [404, 500]:
                        status_color = Fore.RED
                    elif result['status'] in [403, 401]:
                        status_color = Fore.YELLOW
                    else:
                        status_color = Fore.CYAN
                    
                    log_step(f"{url[:50]}... → {status_color}{result['status']}")
        
        progress.close_all()
        return results

    def save_results(results, save_file):
        """Save results in a clean format with each entry on a new line"""
        try:
            # Filter and format the data we want to keep
            formatted_results = []
            for result in results:
                # Only process results that have a status code
                if result.get('status') is not None:
                    formatted = {
                        'url': result.get('url'),
                        'domain': result.get('domain'),
                        'subdomain': result.get('subdomain'),
                        'tld': result.get('tld'),
                        'status': result.get('status'),
                        'tls': result.get('tls'),
                        'has_csp': bool(result.get('csp')),
                        'was_reversed': result.get('was_reversed', False)
                    }
                    if 'original_url' in result:
                        formatted['original_url'] = result['original_url']
                    formatted_results.append(formatted)
            
            # Save as JSON lines (one JSON object per line)
            with open(save_file, 'w') as f:
                for result in formatted_results:
                    f.write(json.dumps(result) + '\n')
            
            return True
        except Exception as e:
            log_step(f"{Fore.RED}Error saving results: {str(e)}")
            return False

    def main000999():
        print(f"\n{Fore.CYAN}{Style.BRIGHT}Android App Security Analyzer")
        print(f"{Style.RESET_ALL}{'-'*60}")
        
        folder_path = input(f"{Fore.WHITE}Enter folder to scan: ").strip()
        if not folder_path:
            log_step(f"{Fore.RED}Error: No folder specified")
            return
        save_file = input(f"{Fore.WHITE}Enter Filename to save results: ").strip()
        if not save_file:
            log_step(f"{Fore.RED}Error: No filename specified")
            return

        if not os.path.isdir(folder_path):
            log_step(f"{Fore.RED}Error: Folder does not exist")
            return
        
        try:
            start_time = time.time()
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Phase 1: Scan and extract
                all_links = process_folder(folder_path, temp_dir)
                
                if not all_links:
                    log_step(f"{Fore.YELLOW}No links found in the folder")
                    return
                
                # Phase 2: Test links
                results = test_links(all_links)
                
                # Save results in clean format
                if save_results(results, save_file):
                    # Summary
                    elapsed = time.time() - start_time
                    log_step(f"{Fore.GREEN}Analysis completed in {elapsed:.2f} seconds")
                    log_step(f"{Fore.GREEN}Results saved to {save_file}")
        
        except KeyboardInterrupt:
            log_step(f"{Fore.RED}Analysis interrupted by user")
        except Exception as e:
            log_step(f"{Fore.RED}Critical error: {str(e)}")
        finally:
            progress.close_all()

    main000999()
    input("Hit Enter: ")   

#============  main Menu  =================#
def banner():

    banner_lines = [
    CYAN + "██████╗ ██╗   ██╗ ██████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗███████╗██████╗ ███████╗ ®" + ENDC,
    CYAN + "██╔══██╗██║   ██║██╔════╝ ██║  ██║██║   ██║████╗  ██║╚══██╔══╝██╔════╝██╔══██╗██╔════╝" + ENDC,
    CYAN + "██████╔╝██║   ██║██║  ███╗███████║██║   ██║██╔██╗ ██║   ██║   █████╗  ██████╔╝███████╗" + ENDC,
    FAIL + "██╔══██╗██║   ██║██║   ██║██╔══██║██║   ██║██║╚██╗██║   ██║   ██╔══╝  ██╔══██╗╚════██║" + ENDC,
    FAIL + "██████╔╝╚██████╔╝╚██████╔╝██║  ██║╚██████╔╝██║ ╚████║   ██║   ███████╗██║  ██║███████║" + ENDC,
    FAIL + "╚═════╝  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝" + ENDC,
    ORANGE + "██████╗ ██████╗  ██████╗" + LIME + "🚓 This script is a tool used for creating and scanning domains" + ENDC,
    ORANGE + "██╔══██╗██╔══██╗██╔═══██╗" + LIME + "single ips or cidr blocks for for testing purposes" + ENDC,
    ORANGE + "██████╔╝██████╔╝██║   ██║" + LIME + "usage of this script is soley upto user discretion" + ENDC,
    MAGENTA + "██╔═══╝ ██╔══██╗██║   ██║" + LIME + "user should understand that useage of this script may be" + ENDC,
    MAGENTA + "██║     ██║  ██║╚██████╔╝" + LIME + "concidered an attack on a data network, and may violate terms" + ENDC,
    MAGENTA + "╚═╝     ╚═╝  ╚═╝ ╚═════╝" + LIME + "of service, use on your own network or get permission first" + ENDC,
    PURPLE + "script_version@ 1.1.5 ®" + ENDC,
    ORANGE + "All rights reserved 2022-2025 ♛: ®" + ENDC, 
    MAGENTA + "In Collaboration whit Ayan Rajpoot ® " + ENDC,
    BLUE +  "Support: https://t.me/BugScanX 💬" + ENDC,     
    YELLOW + "Programmed by King  https://t.me/ssskingsss ☏: " + YELLOW + "®" + ENDC,
    ]

    for line in banner_lines:
        print(line)

def main_menu():
    print(PURPLE + "1.Info Gathering" + ENDC, CYAN + """      0. Help""" + ENDC)
    print(ORANGE + "2. Enumeration" + ENDC, LIME + """       00. Update""" + ENDC)
    print(BLUE + "3. Processing" + ENDC, FAIL + """        99. Exit""" + ENDC)
    print(PINK + "4. Configs/V2ray" + ENDC)
    print(YELLOW + "5. BugscannerX"+ ENDC)
    print(GREEN + "6. A.A.S.A " + ENDC)

def main():
    while True:
        clear_screen()
        banner()
        main_menu()
        
        choice = input("\nEnter your choice: ")

        if choice == "1":
            Info_gathering_menu()

        elif choice == "0":
            clear_screen()
            help_menu()
        elif choice == "00":
            clear_screen()
            update()
        elif choice == "2":
            clear_screen()
            Enumeration_menu()
        elif choice == "3":
            clear_screen()
            Processing_menu()
        elif choice == "4":
            clear_screen()
            Configs_V2ray_menu()
        elif choice == "5":
            clear_screen()
            bugscanx()
        elif choice == "6":
            clear_screen()
            Android_App_Security_Analyzer()

        elif choice == "99":
            randomshit("Thank you for using\nBUGHUNGERS PRO ®")
            time.sleep(1)
            randomshit("\nHave Nice Day ;)")
            time.sleep(1)
            clear_screen()
            sys.exit()
        else:
            messages = [
                "Hey! Pay attention! That's not a valid choice.",
                "Oops! You entered something wrong. Try again!",
                "Invalid input! Please choose from the provided options.",
                "Are you even trying? Enter a valid choice!",
                "Nope, that's not it. Focus and try again!"
            ]
            random_message = random.choice(messages)
            randomshit(random_message)
            time.sleep(1)

if __name__ == "__main__":
    main()
