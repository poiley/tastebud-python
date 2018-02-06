'''
format old values in csv file when new columns are added. This will need some
customization depending on the implementation but is good for temporary use.
'''

fin = open("data.csv", "r") #open file to read data
lines = fin.read().splitlines() #get data, store
fin.close() #close file

fout = open("data.csv", "w") #reopen in different mode

for line in lines:
    line_data = line.split(",")
    strbuild = ""

    if len(line_data) == 8:

        for i in line_data:
            strbuild += (i + ",")

        print(strbuild)
        fout.write(strbuild+"\n")
    elif len(line_data) == 8:
        fout.write(line+"\n")

fout.close()
