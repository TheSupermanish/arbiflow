from exchange_config import *
import subprocess
import time
import sys
import ccxt
import os
from colorama import Style, init, Fore
init()
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
print("\033[2J\033[H", end="")  # Clear screen, move to top

print(r'''
 $$$$$$\            $$\       $$\ $$$$$$$$\ $$\                         
$$  __$$\           $$ |      \__|$$  _____|$$ |                        
$$ /  $$ | $$$$$$\  $$$$$$$\  $$\ $$ |      $$ | $$$$$$\  $$\  $$\  $$\ 
$$$$$$$$ |$$  __$$\ $$  __$$\ $$ |$$$$$\    $$ |$$  __$$\ $$ | $$ | $$ |
$$  __$$ |$$ |  \__|$$ |  $$ |$$ |$$  __|   $$ |$$ /  $$ |$$ | $$ | $$ |
$$ |  $$ |$$ |      $$ |  $$ |$$ |$$ |      $$ |$$ |  $$ |$$ | $$ | $$ |
$$ |  $$ |$$ |      $$$$$$$  |$$ |$$ |      $$ |\$$$$$$  |\$$$$$\$$$$  |
\__|  \__|\__|      \_______/ \__|\__|      \__| \______/  \_____\____/                                                                                                                                                                           
''')

args = sys.argv
mode = args[1]
if renewal:
    balance = args[3]
    pair = args[4]
    renew = args[2]
    ex_list = args[5]
else:
    balance = args[2]
    pair = args[3]
    renew = "525600"
    ex_list = args[4]
i = 0
if mode != 'demo':
    real_balance = 0
    for ex_str in ex_list.split(','):
        bal = ex[ex_str].fetchBalance()
        real_balance += float(bal[pair.split('/')[1]]['total'])
    with open(f"real_balance.txt", "w") as f:
        f.write(str(real_balance))
else:
    with open(f"real_balance.txt", "w") as f:
        f.write(str(balance))

while True:
    with open(f"real_balance.txt", "r") as f:
        balance = str(f.read())
    if i >= 1 and p.returncode == 1:
        sys.exit(1)
    if mode == "demo":
        p = subprocess.run(
            [python_command, "demo-bot.py", pair, balance, renew, pair, ex_list])
    elif mode == "real":
        p = subprocess.run([python_command, "bot.py", pair,
                           balance, renew, pair, ex_list])
    else:
        printerror(m=f"mode input is incorrect.")
        sys.exit(1)
    i += 1
