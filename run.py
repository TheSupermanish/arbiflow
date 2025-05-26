from os import name, system
from colorama import Style, Fore, init
import time
import subprocess
from exchange_config import *
import sys
import os
sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
init()


def clear():
    if name == 'nt':
        system('cls')
    else:
        system('clear')


try:
    if len(sys.argv) < 3:
        input_list = ["mode (demo or real)", "renewal period (in minutes)",
                      "balance to use", "pair", "exchanges list separated without space with commas (,)"]
        if not renewal:
            input_list.remove("renewal period (in minutes)")
        output = []

        for inputt in input_list:
            output.append(input(inputt+" >>> "))

        mode = output[0]
        if not renewal:
            renew_time = "525600"
            balance = output[1]
            pair = output[2]
            ex_list = output[3]
        else:
            renew_time = output[1]
            balance = output[2]
            pair = output[3]
            ex_list = output[4]

        if mode != 'demo':
            real_balance = 0
            for ex_str in ex_list.split(','):
                bal = ex[ex_str].fetchBalance()
                real_balance += float(bal[pair.split('/')[1]]['total'])
            with open(f"real_balance.txt", "w") as f:
                f.write(str(real_balance))

        if renewal:
            subprocess.run([python_command, f"main.py", mode,
                           renew_time, balance, pair, ex_list])
        else:
            subprocess.run([python_command, f"main.py",
                           mode, balance, pair, ex_list])

    else:
        if (len(sys.argv) != 6) and renewal:
            printerror(
                m=f"Not correctly configured. Usage:\n \n{python_command} run.py <mode> <renewal period minutes> <balance to use> <crypto pair> <exchanges list separated without space with commas (,)>\n")
            sys.exit(1)
        if (len(sys.argv) != 5) and not renewal:
            printerror(
                m=f"Not correctly configured. Usage:\n \n{python_command} run.py <mode> <balance to use> <crypto pair> <exchanges list separated without space with commas (,)>\n")
            sys.exit(1)
        args = sys.argv

        mode = args[1]
        if not renewal:
            renew_time = "525600"
            balance = args[2]
            pair = args[3]
            ex_list = args[4]
        else:
            renew_time = args[2]
            balance = args[3]
            pair = args[4]
            ex_list = args[5]

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
        i = 0

        while True:
            with open(f"real_balance.txt", "r") as f:
                balance = str(f.read())
            if i >= 1 and p.returncode == 1:
                sys.exit(1)
            if mode == "demo":
                if os.path.exists('demo-bot.py'):
                    p = subprocess.run(
                        [python_command, "demo-bot.py", pair, balance, renew_time, pair, ex_list])
                else:
                    printerror(
                        m=f'please put the file "demo-bot.py" in the current directory.')
            elif mode == "real":
                # TODO: we need some work for the real bot, add some money in the dexes
                if os.path.exists('demo-bot.py'):
                    p = subprocess.run(
                        [python_command, "demo-bot.py", pair, balance, renew_time, pair, ex_list])
                else:
                    printerror(
                        m=f'please put the file "bot.py" in the current directory.')
            else:
                printerror(m=f"mode input is incorrect.")
                sys.exit(1)
            i += 1
except KeyboardInterrupt:
    if mode != 'demo':
        print(" \n \n \n")
        clear()
        answered = False
        while answered == False:
            inp = input(
                f"{get_time()} CTRL+C was pressed. Do you want to sell all crypto back? (y)es / (n)o\n \ninput: ")
            append_new_line('logs/logs.txt',
                            f"{get_time_blank()} INFO: ctrl+c was pressed.")
            if inp.lower() == "y" or inp.lower() == "yes":
                answered = True
                emergency_convert_list(pair, [ex_list.split(
                    ',')[i] for i in range(len(ex_list.split(',')))])
                sys.exit(1)
            if inp.lower() == "n" or inp.lower() == "no":
                answered = True
                sys.exit(1)
            else:
                answered = False
    else:
        pass
