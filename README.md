# ethmon
Very simple python script for monitoring Claymore's Dual Ethereum miner. Sure it's not the best solution to control a huge amount of rigs, but if you have a few and don't need complicated event analyzing and autorecover features - feel free to use it.  
The script will notify you via email if:
  1. Average hashrate during 5 minutes is less than a configured limit
  2. GPU temperature is higher than a configured limit
  3. GPU fan speed is less than a configured limit (possibly fan is broken)
  4. Number of invalid shares increasing
  5. Miner was restarted
  6. System was rebooted 
  7. Pool is unreachable
  
If average hashrate during 5 mins is less than a limit two times in a row, ethmon will send email and reboot the system.

## Dependencies:  
Python uptime package. Installation:  
    *pip install uptime*
  
## Setup:  
  Just set all necessary parameters at config section
  
  
## Screenshot
![Alt text](https://github.com/amravyan/ethmon/raw/master/screen.JPG "Optional Title")  

All comments and additions are welcome.
