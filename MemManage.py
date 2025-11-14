def mft(memsize, partsize, processes):
    numpart = memsize // partsize
    ans = [], memused = 0
    for proc in processes:
        if numpart > 0 and proc[1] <= partsize:
            ans.append((proc[0],proc[1],partsize - proc[1]))
            numpart -= 1
        else:
            ans.append((proc[0],0,-1))
        memused += ans[-1][1]
    return ans, memused

def mvt(memsize, processes):
    ans = []; memused = 0
    for proc in processes:
        if proc[1] + memused <= memsize:
            ans.append((proc[0], proc[1]))
        else:
            ans.append((proc[0], 0))
        memused += ans[-1][1]
    return ans, memused
            
if __name__ == '__main__':
    processes = [('Process 1',90),('Process 2',20),('Process 3',50),('Process 4',70),('Process 5',40)]
    ans = mft(500,100,processes)
    for i, tup in enumerate(ans):
        print(f'Partition {i + 1}: Process \'{tup[0]}\', Internal Fragmentation {tup[1]}')
