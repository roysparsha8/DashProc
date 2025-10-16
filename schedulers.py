# proclist is list of tuples (process_name, arrival_time, burst_time)
# tat stands for Turn Around Time
# wt stands for Waiting Time
# fifo - First Come First Serve Scheduler
# sjf - Shortest job First Scheduler
# srtf - Shortest Remaining Time First Scheduler
# hrrf - Highest Response Ratio First Scheduler
# rr - Round Robin Scheduler
# prio - Preemptive Priority Scheduler
# cpi - Current Process Index
# ts - Time Slice, tm - Time
# pdl - Priority Distribution List, p - Current Process's Priority, ariv - Current Process's arrival time, brst - Current Process Burst Time 


# FIX - SRTF logic
import heapq, random
from collections import deque
import matplotlib as mlp
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

mlp.rcParams['toolbar'] = 'None'

class Scheduler:
    def __init__(self, proclist):
        self.proclist = proclist

    def __present(self, title):
        intervals = self.data[0].copy()
        wt = self.data[1].copy()
        tat = self.data[2].copy()
        rt = self.data[3].copy()
        tp = self.data[4]; cu = self.data[5]; csc = self.data[6]
        wt.sort(key=lambda x : x[0])
        tat.sort(key=lambda x : x[0])
        cell_text = []; total_wt = 0; total_tat = 0; total_rt = 0
        for i in range(0, len(wt)):
            cell_text.append([wt[i][0], wt[i][1], tat[i][1], rt[i][1]])
            total_wt += wt[i][1]
            total_tat += tat[i][1]
            total_rt += rt[i][1]
        cell_text.append(['Average', total_wt / len(wt), total_tat / len(tat), total_rt / len(rt)])
        plt.style.use('dark_background')
        fig, axesDict = plt.subplot_mosaic('AB\nCD', layout='constrained')
        fig.canvas.manager.set_window_title(title=title)
        ax1 = axesDict['A']
        ax2 = axesDict['B']
        ax3 = axesDict['C']
        ax4 = axesDict['D']
        colors = dict()
        for interval in intervals:
            if interval[0] not in colors:
                colors[interval[0]] = tuple(mcolors.hsv_to_rgb((random.randint(0, 361)/ 360, 0.8, 1)))
            ax1.barh([interval[0]], [interval[2] - interval[1]], left=[interval[1]], color=[colors[interval[0]]], height=[0.2])
        ax1.set_xlabel('Time -->')
        ax1.set_ylabel('Processes')
        ax1.set_title('Time Allotment', y=1.1)

        line1x, line2x, line3x = [[0, 1.6 * len(tat) - 0.4]] * 3
        line1y, line2y, line3y = [[total_wt / len(wt)] * 2, [total_tat / len(tat)] * 2, [total_rt / len(rt)] * 2]
        ax2.bar(x=[(1.6 * i) for i in range(0, len(wt))],
                height=[x[1] for x in wt], width=[0.4] * len(wt), align='edge', 
                color=['seagreen'] * len(wt), label='Waiting Time')
        ax2.bar(x=[(0.6 + 1.6 * i) for i in range(0, len(tat))],
                height=[x[1] for x in tat], width=[0.4] * len(tat), align='center',
                color=['yellow'] * len(tat), label='TurnAround Time')
        ax2.bar(x=[0.8 + 1.6 * i for i in range(0, len(rt))], 
                height=[x[1] for x in rt], width=[0.4] * len(rt), align='edge',
                color=['blue'] * len(rt), label='Response Time')
        ax2.plot(line1x, line1y, color='green', linestyle='-', linewidth=1, label='AvgWait')
        ax2.plot(line2x, line2y, color='white', linestyle='--', linewidth=1, label='AvgTat')
        ax2.plot(line3x, line3y, color='skyblue', linestyle=':', linewidth=1, label='AvgResp')
        ax2.set_xticks(ticks=[(0.6 + 1.6 * i) for i in range(0, len(wt))], labels=[x[0] for x in wt])
        ax2.set_xlabel('Process -->')
        ax2.set_ylabel('Wait / Turnaround Time / Response Time')
        ax2.set_title('Waiting time, TurnAround time, Response Time', y=1.1)
        ax2.legend(loc='upper left', ncol=2)

        columns = ['Name', 'Wait Time', 'TurnAround Time', 'Response Time']
        ax3.axis(False); ax3.axis('tight')
        table = ax3.table(colLabels=columns, cellText=cell_text, loc='center', cellLoc='center', cellColours=[['#000000'] * 4] * len(cell_text), colColours=['blue'] * 4)
        for cell in table.get_celld().values():
            cell.set_edgecolor('white')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        ax3.set_title('Process Information', y=-0.1)

        ax4.bar(x=[1,2,3], height=[tp*100,cu,csc], width=[0.4] * 3, tick_label=['ThroughPut X 100','CPU Utilization%','Context Swicth Count'],
                align='center', color=['skyblue','violet','green'])
        ax4.set_title("CPU reports", y=-0.3)
        return fig

    def fifo(self):
        if len(self.proclist) == 0:
            return ([],[],[],[],0.0,0.0,0)
        proclist = self.proclist.copy()      
        wt = []; tat = []; intervals = []
        proclist.sort(key = lambda x : x[1])
        tm = 0
        for proctup in proclist:
            tm = max(tm, proctup[1])
            intervals.append((proctup[0], tm, tm + proctup[2]))
            wt.append((proctup[0], tm - proctup[1]))
            tm += proctup[2]
            tat.append((proctup[0], tm - proctup[1]))
        tott = max(intervals, key=lambda x : x[2])[2] - min(intervals, key=lambda x : x[1])[1]
        cut = sum([(x[2] - x[1]) for x in intervals])
        self.data = (intervals, wt, tat, wt, len(proclist) / tott, (cut * 100) / tott, 0)
        fig = self.__present("First Come First Serve")
        return (fig, self.data)
    
    def sjf(self):
        if len(self.proclist) == 0:
            return ([],[],[],[],0.0,0.0,0)
        proclist = self.proclist.copy()
        wt = []; tat = []; intervals = []
        proclist.sort(key = lambda x : (x[1], x[2]))
        tm = proclist[0][1]; i = 0
        heap = []
        heapq.heapify(heap)
        while True:
            while i < len(proclist) and proclist[i][1] <= tm:
                heapq.heappush(heap, (proclist[i][2], proclist[i][1], proclist[i][0]))
                i += 1
            if len(heap) == 0:
                break
            else:
                burst, arrive, name = heapq.heappop(heap)
                intervals.append((name, tm, tm + burst))
                tat.append((name, tm + burst - arrive))
                wt.append((name, tm - arrive))
                tm += burst
        tott = max(intervals, key=lambda x : x[2])[2] - min(intervals, key=lambda x : x[1])[1]
        cut = sum([(x[2] - x[1]) for x in intervals])
        self.data = (intervals, wt, tat, wt, len(proclist) / tott, (cut * 100) / tott, 0)
        fig = self.__present("Shortest Job First")
        return (fig, self.data)

    def srtf(self):
        if len(self.proclist) == 0:
            return ([],[],[],[],0.0,0.0,0)
        proclist = self.proclist.copy()
        proclist.sort(key=lambda x : (x[1], x[2]))
        heap = []; heapq.heapify(heap); intervals = []; tat = {}; rt = {}
        i = 0; tm = 0
        while True:
            while i < len(proclist) and tm >= proclist[i][1]:
                heapq.heappush(heap, (proclist[i][2], proclist[i][1], proclist[i][0]))
                i += 1
            if len(heap) == 0:
                if i < len(proclist):
                    tm = proclist[i][1]
                    heapq.heappush(heap, (proclist[i][2], proclist[i][1], proclist[i][0]))
                    i += 1
                else:
                    break
            curr_burst, curr_arrive, name = heapq.heappop(heap)
            if len(intervals) > 0 and intervals[-1][0] == name:
                intervals[-1] = (intervals[-1][0], intervals[-1][1], tm + 1)
            else:
                intervals.append((name, tm, tm + 1))
            if name not in rt:
                rt[name] = tm - curr_arrive
            tat[name] = tm + 1
            tm += 1
            if curr_burst > 1:
                heapq.heappush(heap, (curr_burst - 1, curr_arrive, name))
        wt = []
        for nm, arrivetm, bursttm in proclist:
            tat[nm] -= arrivetm
            wt.append((nm, tat[nm] - bursttm))
        tott = max(intervals, key=lambda x : x[2])[2] - min(intervals, key=lambda x : x[1])[1]
        cut = sum([(x[2] - x[1]) for x in intervals])
        self.data = (intervals, wt, list(tat.items()), list(rt.items()), len(proclist) / tott, (cut * 100) / tott, len(intervals) - 1)
        fig = self.__present('Shortest Remaining Time First')
        return (fig, self.data)        


    def hrrf(self): # cpi stands for Current Process Index
        if len(self.proclist) == 0:
            return ([],[],[],[],0.0,0.0,0)
        proclist = self.proclist.copy()
        intervals = []; tat = []; wt = []
        proclist.sort(key = lambda x : x[1])
        visit = set(range(0, len(proclist))); tm = proclist[0][1]
        while len(visit) > 0:
            cpi = max(visit, key = lambda x : (tm - proclist[x][1] + proclist[x][2]) / proclist[x][2])
            visit.remove(cpi)
            intervals.append((proclist[cpi][0], tm, tm + proclist[cpi][2]))
            wt.append((proclist[cpi][0], tm - proclist[cpi][1]))
            tm = proclist[cpi][2] + max(proclist[cpi][1], tm)
            tat.append((proclist[cpi][0], tm - proclist[cpi][1]))
        tott = max(intervals, key=lambda x : x[2])[2] - min(intervals, key=lambda x : x[1])[1]
        cut = sum([(x[2] - x[1]) for x in intervals])
        self.data = (intervals, wt, tat, wt, len(proclist) / tott, (cut * 100) / tott, 0)
        fig = self.__present("Highest Response Ratio First")
        return (fig, self.data)
    
    def rr(self, ts): # ts means time slice, tm for time
        if len(self.proclist) == 0:
            return ([],[],[],[],0.0,0.0,0)
        proclist = self.proclist.copy()
        intervals = []; tat = {}; wt = []; rt = {}
        proclist.sort(key = lambda x : x[1]); tm = 0; contextsw = 0
        q = deque(proclist)
        while len(q) > 0:
            tm = max(tm, q[0][1])
            if q[0][0] not in rt:
                rt[q[0][0]] = tm
            if ts >= q[0][2]:
                if len(intervals) > 0 and intervals[-1][0] == q[0][0] and intervals[-1][2] == tm:
                    intervals[len(intervals) - 1] = (intervals[-1][0], intervals[-1][1], tm + q[0][2])
                else:
                    intervals.append((q[0][0], tm, tm + q[0][2]))
                tm += q[0][2]
                tat[q[0][0]] = tm
                q.popleft()
            else:
                if len(intervals) > 0 and intervals[len(intervals) - 1][0] == q[0][0] and intervals[-1][2] == tm:
                    intervals[len(intervals) - 1][2] = tm + ts
                else:
                    intervals.append((q[0][0], tm, tm + ts))
                tm += ts
                tat[q[0][0]] = tm
                temp = q.popleft()
                q.append((temp[0], temp[1], temp[2] - ts))
        for x in proclist:
            rt[x[0]] -= x[1]
            tat[x[0]] -= x[1]
            wt.append((x[0], tat[x[0]] - x[2]))
        tott = max(intervals, key=lambda x : x[2])[2] - min(intervals, key=lambda x : x[1])[1]
        cut = sum([(x[2] - x[1]) for x in intervals])
        contextswtrack = {x[0] : x[2] for x in proclist}
        for x in intervals:
            if contextswtrack[x[0]] > x[2] - x[1]:
                contextsw += 1
                contextswtrack[x[0]] -= x[2] - x[1]
        self.data = (intervals, wt, list(tat.items()), list(rt.items()), len(proclist) / tott, (cut * 100) / tott, contextsw)
        fig = self.__present("Round Robin")
        return (fig, self.data)
    
    def prio_preemptive(self, pdl):
        if len(self.proclist) == 0 or len(self.proclist) != len(pdl):
            return ([],[],[],[],0.0,0.0,0)
        proclist = self.proclist.copy()
        temp = []
        for i in range(0, len(pdl)):
            temp.append((proclist[i][1], proclist[i][2], i))
        temp.sort(reverse=False)
        heap = []; intervals = []; tat = {}; wt = []; rt = {}; contextsw = 0
        i = 0
        heapq.heapify(heap); tm = temp[0][0]
        while True:
            if i == len(temp) and len(heap) == 0:
                break
            if i < len(temp):
                tm = max(tm, temp[i][0])
            while i < len(temp) and temp[i][0] <= tm:
                heapq.heappush(heap, (pdl[temp[i][2]], temp[i][0], temp[i][1], i))
                i += 1
            (p, ariv, brst, id) = heapq.heappop(heap)
            if proclist[id][0] not in rt:
                rt[proclist[id][0]] = tm
            if len(intervals) == 0 or intervals[len(intervals) - 1][0] != proclist[id][0]:
                intervals.append((proclist[id][0], tm, tm + 1))
            else:
                intervals[-1] = (intervals[-1][0], intervals[-1][1], tm + 1)
            tat[proclist[id][0]] = tm + 1
            if brst > 1:
                heapq.heappush(heap, (p + 1, ariv, brst - 1, id))
            tm += 1
        for x in proclist:
            rt[x[0]] -= x[1]
            tat[x[0]] -= x[1]
            wt.append((x[0], tat[x[0]] - x[2]))
        tott = max(intervals, key=lambda x : x[2])[2] - min(intervals, key=lambda x : x[1])[1]
        cut = sum([(x[2] - x[1]) for x in intervals])
        contextswtrack = {x[0] : x[2] for x in proclist}
        for x in intervals:
            if contextswtrack[x[0]] > x[2] - x[1]:
                contextsw += 1
                contextswtrack[x[0]] -= x[2] - x[1]
        self.data = (intervals, wt, list(tat.items()), list(rt.items()), len(proclist) / tott, (cut * 100) / tott, contextsw)
        fig = self.__present("Priority Preemptive")
        return (fig, self.data)
    
    def prio_no_preemptive(self, pdl):
        if len(self.proclist) == 0:
            return ([],[],[],[],0.0,0.0,0)
        temp = [(x[1], pdl[i], x[2], i) for i, x in enumerate(self.proclist)]
        temp.sort(reverse=False)
        tm = 0; i = 1
        heap = [(temp[0][1], temp[0][0], temp[0][2], temp[0][3])]; intervals = []; tat = []; wt = []
        heapq.heapify(heap)
        cnt = 0
        while True:
            if len(heap) > 0:
                currp = heapq.heappop(heap)
                tm = max(tm, currp[1])
                intervals.append((self.proclist[currp[3]][0], tm, tm + currp[2]))
                tat.append((self.proclist[currp[3]][0], tm + currp[2] - currp[1]))
                wt.append((self.proclist[currp[3]][0], tm - currp[1]))
                tm += currp[2]
            elif i < len(temp):
                tm = temp[i][0]
            else:
                break
            while i < len(temp) and tm >= temp[i][0]:
                heapq.heappush(heap, (temp[i][1], temp[i][0], temp[i][2], temp[i][3]))
                i += 1
        tott = max(intervals, key=lambda x : x[2])[2] - min(intervals, key=lambda x : x[1])[1]
        cut = sum([(x[2] - x[1]) for x in intervals])
        self.data = (intervals, wt, tat, wt, len(self.proclist) / tott, (cut * 100) / tott, 0)
        fig = self.__present("Priority No Preemptive")
        return (fig, self.data)
    
    def __mlq_fifo(self, systemq, tm, limit, intervals, tat, rt):
        while len(systemq) > 0:
            currp = systemq.popleft()
            if max(tm, currp[0]) >= limit:
                systemq.appendleft(currp)
                tm = limit
                break
            else:
                tm = max(tm, currp[0])
                ftm = min(limit, tm + currp[1])
                if ftm < tm + currp[1]:
                    systemq.appendleft((ftm, currp[1] - ftm + tm, currp[2]))
                if currp[2] not in rt:
                    rt[currp[2]] = tm
                if len(intervals) > 0 and intervals[-1][0] == currp[2] and intervals[-1][2] == tm:
                    intervals[-1] = (intervals[-1][0], intervals[-1][1], ftm)
                else:
                    intervals.append((currp[2], tm, ftm))
                tat[currp[2]] = ftm
                tm = ftm
        return (systemq, tm, intervals, tat, rt)
    
    def __mlq_rr(self, userq, tm, limit, intervals, tat, ts, rt):
        while len(userq) > 0:
            currp = userq.popleft()
            if max(tm, currp[0]) >= limit:
                userq.appendleft(currp)
                tm = limit
                break
            else:
                tm = max(tm, currp[0])
                ftm = min(tm + min(currp[1], ts), limit)
                if ftm < tm + min(currp[1], ts):
                    userq.appendleft((ftm, currp[1] - ftm + tm, currp[2]))
                    if currp[2] not in rt:
                        rt[currp[2]] = tm
                    if len(intervals) > 0 and intervals[-1][0] == currp[2] and intervals[-1][2] == tm:
                        intervals[-1] = (intervals[-1][0], intervals[-1][1], ftm)
                    else:
                        intervals.append((currp[2], tm, ftm))
                    tat[currp[2]] = ftm
                else:
                    if ftm < tm + currp[1]:
                        userq.append((ftm, currp[1] - ftm + tm, currp[2]))
                    if currp[2] not in rt:
                        rt[currp[2]] = tm
                    if len(intervals) > 0 and intervals[-1][0] == currp[2] and intervals[-1][2] == tm:
                        intervals[-1] = (intervals[-1][0], intervals[-1][1], ftm)
                    else:
                        intervals.append((currp[2], tm, ftm))
                    tat[currp[2]] = ftm
                tm = ftm
        return (userq, tm, intervals, tat, rt)

    def mlq(self, pdl, qts, ts):
        if len(self.proclist) == 0:
            return ([],[],[],[],0.0,0.0,0)
        systemlist = [(x[1],x[2],x[0]) for i, x in enumerate(self.proclist) if pdl[i] % 2 == 1]
        userlist = [(x[1],x[2],x[0]) for i, x in enumerate(self.proclist) if pdl[i] % 2 == 0]
        systemlist.sort(key=lambda x : x[0]); userlist.sort(key=lambda x : x[0])
        systemq = deque(systemlist); userq = deque(userlist); tm = 0; i = 0; contextsw = 0
        intervals = []; wt = []; tat = {}; rt = {}
        while True:
            limit = tm + qts
            if i % 2 == 0:
                if len(systemq) > 0:
                    systemq, tm, intervals, tat, rt = self.__mlq_fifo(systemq, tm, limit, intervals, tat, rt)
                elif len(userq) > 0:
                    userq, tm, intervals, tat, rt = self.__mlq_rr(userq, tm, limit, intervals, tat, ts, rt)
                else:
                    break
            else:
                if len(userq) > 0:
                    userq, tm, intervals, tat, rt = self.__mlq_rr(userq, tm, limit, intervals, tat, ts, rt)
                elif len(systemq) > 0:
                    systemq, tm, intervals, tat, rt = self.__mlq_fifo(systemq, tm, limit, intervals, tat, rt)
                else:
                    break
            i += 1
        for x in self.proclist:
            rt[x[0]] -= x[1]
            tat[x[0]] -= x[1]
            wt.append((x[0], tat[x[0]] - x[2]))
        contextswtrack = {x[0] : x[2] for x in self.proclist}
        for x in intervals:
            if contextswtrack[x[0]] > x[2] - x[1]:
                contextsw += 1
                contextswtrack[x[0]] -= x[2] - x[1]
        tott = max(intervals, key=lambda x : x[2])[2] - min(intervals, key=lambda x : x[1])[1]
        cut = sum([(x[2] - x[1]) for x in intervals])
        self.data = (intervals, wt, list(tat.items()), list(rt.items()), len(self.proclist) / tott, (cut * 100) / tott, contextsw)
        fig = self.__present("Multilevel Queue")
        return (fig, self.data)
    


    


        
        




        


        





