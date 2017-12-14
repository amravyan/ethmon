# ethmon
Python script for monitoring Claymore's Dual Ethereum miner

Very simple python script for monitoring Claymore's Dual Ethereum miner. It will notify you via email if:
  1. Hashrate is less than a configured limit
  2. GPU temperature is higher than a configured limit
  3. GPU fan speed is less than a configured limit (possibly fan is broken)
  4. Number of invalid shares increasing
  5. Miner was restarted
  6. System was rebooted
  
Setup:
  Just set all necessary parameters at config section
