#!/usr/bin/env python3

from colorama import Fore, Style
from pwn import *
import signal, sys, os, time, subprocess, httpx, argparse

def def_handler(sig, frame):
    print(f"{Fore.RED}\n\n[!] Exiting...\n{Style.RESET_ALL}")
    sys.exit(1)

signal.signal(signal.SIGINT, def_handler)

def full_mode(domain):
    start_time = time.time()
    
    enumerate_subdomains(domain)
    output_file = f"output/{domain}.txt"

    check_alive_subdomains(output_file)
    alive_file = f"{output_file}_alive.txt"

    recon_subdomains(alive_file)

    run_subzy(alive_file)

    end_time = time.time()
    duration = end_time - start_time

    with open(output_file, 'r') as f:
        total_subdomains = len(f.readlines())
    with open(alive_file, 'r') as f:
        alive_subdomains = len(f.readlines())

    print(f"\n{Fore.LIGHTCYAN_EX}{'-'*40}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTGREEN_EX}[✔] FULL RECON SUMMARY{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLUE_EX}Domain: {Style.RESET_ALL}{domain}")
    print(f"{Fore.LIGHTBLUE_EX}Total subdomains found: {Style.RESET_ALL}{total_subdomains}")
    print(f"{Fore.LIGHTBLUE_EX}Alive subdomains: {Style.RESET_ALL}{alive_subdomains}")
    print(f"{Fore.LIGHTBLUE_EX}Total time: {Style.RESET_ALL}{round(duration, 2)} seconds")
    print(f"{Fore.LIGHTCYAN_EX}{'-'*40}{Style.RESET_ALL}\n")

def recon_subdomains(file):
    print(f"\n{Fore.LIGHTMAGENTA_EX}[...] Running recon (WebTech) on subdomains...{Style.RESET_ALL}\n")    
    time.sleep(2)

    with open(file, 'r') as f:
        subdomains = [line.strip() for line in f if line.strip()]

    for subdomain in subdomains:
        found = False
        for protocol in ["https", "http"]:
            url = f"{protocol}://{subdomain}"
            try:
                result = subprocess.run(
                    ["webtech", "--rua", "-u", url],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True
                )
                output = result.stdout

                if "Detected technologies:" in output:
                    print(f"{Fore.CYAN}[+] {url}{Style.RESET_ALL}")
                    tech_lines = False
                    for line in output.splitlines():
                        if line.strip().startswith("Detected technologies:"):
                            tech_lines = True
                            continue
                        if line.strip().startswith("Detected the following") or not line.strip():
                            break
                        if tech_lines and line.strip().startswith("-"):
                            print(f"   {Fore.YELLOW}{line.strip()}{Style.RESET_ALL}")
                    print()
                    found = True
                    break
            except Exception:
                continue
        if not found:
            pass

def run_subzy(file):
    print("\n")
    print(f"{Fore.LIGHTMAGENTA_EX}[...] Running subzy...{Style.RESET_ALL}\n")
    time.sleep(2)
    try:
        subprocess.run(f"subzy run --targets {file} --hide_fails", shell=True)
    except Exception as e:
        print(f"{Fore.RED}[-] Error running subzy: {e}{Style.RESET_ALL}")

def check_alive_subdomains(file):
    print("\n")
    print(f"{Fore.LIGHTMAGENTA_EX}[...] Checking alive subdomains...{Style.RESET_ALL}\n")
    time.sleep(2)
    with open(file, 'r') as f:
        subdomains = f.readlines()
    alive_subdomains = []
    for subdomain in subdomains:
        subdomain = subdomain.strip()
        is_alive = False
        for protocol in ["http", "https"]:
            try:
                response = httpx.get(f"{protocol}://{subdomain}", timeout=5, follow_redirects=True)
                if response.status_code:
                    alive_subdomains.append(subdomain)
                    print(f"{Fore.LIGHTGREEN_EX}[+] Alive: {subdomain} {Style.RESET_ALL}({response.status_code})")
                    is_alive = True
                    break
            except httpx.RequestError:
                continue
            
        if not is_alive:
            print(f"{Fore.LIGHTRED_EX}[-] Died: {subdomain}{Style.RESET_ALL}")

    print("\n")
    print(f"{Fore.LIGHTCYAN_EX}[+] Alive subdomains:{Style.RESET_ALL}\n")
    time.sleep(2)
    for alive in alive_subdomains:
        print(f"{Fore.LIGHTGREEN_EX}{alive}{Style.RESET_ALL}")
    
    with open(f"{file}_alive.txt", 'w') as out:
        out.writelines("\n".join(alive_subdomains))
    print(f"\n{Fore.YELLOW}[+] Alive subdomains saved to {Style.RESET_ALL}{out.name}\n")

def enumerate_subdomains(domain):
    print("\n")
    logbar = log.progress(f"{Fore.LIGHTMAGENTA_EX} Enumerating subdomains for {Fore.CYAN}{domain}{Fore.LIGHTMAGENTA_EX} ...{Style.RESET_ALL}")
    output_file = f"output/{domain}.txt"
    temp_file = f"output/{domain}_temp.txt"
    with open(temp_file, 'w') as file:
        subprocess.run(f"subfinder -d {domain} -all -silent", shell=True, stdout=file)
        print("\n")
        logbar.status(f"{Fore.LIGHTBLUE_EX}Please wait, we haven't finished...{Style.RESET_ALL}")
        subprocess.run(f"assetfinder -subs-only {domain}", shell=True, stdout=file)
    with open(temp_file, 'r') as file:
        subdomains = sorted(set(file.readlines()))
    with open(output_file, 'w') as file:
        file.writelines(subdomains)
    os.remove(temp_file)
    logbar.success(f"{Fore.LIGHTGREEN_EX}Subdomains enumerated successfully!{Style.RESET_ALL}")
    time.sleep(2)
    os.system(f"cat {output_file}")
    print(f"{Fore.LIGHTGREEN_EX}\n[+] Subdomains saved to {Style.RESET_ALL}{output_file}\n")

def main():
    os.system("clear && figlet SubDomRipper | lolcat")
    print(f"{Fore.LIGHTGREEN_EX+Style.BRIGHT}Made by OusCyb3rH4ck\n{Style.RESET_ALL}")

    parser = argparse.ArgumentParser(description="SubDomRipper - Subdomain Enumeration Tool")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    enum_parser = subparsers.add_parser("enum", help="Enumerate subdomains")
    enum_parser.add_argument("-d", "--domain", required=True)

    check_parser = subparsers.add_parser("check", help="Check which subdomains are alive")
    check_parser.add_argument("-f", "--file", required=True)

    recon_parser = subparsers.add_parser("recon", help="Run recon on a list of subdomains for retrieve WAF's, CMS's, technologies, etc.")
    recon_parser.add_argument("-f", "--file", required=True)

    subzy_parser = subparsers.add_parser("subzy", help="Run subzy against a list of subdomains")
    subzy_parser.add_argument("-f", "--file", required=True)

    full_parser = subparsers.add_parser("full", help="Full mode: enumerate, check, recon, takeover detection")
    full_parser.add_argument("-d", "--domain", required=True)

    args = parser.parse_args()

    if args.mode == "enum":
        enumerate_subdomains(args.domain)

    elif args.mode == "check":
        check_alive_subdomains(args.file)

    elif args.mode == "recon":
        recon_subdomains(args.file)

    elif args.mode == "subzy":
        run_subzy(args.file)
    
    elif args.mode == "full":
        full_mode(args.domain)

if __name__ == '__main__':
    main()
