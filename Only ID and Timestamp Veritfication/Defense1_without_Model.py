import threading as th  
import statistics as stats


ids = {    #[dp, media, flag, timeStamp]
    112:[0.0025143939369990788,0.002509530744465201,0,0],
    223:[0.005012969315368336,0.0050092225660557,0,0],
    330:[0.007512921815145051,0.007509492327822053,0,0],
    360:[0.00751296586894381,0.007509493279410016,0,0],
    450:[0.010013888753237452,0.010009537815126049,0,0]
}

def check_timestamp(timestamp, dp, mean):
    if (mean+3*dp) >= timestamp and (mean-3*dp) <= timestamp:
        return True
    else:
        return False

def main():

    try:
        file = open('/home/marcela/Downloads/atk1_it3.txt')
    except:
        print('erro')
    else:
        count1=0
        count2=0
        file_r = file.readlines()

        for i in file_r:
            id = i.split(' can0 ')
            id = id[1].split('#')
            id = int(id[0])

            ts = i.split(')')
            ts = ts[0].strip('(')
            ts = float(ts)
             

            if(id not in ids.keys()):
                count1+=1

            else:
                data = ids.get(id)
                print(f'TS:{ts-data[3]}')
                if(data[3]!=0 and check_timestamp(ts-data[3], data[0], data[1])==False):
                    count2 += 1
                     

                data[3] = ts
                ids.update({id:data})
                
        print(count1,count2)
        file.close()
if __name__=='__main__':
    main()
