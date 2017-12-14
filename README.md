# ethmon
Python script for monitoring Claymore's Dual Ethereum miner

Very simple python script for monitoring Claymore's Dual Ethereum miner. It will notify you via email if:
  1. Avg hashrate during 5 minutes is less than a configured limit
  2. GPU temperature is higher than a configured limit
  3. GPU fan speed is less than a configured limit (possibly fan is broken)
  4. Number of invalid shares increasing
  5. Miner was restarted
  6. System was rebooted
If avg hashrate during 5 mins is less than a limit two times in a row, ethmon will send email and reboot the system.
  
Setup:
  Just set all necessary parameters at config section
