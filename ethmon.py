import socket
import json
import smtplib
import time
import statistics
import os
import logging
import uptime

###################################################CONFIG##############################################################


# email
email_user = 'user@gmail.com'
email_password = 'gmailPassword'
recipient = ['person1@gmail.com', 'person2@gmail.com']


# miner
miner_ip = '127.0.0.1'
miner_port = 3333
miner_password = 'password'
process_name = 'EthDcrMiner64.exe'
pools = ['eth-eu1.nanopool.org', 'eth-eu2.nanopool.org', 'eth-us-east1.nanopool.org', 'eth-us-west1.nanopool.org',
         'eth-asia1.nanopool.org']
pool_port = 9999
miner_path = 'C:\Claymore10.2\EthDcrMiner64.exe'
epool = 'eth-eu1.nanopool.org:9999'
ewal = 'wallet.worker1/mail@gmail.com'
epsw = 'x'
dcoin = 'sia'
dpool = 'stratum+tcp://sia-eu1.nanopool.org:7777'
dwal = 'wallet/worker1/mail@gmail.com'
dpsw = 'x'
ftime = '10'
mpsw = 'password'

# limits
hashrate_limit = 100000 	#h/s
fan_speed_limit = 50		#percent    
gpu_temp_limit = 65			#Celsius
uptime_limit = 180			#seconds
cards_limit = 6

# logging
log_name = 'ethmon.log'


#######################################################################################################################

def get_data(ip, port, password, logger):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    try:
        sock.connect(server_address)
    except Exception as e:
        logger.info('Miner socket ' + str(ip) + ':' + str(port) + ' is closed')
        return []
    request = '{\"id\":0,\"jsonrpc\":\"2.0\",\"method\":\"miner_getstat1\",\"psw\":\"' + password + '\"}'
    request = request.encode()
    try:
        sock.sendall(request)
    except Exception as e:
        logger('Sending data was aborted')
        return []
    try:
        data = sock.recv(512)
    except Exception as e:
        logger('Recieveing data was aborted')
        return []
    message = json.loads(data)
    sock.close()
    return message


def check_connection(address, port):
    s = socket.socket()
    try:
        s.connect((address, port))
        return True
    except Exception as e:
        return False
    finally:
        s.close()


def get_pid(procces):
    pids = []
    for pid in psutil.pids():
        p = psutil.Process(pid)
        if p.name() == procces:
            pids.append(p.pid)
    return pids


def send_email(user, pwd, recipient, subject, body, logger):
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        logger.info('Successfully sent the mail')
    except:
        logger.info('Failed to send mail')


def get_avg_hashrate_1m(ip, port, password, logger):
    hashrates = []
    for i in range(0, 5):
        data = get_data(ip, port, password, logger)
        try:
            hashrate = data['result'][2].split(';')[0]
        except Exception as e:
            logger.info('Data is empty or invalid')
            time.sleep(30)
            continue
        hashrates.append(float(hashrate))
        time.sleep(10)
        i += 1
    try:
        return statistics.mean(hashrates)
    except Exception as e:
        return 0


def config_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_name)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)
    return logger


def start_miner():
    command = 'start cmd.exe /k ' + miner_path + ' -epool ' + epool + ' -eval ' + ewal + ' -epsw ' + epsw + ' -dcoin ' + dcoin + ' -dpool ' + dpool + ' -dwal ' + dwal + ' -dpsw ' + dpsw + ' -ftime ' + ftime + ' -mpsw ' + mpsw
    os.system(command)


def stop_miner():
    os.system("taskkill /f /im EthDcrMiner64.exe")
    os.system("taskkill /f /im cmd.exe")


