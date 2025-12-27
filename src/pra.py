import heapq, random, math
from collections import deque
import matplotlib.pyplot as plt, matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation

# seq - Page demand sequence, fcnt - Frame count, pfmp - Frame To Page map, ptmp - Page To Time map
class PRA:
    def update(self, frame, angles, wedges, autotexts):
        for wedge, (start_theta, end_theta), text in zip(wedges, angles, autotexts):
            currtheta1 = start_theta * math.sin(math.pi * frame / 200)
            currtheta2 = end_theta * math.sin(math.pi * frame / 200)
            wedge.set_theta1(currtheta1); wedge.set_theta2(currtheta2)
            text.set_text(f'{(currtheta2 - currtheta1) * 100 / 360:.1f}%')
        return [*wedges, *autotexts]
        # return wedges, autotexts - This is wrong as update is supposed to return a single iterable, not pair of two

    def __present(self, ans, ph, seq):
        plt.style.use('dark_background')
        fig, axd = plt.subplot_mosaic('AB', layout='constrained')

        axd['A'].set_title('Hit Fault Distribution') 
        color1 = mcolors.hsv_to_rgb((x := random.randint(0, 360) / 360, 1, 1))
        color2 = mcolors.hsv_to_rgb((1 - x, 1, 1))
        wedges, texts, autotexts = axd['A'].pie([ph, len(ans) - ph], labels=['Page Hit%', 'Page Fault%'], colors=[color1, color2], autopct='1.1%%', textprops={'fontsize':12})
        leg = axd['A'].legend(loc='upper left', ncol=2, )
        angles = [(wedge.theta1, wedge.theta2) for wedge in wedges]

        axd['B'].set_title('Hit Fault Sequence')
        table = axd['B'].table(loc='center', cellLoc='center', cellText=[[x] for x in seq], cellColours=[[('#ff0000', '#00ff00')[x]] for x in ans])

        fig.animation = FuncAnimation(fig, self.update, frames=101, fargs=(angles, wedges, autotexts), interval=8, blit=True, repeat=False) # interval is in millisecond
        return fig

    def lru(self, seq, fcnt):
        frames, pfmp, ptmp, ph = fcnt, {}, {}, 0
        heap = []; ans = []
        heapq.heapify(heap)
        for t in range(0, len(seq)):
            page = seq[t]
            if page in pfmp:
                ph += 1
                ptmp[page] = t
                ans.append(True)
            elif frames > 0:
                pfmp[page], ptmp[page] = frames, t
                frames -= 1
                ans.append(False)
            else:
                while heap and ptmp[heap[0][1]] > heap[0][0]:
                    heapq.heappop(heap)
                tm, lpage = heapq.heappop(heap)
                ptmp[page] = t; page != lpage and ptmp.pop(lpage)
                pfmp[page] = pfmp[lpage]; page != lpage and pfmp.pop(lpage)
                ans.append(False)
            heapq.heappush(heap, (t, page))
        fig = self.__present(ans, ph)
        return fig, ans, ph, len(ans) - ph
    
    def fifo(self, seq, fcnt):
        q = deque([]); pageset = set()
        ans = []; ph = 0
        for page in seq:
            if page in pageset:
                ans.append(True)
                ph += 1
            else:
                ans.append(False)
                if len(q) == fcnt:
                    lpage = q.popleft()
                    pageset.remove(lpage)
                q.append(page); pageset.add(page)
        fig = self.__present(ans, ph, seq)
        return fig, ans, ph, len(ans) - ph


    


        
        

