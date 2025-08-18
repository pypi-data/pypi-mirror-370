[![penterepTools](https://www.penterep.com/external/penterepToolsLogo.png)](https://www.penterep.com/)


## PTELASTIC

Security testing tool for identifying, fingerprinting, and exploiting vulnerabilities in Elasticsearch instances.  
The tool:
- Identifies whether or not Elasticsearch is running on a host
- Identifies whether it is running on HTTP or HTTPS
- Identifies whether or not it has authentication enabled
- Enumerates:
   - Elasticsearch version
   - Modules, their version and description
   - Installed plugins and their version
   - Users, their roles and privileges
- Tests for the following CVEs:
   - CVE-2015-5531
   - CVE-2015-1427
   - CVE-2014-3120
   - CVE-2015-3337
- Dumps:
   - Structure of indices
   - Data from indices

## Installation

```
pip install ptelastic
```

## Adding to PATH
If you're unable to invoke the script from your terminal, it's likely because it's not included in your PATH. You can resolve this issue by executing the following commands, depending on the shell you're using:

For Bash Users
```bash
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.bashrc
source ~/.bashrc
```

For ZSH Users
```bash
echo "export PATH=\"`python3 -m site --user-base`/bin:\$PATH\"" >> ~/.zshrc
source ~/.zshrc
```

## Usage examples
```
ptelastic -u htttps://www.example.com/
```

## Options
```
   -u   --url         <url>           Connect to URL
   -ts  --tests       <test>          Specify one or more tests to perform:
                       AUTH           Elasticsearch authentication test
                       HTTPS          Elasticsearch HTTP/S test
                       IS_ELASTIC     Elasticsearch availability test

   -p   --proxy       <proxy>         Set proxy (e.g. http://127.0.0.1:8080)
   -T   --timeout     <miliseconds>   Set timeout (default 10)
   -t   --threads     <threads>       Set thread count (default 10)
   -c   --cookie      <cookie>        Set cookie
   -a   --user-agent  <a>             Set User-Agent header
   -H   --headers     <header:value>  Set custom header(s)
   -r   --redirects                   Follow redirects (default False)
   -vv  --verbose                     Enable verbose mode
   -v   --version                     Show script version and exit
   -h   --help                        Show this help message and exit
   -j   --json                        Output in JSON format


```

## Dependencies
```
ptlibs
```

## License

Copyright (c) 2025 Penterep Security s.r.o.

ptelastic is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

ptelastic is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with ptelastic. If not, see https://www.gnu.org/licenses/.

## Warning

You are only allowed to run the tool against the websites which
you have been given permission to pentest. We do not accept any
responsibility for any damage/harm that this application causes to your
computer, or your network. Penterep is not responsible for any illegal
or malicious use of this code. Be Ethical!


