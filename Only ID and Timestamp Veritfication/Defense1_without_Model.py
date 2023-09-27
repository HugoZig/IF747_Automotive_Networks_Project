ids = {    #[dp, media, flag, timeStamp]
    112:[0.00021763819850441595,0.005019260990539788,0,0],
    223:[0.00025132419387750144,0.010019240120615775,0,0],
    330:[0.0002505963260446601,0.015020771353794907,0,0],
    360:[0.00025316818081237415,0.01502077325719724,0,0],
    450:[0.0002809399738319124,0.020022250237868695,0,0]
}

def check_timestamp(timestamp, dp, mean):
    if (mean+3*dp) >= timestamp and (mean-3*dp) <= timestamp:
        return True
    else:
        return False

def main():

    try:
        file = open('/home/marcela/Downloads/atk3-it1.txt')
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
