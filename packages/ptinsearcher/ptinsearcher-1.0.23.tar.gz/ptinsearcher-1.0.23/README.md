[![penterepTools](https://www.penterep.com/external/penterepToolsLogo.png)](https://www.penterep.com/)


# PTINSEARCHER - Web/File Information Extractor
 ptinsearcher is a tool designed to extract information from sources such as URLs and files. It can retrieve HTML comments, email addresses, phone numbers, IP addresses, subdomains, HTML forms, links, and document metadata.

## Installation
```
pip install ptinsearcher
```

```
sudo apt-get install libmagic1
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
   ptinsearcher -u https://www.example.com/
   ptinsearcher -u https://www.example.com/ --extract E        # Extract emails
   ptinsearcher -u https://www.example.com/ --extract UQX      # Extract internal URLs, internal URLs w/ parameters, external URLs
   ptinsearcher -f url_list.txt --grouping
   ptinsearcher -f url_list.txt --grouping-complete
   ptinsearcher -f url_list.txt
   ptinsearcher -u image.jpg -e M
   ptinsearcher -u images/*.jpg -e M
```

## Options
```
   -u   --url                 <url>           Test URL or File
   -f   --file                <file>          Load list of URLs from file
   -d   --domain              <domain>        Domain - merge domain with filepath. Use when wordlist contains filepaths (e.g. /index.php)
   -e   --extract             <extract>       Specify data to extract:
                                 A              All (extracts everything - default option)
                                 E              Emails
                                 S              Subdomains
                                 C              Comments
                                 F              Forms
                                 I              IP addresses
                                 P              Phone numbers
                                 U              Internal urls
                                 Q              Internal urls with parameters
                                 X              External urls
                                 N              Insecure urls
                                 M              Metadata

   -ey  --extension-yes       <extensions>    Process only URLs from <list> that end with <extension-yes>
   -en  --extension-no        <extensions>    Process only URLs from <list> that do not end with <extension-no>
   -g   --grouping                            Group findings from multiple sources into one table
   -gc  --grouping-complete                   Group and merge findings from multiple sources into one result
   -gp  --group-parameters                    Group URL parameters
   -wp  --without-parameters                  Without URL parameters
   -op  --output-parts                        Save each extract-type to separate file
   -o   --output              <output>        Save output to file
   -p   --proxy               <proxy>         Set proxy (e.g. http://127.0.0.1:8080)
   -T   --timeout             <timeout>       Set timeout
   -c   --cookie              <cookie=value>  Set cookie
   -a   --user-agent          <user-agent>    Set User-Agent
   -t   --threads             <threads>       Set Threads
   -H   --headers             <header:value>  Set custom header(s)
   -r   --redirects                           Follow redirects (default False)
   -C   --cache                               Cache requests (load from tmp in future)
   -v   --version                             Show script version and exit
   -h   --help                                Show this help message and exit
   -j   --json                                Output in JSON format

```

## Dependencies
We use [ExifTool](https://exiftool.org/) to extract metadata.
```
ptlibs
bs4
lxml
pyexiftool
validators
python-magic
```

## License

Copyright (c) 2025 Penterep Security s.r.o.

ptinsearcher is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ptinsearcher is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ptinsearcher.  If not, see <https://www.gnu.org/licenses/>.

## Warning

You are only allowed to run the tool against the websites which
you have been given permission to pentest. We do not accept any
responsibility for any damage/harm that this application causes to your
computer, or your network. Penterep is not responsible for any illegal
or malicious use of this code. Be Ethical!
