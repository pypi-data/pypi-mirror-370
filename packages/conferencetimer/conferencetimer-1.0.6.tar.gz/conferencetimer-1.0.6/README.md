# Conference Timer

This project provides a timer and a remote PyQt6 application for a conference timer.
The talk and questions times can be set and the timer will provide the speakers with the remaining time.

After installing the package you can run the timer via
```bash
ctimer
```
and the remote via
```bash
cremote
```

Add the *-h* flag to see the allowed command line arguments.


Alternatively, you can start the timer via python
```python
import conferencetimer
conferencetimer.start_timer()
```
and accordingly the remote via

```python
import conferencetimer
conferencetimer.start_remote()
```

If you want to use the remote from a different computer, make sure that both computers are in the same network and that your firewall is configured accordingly.

## Remote

The remote functionality is based on a small tcp server which expects a json dictionary with *command* being one of the following:

- *startpause* (toggle between running and pause)
- *reset* (resetting the timer, if *talk* and *qna* are specified the time for the talk and the questions is set respectively)
- *adjust* (adds or subtracts time specified by *delta* from the timer)
- *fullscreen* (toggles fullscreen)

### Unix systems

You can also control the timer app via the command line with netcat:

```bash
echo '{"command": "startpause"}' | nc 127.0.0.1 5555
echo '{"command": "reset", "talk": 30, "qna": 15}' | nc 127.0.0.1 5555
```

### Windows Powershell Example

A small example script to control the timer app via the powershell:

```powershell
$payload = '{"command":"start"}'
$ip = "192.168.1.50"
$port = 5555
$client = New-Object System.Net.Sockets.TcpClient($ip, $port)
$stream = $client.GetStream()
$writer = New-Object System.IO.StreamWriter($stream)
$writer.Write($payload)
$writer.Flush()
$writer.Close()
$client.Close()
```