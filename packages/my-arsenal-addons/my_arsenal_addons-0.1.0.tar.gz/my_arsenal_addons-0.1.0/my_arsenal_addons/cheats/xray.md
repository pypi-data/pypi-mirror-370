# xray

% proxy, scanner, pentest, 网络安全工具, 内网穿透
#platform/linux #platform/windows #target/remote #cat/NETWORK #cat/WEB #cat/PENTEST

## Port Forward
```
xray reverse --local-addr <local_ip>:<local_port> --remote-addr <public_ip>:<public_port>
```

## Local proxy forwarding
```
xray proxy --listen <listen_ip>:<listen_port> --mode tcp
```

## TLS intercept
```
xray tls --listen <listen_ip>:443 --cert <cert_file>.pem --key <key_file>.pem
```

## Network Scan
```
xray network --scan-type tcp --target <target_host>
```

## webscan crawler
```
xray webscan --basic-crawler <target_url> --html-output result.html
```

## inner service expose
```
xray reverse --local-addr <local_ip>:<local_port> --remote-addr <remote_ip>:<remote_port>
```

## proxy debug
```
xray proxy --listen <local_ip>:<local_port> --mode tcp
```
