import sys
import re
import json
import datetime
import dateutil.parser

def main():
    line = sys.stdin.readline()
    while line:
        line = line.strip()
        if match := re.search("##ENOLOGMESSAGE .*", line):
            _, loginfo_json = match.group(0).split(" ", 1)
            loginfo = json.loads(loginfo_json)
            date = dateutil.parser.isoparse(loginfo["timestamp"])
            prefix = date.strftime("%T:%f")
            print(prefix,":", loginfo["message"])
        else:
            print(">> " + line)
        line = sys.stdin.readline()

if __name__ == "__main__":
    main()
