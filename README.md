# ethmon
Very simple python script for monitoring Claymore's Dual Ethereum miner. Sure it's not the best solution to control a huge amount of rigs, but if you have a few and don't need complicated event analyzing and autorecover features - feel free to use it.  
The script will notify you via email if:
  1. Average hashrate during 5 minutes is less than a configured limit
  2. GPU temperature is higher than a configured limit
  3. GPU fan speed is less than a configured limit (possibly fan is broken)
  4. Number of invalid shares increasing
  5. Number of active cards(GPUS) is less than a configured limit
  6. Miner was restarted
  7. System was rebooted 
  8. Pool is unreachable
  
The script will:
  1. Start miner if there's no such process
  2. Restart miner if there's more then 1 miner running
  3. Restart miner if it's unreachable via API
  4. Restart miner if invalid shares increasing
  5. Restart miner if number of active cards (GPUs) is less than a configured limit
  6. Restart system if average hashrate during 5 mins is less than a limit two times in a row

## Dependencies:  
Python uptime package. Installation:  
    *pip install uptime*
  
## Setup:  
  Just set all necessary parameters at config section & add miner to Windows startup
  
  
## Screenshot
![Alt text](https://github.com/amravyan/ethmon/raw/master/screen.JPG "Optional Title")  

All comments and additions are welcome.
