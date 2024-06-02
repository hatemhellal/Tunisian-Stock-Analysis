import os
import pandas as pd

l=os.listdir("./raw text datasets")
l=[i for i in l if i.startswith("histo")]
def adjust(string):
    return " ".join(string.split())
def get_list(l,start,end):
    container=[]
    for i in l:
        container.append(i[start:end])
    return container
for i in l:
    with open("./raw text datasets/"+i,"r") as f:
        sentences=f.readlines()
    keys=sentences[0]
    keys=" ".join(keys.split())
    l=[o.strip() for o in sentences[2:]]
    keys = keys.split(" ")
    dic = {}
    for m in keys:
        dic[m] = 0
    lengths=[len(i)+1 for i in sentences[1].split(" ")]
    for j in range(len(keys)):
        dic[keys[j]]=get_list(l,sum(lengths[0:j]),sum(lengths[0:j+1]))
    df=pd.DataFrame.from_dict(dic)
    df.to_csv("D:/stock analysis/datasets csv/"+i[:-3]+"csv",index=False)