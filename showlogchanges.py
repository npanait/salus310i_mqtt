
import argparse

# Create the parser
parser = argparse.ArgumentParser()
# Add  argument/arguments
parser.add_argument('--logFile', type=str, help='Optionally provide the file path to be parsed. Defaul log is app.log')
parser.add_argument('--filterLines', type=str, help='Optionally provide the filter for change. Defaul is Gaz')

# Parse the argument/arguments
args = parser.parse_args()

if args.logFile :
    logfile = args.logFile
else:
    logfile = 'app.log'
    

if  args.filterLines :
    filterLines = args.filterLines
else:
    filterLines = 'Gaz'
    

oldline_status=""
c=0
with open(logfile) as fp:
    Lines = fp.readlines()
    for line in Lines:
        if filterLines in line:
            line_status = line.split(" - ")[1].strip()
            if line_status != oldline_status:
                
                print(line)
                oldline_status = line_status
        
