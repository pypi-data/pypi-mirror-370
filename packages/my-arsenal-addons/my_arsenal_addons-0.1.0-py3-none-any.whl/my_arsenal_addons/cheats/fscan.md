# fscan

% scanner, network, portscan, alive, smb, enum, vuln
#platform/windows #platform/linux #target/remote #cat/RECON #cat/FUZZ #cat/ATTACK

## default scan (TCP port scan)
```
fscan -h <target>
```

## quick scan (TCP + UDP + common ports)
```
fscan -h <target> -np -u -v
```

## SMB enumeration (find shares, users, etc.)
```
fscan -h <target> -smb
```

## Web scan (HTTP headers, titles, dirs)
```
fscan -h <target> -web
```

## Full scan (all modules)
```
fscan -h <target> -a
```

## Scan with output to file
```
fscan -h <target> -o result.txt
```
