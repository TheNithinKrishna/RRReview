from main.rrr import main


if __name__ == "__main__":
    main()

# import os
# import subprocess
# import time
# from random import randint
# from stdlib.creds import email_cred

# if __name__ == "__main__":
#     email_db = email_cred()
#     script_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'main')

#     commands = [
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR1', email_db['rrr1_email_address'], email_db['rrr1_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR2', email_db['rrr2_email_address'], email_db['rrr2_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR3', email_db['rrr3_email_address'], email_db['rrr3_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR4', email_db['rrr4_email_address'], email_db['rrr4_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR5', email_db['rrr5_email_address'], email_db['rrr5_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR11', email_db['rrr11_email_address'], email_db['rrr11_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR14', email_db['rrr14_email_address'], email_db['rrr14_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR17', email_db['rrr17_email_address'], email_db['rrr17_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR23', email_db['rrr23_email_address'], email_db['rrr23_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR26', email_db['rrr26_email_address'], email_db['rrr26_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR27', email_db['rrr27_email_address'], email_db['rrr27_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR28', email_db['rrr28_email_address'], email_db['rrr28_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR29', email_db['rrr29_email_address'], email_db['rrr29_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR30', email_db['rrr30_email_address'], email_db['rrr30_email_password']],
#         ['python', '-m', 'idlelib.idle', '-r', os.path.join(script_directory, 'rrr.py'), 'RRR31', email_db['rrr31_email_address'], email_db['rrr31_email_password']]

#     ]

#     for command in commands:
#         random_sleep_time = randint(2, 2)
#         process = subprocess.Popen(command)
#         time.sleep(random_sleep_time)
