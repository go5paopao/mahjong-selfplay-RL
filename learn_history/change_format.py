import sys
import os
import csv

"""learn_log.txtフォーマットが微妙なので直す"""

file_path = sys.argv[1]
f = open(file_path,"r")
reader = csv.reader(f)
header = next(reader)
w = open(file_path + ".r1.csv","w")
writer = csv.writer(w)
header_row = ["episode","stage","miss","agari","draw","tenpai","average_value","average_entropy"]
writer.writerow(header_row)
stage = 0
for row in reader:
    out_row = []
    #episode
    out_row.append(row[1])
    #stage
    out_row.append(stage)
    #miss
    out_row.append(row[3])
    #agari
    out_row.append(row[5])
    #draw
    out_row.append(row[7])
    #tenpai
    out_row.append(row[9])
    #average_value
    out_row.append(row[12].strip(")"))           
    #average_entropy
    out_row.append(row[14].strip(")]"))
    #update stage
    miss = int(row[3])
    agari = int(row[5])
    draw = int(row[7])
    win_rate = float(agari)/(agari+miss+draw)
    if stage < 4:
        if win_rate > 0.9:
            stage += 1
    elif stage == 4:
        if win_rate > 0.7:
            stage += 1
    elif stage == 5:
        if win_rate > 0.6:
            stage += 1
    writer.writerow(out_row)

f.close()

