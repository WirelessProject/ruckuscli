# user_location

## Requirments
1. Get user location (connected AP's name).
```
./user_location USERNAME
```

## Finished
* Show the queried user's location.

* Show the queried user's device OS type & hostname.

## Reference
### Code
* `../reference/collect.py`

### ZD CLI Command
* `show wlan name <wlan> stations`
	* find the AP's MAC addr which the user is connecting
* `show ap mac <AP MAC addr>`
	* look up the AP's device name using AP's MAC addr
* `show current-active-clients mac <client device MAC addr>`
	* show the details of the user's device (OS type, hostname, etc)