def main():
    invalid_shares_prev = 0
    previous_hashrate = hashrate_limit + 1
    previous_miner_uptime = 1
    sys_uptime = uptime.uptime()
    logger = config_logging()
    logger.info('Started ethmon')
    logger.info('System uptime is ' + str(sys_uptime) + ' seconds')
    if sys_uptime < uptime_limit:
        logger.info('System was rebooted, sending email')
        send_email(email_user, email_password, recipient, 'System was rebooted',
                   'Current system uptime is ' + str(sys_uptime) + ' s', logger)
    while True:
        # check miner process
        logger.info('Checking if miner is running...')
        pids = get_pid(process_name)
        if len(pids) == 0:
            logger.info('Miner is not running, sending email')
            send_email(email_user, email_password, recipient, 'Miner is not running',
                       'Miner is not running. Ethmon will try to start is manually', logger)
            logger.info('Starting miner.')
            start_miner()
            logger.info('Waiting for retry.')
            time.sleep(30)
            continue
        if len(pids) > 1:
            logger.info('More than one miner running, sending email')
            send_email(email_user, email_password, recipient, 'More than one miner running',
                       'Too many miners started, check the system', logger)
            logger.info('Stopping  miner.')
            stop_miner()
            logger.info('Starting miner.')
            start_miner()
            logger.info('Waiting for retry...')
            time.sleep(60)
            continue
        if len(pids) == 1:
            logger.info('Miner is running with PID ' + str(pids[0]))

        # check pool connection
        reachable = 0
        connection = check_connection(pools[0], pool_port)
        logger.info('Connection test result to ' + pools[0] + ' is : ' + str(connection))
        if connection is not True:
            logger.info('Main server ' + pools[0] + ' is unreachable, trying other...')
            for i in range(1, len(pools)):
                connection = check_connection(pools[i], pool_port)
                logger.info('Connection test result to ' + pools[i] + ' is : ' + str(connection))
                if connection is True:
                    logger.info('Server ' + pools[i] + ' is reachable')
                    send_email(email_user, email_password, recipient, 'Nanopool main server is unreachable',
                               'Nanopool main server is unreachable. Reachable server is ' + pools[
                                   i] + ' Check if miner switched correctly.', logger)
                    reachable = 1
                    break
        if connection is not True and reachable == 0:
            logger.info('Nanopool is unreachable, waiting 60 seconds for recheck...')
            time.sleep(60)
            continue

        # getting data from miner using API
        data = get_data(miner_ip, miner_port, miner_password, logger)
        retries = 0
        try:
            all = data['result'][6].split(';')
            temp = all[::2]
            fans = all[1::2]
            invalid_shares = int(data['result'][8].split(';')[0])
            miner_uptime = data['result'][1]
        except Exception as e:
            retries += 1
            if retries < 3:
                logger.info("Data is empty or invalid, waiting 60 seconds for recheck... Attempt # %d" % (retries + 1))
                time.sleep(60)
                continue
            else:
                logger.info("Too many unsuccessful attempts, sending email and restarting miner")
                send_email(email_user, email_password, recipient, 'Miner is unreachable, restarting',
                           'Miner is unrechable via API. Ethmon will try to restart is manually', logger)
                stop_miner()
                start_miner()
                continue

        # checking number of active cards
        cards = len(temp)
        logger.info('Number of active cards: ' + str(cards))
        if cards < cards_limit:
            logger.info('Number of active cards trigger, sending emails')
            send_email(email_user, email_password, recipient, 'Number of active cards less than a limit',
                       'Number of active cards: %d' % cards, logger)
            logger.info('Stopping  miner.')
            stop_miner()
            logger.info('Starting miner.')
            start_miner()

        # checking temp
        logger.info('GPU temp: ' + str(temp))
        high_temp = 0
        for i in range(0, len(temp)):
            if int(temp[i]) > gpu_temp_limit:
                high_temp += 1
            i += 1
        if high_temp != 0:
            logger.info('GPU high temp trigger, sending emails')
            send_email(email_user, email_password, recipient, 'GPU temp is HIGH',
                       'Number of GPUs with HIGH temp: %d' % high_temp, logger)

        # checking fans
        logger.info('Fan speed (%): ' + str(fans))
        stopped = 0
        for i in range(0, len(fans)):
            if int(fans[i]) < fan_speed_limit:
                stopped += 1
            i += 1
        if stopped != 0:
            logger.info('Fan low speed trigger, sending emails')
            send_email(email_password, email_password, recipient, 'Fan speed is LOW',
                       'Number of fans with LOW speed: %d' % stopped, logger)

        # invalid shares
        logger.info('Number of ETH invalid shares: ' + str(invalid_shares))
        if invalid_shares != invalid_shares_prev:
            logger.info('Invalid shares trigger, sending emails')
            send_email(email_user, email_password, recipient, 'Number of invalid shares increasing',
                       'Number of invalid shares: %s' % invalid_shares, logger)
            invalid_shares_prev = invalid_shares
            logger.info('Stopping  miner.')
            stop_miner()
            logger.info('Starting miner.')
            start_miner()
            invalid_shares_prev=0

        # miner uptime
        logger.info('Miner uptime is ' + miner_uptime + ' min')
        if int(miner_uptime) < int(previous_miner_uptime):
            logger.info('Miner was restarted')
            send_email(email_user, email_password, recipient, 'Miner was restarted',
                       'Miner uptime is ' + str(miner_uptime) + ' min', logger)
        previous_miner_uptime = miner_uptime

        hashrates = []
        i = 0
        logger.info('Previous hashrate is %s ' % "{:,.2f}".format(previous_hashrate / 1000) + ' Mh/s')
        logger.info('Started calculating hashrate...')
        for i in range(0, 5):
            hashrates.append(float(get_avg_hashrate_1m(miner_ip, miner_port, miner_password, logger)))
            time.sleep(10)
            i += 1
        current_hashrate = statistics.mean(hashrates)
        logger.info('Avg hashrate: ' + str("{:,.2f}".format(current_hashrate / 1000)) + " Mh/s")
        if current_hashrate < hashrate_limit:
            if previous_hashrate < hashrate_limit:
                logger.info('Avg hashrate <' + str(
                    "{:,}".format(hashrate_limit / 1000)) + ' Mh/s two times in a row, sending emails and reboot!')
                send_email(email_user, email_password, recipient,
                           'Alarm! Hashrate is less than' + str("{:,}".format(hashrate_limit / 1000)) + ' Mh/s',
                           'Current avg hashrate is %s h/s. Rebooting!' % "{:,.2f}".format(
                               current_hashrate), logger)
                os.system("shutdown -r -c \"low hashrate, rebooted by vahter!\"")
            logger.info('Avg hashrate <' + str("{:,}".format(hashrate_limit / 1000)) + ' Mh/s, sending emails')
            send_email(email_user, email_password, recipient,
                       'Warning! Hashrate is less than ' + str("{:,}".format(hashrate_limit / 1000)) + ' Mh/s',
                       'Current avg hashrate is %s h/s.' % "{:,.2f}".format(current_hashrate), logger)
        previous_hashrate = current_hashrate


if __name__ == '__main__':
    main()
