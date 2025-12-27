from tkinter import *
from tkinter import filedialog, messagebox, ttk
from schedulers import Scheduler
from banker import banker
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
from pra import PRA
import csv, json, math

# iwc = Initial Window Configuration = (width, height, x_topleft, y_topleft, name, background_color)
class App(Tk):
    def customize_button(self, button, tp):
        button.bind('<Enter>', lambda e: e.widget.configure(background=('#116bfc', '#37c20d')[tp == 2]))
        button.bind('<Leave>', lambda e: e.widget.configure(background=('#bcbbbc', '#A5A5A5')[tp == 2]))
        button.bind('<ButtonPress-1>', lambda e: e.widget.configure(background=('#063684', '#227d07')[tp == 2]))
        button.bind('<ButtonRelease-1>', lambda e: e.widget.configure(background=('#116bfc', '#37c20d')[tp == 2]))

    def __init__(self):
        super().__init__()
        self.nbdesign = {
            'relief': 'flat',
            'border': 0,
            'highlightthickness': 0,
            'font': ('Ubuntu Mono', 12)
        }
        self.nb_background = lambda tp : { 'background' : ('#bcbbbc','#A5A5A5')[tp == 2], 'activebackground' : ('#063684','#227d07')[tp == 2] }
        # NOTE - ttk.Label and ttk.Entry fonts can be changed using font=('family', size) method inside function call and ttk.Button can't be.
        # To change ttk.Button font, we need to use ttk.Style()
        self.ttk_button_style = ttk.Style(self)
        self.ttk_button_style.configure('Custom.TButton', font=('Ubuntu Mono', 15))

        self.iwc = (1000, 600, 100, 50, 'DashProc', '#ffffff')
        self.default_font = ('Ubuntu Mono', 15)
        self.title(self.iwc[4])
        self.geometry(f'{self.iwc[0]}x{self.iwc[1]}+{self.iwc[2]}+{self.iwc[3]}') # Sets witdh=1000, height=600, x_topleft=100, y_topleft=50 of main window

        dirname = Path(__file__).resolve().parent
        self.iconbitmap(f'{dirname}/assets/icon.ico')
        
        self.configure(background=self.iwc[5])
        
        self.navbar2 = Frame(self, background="#272626")
        self.navbar2.place(relx=0, rely=0, relwidth=0.08, relheight=1)
        self.navbar2_content = Frame(self, background='#ffffff')
        self.navbar2_content.place(relx=0.08, rely=0, relwidth=0.92, relheight=1)

        self.navbar2_tab1 = Button(self.navbar2, text='Scheduler', **self.nbdesign, **self.nb_background(2), command=self.scheduler)
        self.customize_button(self.navbar2_tab1, 2)
        self.navbar2_tab1.place(relx=0, rely=0, relwidth=1, relheight=0.08 * (self.iwc[0] / self.iwc[1]))
        self.tsvalue = IntVar(value=1); self.qtsvalue = IntVar(value=1) # Auto synchronized variable
        self.pdlstr = StringVar(value=''); self.csv_filename = StringVar(value='')

        self.navbar2_tab2 = Button(self.navbar2, text='Banker', **self.nbdesign, **self.nb_background(2), command=self.deadlock_prevent)
        self.customize_button(self.navbar2_tab2, 2)
        self.navbar2_tab2.place(relx=0, rely=0.08 * (self.iwc[0] / self.iwc[1]), relwidth=1, relheight=0.08 * (self.iwc[0] / self.iwc[1]))
        self.json_filename = StringVar(value='') # Auto synchronized variable

        self.navbar2_tab3 = Button(self.navbar2, text='PRA', **self.nbdesign, **self.nb_background(2), command=self.page_replacement)
        self.customize_button(self.navbar2_tab3, 2)
        self.navbar2_tab3.place(relx=0, rely=0.16 * (self.iwc[0] / self.iwc[1]), relwidth=1, relheight=0.08 * (self.iwc[0] / self.iwc[1]))
        self.seq_str = StringVar(value='') # Auto synchronized variable
        self.frame_count = IntVar(value=1)

        self.scheduler()

    def clear_navbar2_content(self):
        for wg in self.navbar2_content.winfo_children():
            wg.destroy()

    def scheduler(self):
        self.clear_navbar2_content()
        self.navbar1 = Frame(self.navbar2_content, background='#777575')
        self.navbar1.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        self.content = Frame(self.navbar2_content, background='#ffffff')
        self.content.place(relx=0, rely=0.05, relwidth=1, relheight=0.95)

        button_list = ['file','fifo','sjf','srtf','hrrf','rr','pp','pnp','mlq']
        self.button_handle = dict()
        for id, button_name in enumerate(button_list):
            self.button_handle[button_name] = Button(self.navbar1, text=button_name, **self.nbdesign, **self.nb_background(1), command=getattr(self, button_name+'_render'))
            self.customize_button(self.button_handle[button_name], 1)
            self.button_handle[button_name].place(relx=id / len(button_list), rely=0, relwidth=1 / len(button_list), relheight=1)
        self.file_render()

    def deadlock_prevent(self):
        self.clear_navbar2_content()
        self.navbar1 = Frame(self.navbar2_content, background='#777575')
        self.navbar1.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        self.content = Frame(self.navbar2_content, background='#ffffff')
        self.content.place(relx=0, rely=0.05, relwidth=1, relheight=0.95)
        self.banker_file_button = Button(self.navbar1, text='file', **self.nbdesign, **self.nb_background(1), command=self.file_page_banker)
        self.customize_button(self.banker_file_button, 1)
        self.banker_file_button.place(relx=0, rely=0, relwidth=0.5, relheight=1)
        self.banker_img_button = Button(self.navbar1, text='Output', **self.nbdesign, **self.nb_background(1), command=self.image_render)
        self.customize_button(self.banker_img_button, 1)
        self.banker_img_button.place(relx=0.5, rely=0, relwidth=0.5, relheight=1)
        self.file_page_banker()
    
    def page_replacement(self):
        self.clear_navbar2_content()
        self.pra_instance = PRA()
        self.navbar1 = Frame(self.navbar2_content, background='#777575')
        self.navbar1.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        self.content = Frame(self.navbar2_content, background='#ffffff')
        self.content.place(relx=0, rely=0.05, relwidth=1, relheight=0.95)
        button_list = ['data','fifo','lru']
        self.button_handle = dict()
        for id, button_name in enumerate(button_list):
            self.button_handle[button_name] = Button(self.navbar1, text=button_name, **self.nbdesign, **self.nb_background(1), command=getattr(self, 'pra_'+button_name+'_render'))
            self.customize_button(self.button_handle[button_name], 1)
            self.button_handle[button_name].place(relx=id / len(button_list), rely=0, relwidth=1 / len(button_list), relheight=1)
        self.pra_data_render()

    def clear(self):
        for wg in self.content.winfo_children():
            wg.destroy()
    
    def file_render(self):
        self.clear()
        # self.label = Label(self.content, text='From File tab', font=self.default_font)
        # self.label.place(relx=0.4, rely=0.45, relwidth=0.2, relheight=0.1)
        self.file_entry = ttk.Entry(self.content, textvariable=self.csv_filename, font=('Ubuntu Mono', 13))
        self.file_entry.place(relx=0.3, rely=0.1, relwidth=0.2, relheight=0.1)
        self.browse_button = ttk.Button(self.content, text='Browse', style='Custom.TButton', command=lambda: self.open_file_browser(('CSV', '*.csv')))
        self.browse_button.place(relx=0.5, rely=0.1, relwidth=0.1, relheight=0.1)
        self.read_button = ttk.Button(self.content, text='Read', style='Custom.TButton', command=self.read_file1)
        self.read_button.place(relx=0.6, rely=0.1, relwidth=0.1, relheight=0.1)

        self.pdl_entry = ttk.Entry(self.content, textvariable=self.pdlstr, font=('Ubuntu Mono', 13))
        self.pdl_entry.place(relx=0.3, rely=0.3, relwidth=0.2, relheight=0.1)
        self.pdl_label = ttk.Label(self.content, text='', font=('Ubuntu Mono', 10), background='#ffffff')
        self.pdl_label.place(relx=0.5, rely=0.3, relwidth=0.45, relheight=0.1)
        
        self.ts_label = ttk.Label(self.content, text=f'ts={self.tsvalue.get()}', font=('Ubuntu Mono', 10))
        self.ts_label.place(relx=0.4, rely=0.5, relwidth=0.1, relheight=0.1)
        self.tsscale = ttk.Scale(self.content, from_=1, to=50, orient='horizontal', variable=self.tsvalue, command=lambda x : self.ts_label.configure(text=f'ts={x}'))
        self.tsscale.place(relx=0.2, rely=0.5, relwidth=0.2, relheight=0.1)
        self.qts_label = ttk.Label(self.content, text=f'qts={self.qtsvalue.get()}', font=('Ubuntu Mono', 10))
        self.qts_label.place(relx=0.7, rely=0.5, relwidth=0.1, relheight=0.1)
        self.qtsscale = ttk.Scale(self.content, from_=1, to=50, orient='horizontal', variable=self.qtsvalue, command=lambda x : self.qts_label.configure(text=f'qts={x}'))
        self.qtsscale.place(relx=0.5, rely=0.5, relwidth=0.2, relheight=0.1)
        

    def file_page_banker(self):
        self.clear()
        self.file_entry = ttk.Entry(self.content, textvariable=self.json_filename, font=('Ubuntu Mono', 13))
        self.file_entry.place(relx=0.3, rely=0.45, relwidth=0.2, relheight=0.1)
        self.browse_button = ttk.Button(self.content, text='Browse', style='Custom.TButton', command=lambda: self.open_file_browser(('JSON', '*.json')))
        self.browse_button.place(relx=0.5, rely=0.45, relwidth=0.1, relheight=0.1)
        self.read_button = ttk.Button(self.content, text='Read', style='Custom.TButton', command=self.read_file2)
        self.read_button.place(relx=0.6, rely=0.45, relwidth=0.1, relheight=0.1)

    def image_render(self):
        self.clear()
        if not hasattr(self, 'input_data2') or not self.input_data2:
            messagebox.showerror(title='Error', message='Enter data first')
            self.file_page_banker()
            return
        if len(self.input_data2) == 2 and type(self.input_data2[0]) == list and type(self.input_data2[1]) == dict:
            fig = banker(self.input_data2[0], self.input_data2[1])
        else:
            fig = banker([], {})
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas.get_tk_widget().place(relx=0, rely=0, relwidth=1, relheight=1)

    def open_file_browser(self, filetype):
        file_path = filedialog.askopenfilename(title='Select a file', filetypes=[filetype])
        self.file_entry.delete(0, END)
        self.file_entry.insert(0, file_path)

    def read_file1(self):
        file_path = self.file_entry.get()
        self.input_data1 = []
        try:
            with open(file_path, 'r') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    self.input_data1.append(tuple(int(x) if x.isdigit() else x for x in row))
            self.handle_scheduler = Scheduler(self.input_data1)
            self.pdl_label.configure(text=f'Enter {len(self.input_data1)} priorities >= 0 seperated by comma without spaces')
        except Exception as e:
            messagebox.showerror(title='Error', message=f'{e}')

    def read_file2(self):
        file_path = self.file_entry.get()
        self.input_data2 = []
        try:
            with open(file_path, 'r') as f:
                self.input_data2 = json.loads(f.read())
        except Exception as e:
            messagebox.showerror(title='Error', message=f'{e}')
        
    def __read_pdl(self):
        pdlstr = self.pdlstr.get().strip()
        if len(pdlstr) == 0:
            return []
        else:
            testarr = pdlstr.split(','); ans = []
            for unit in testarr:
                try:
                    val = int(unit)
                    ans.append(val)
                except Exception:
                    return []
            return ans

    def fifo_render(self):
        try:
            self.clear()
            fig = self.handle_scheduler.fifo()[0]
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        except Exception as e:
            messagebox.showerror(title='Error', message='Enter data first')
            self.file_render()

    def sjf_render(self):
        try:
            self.clear()
            fig = self.handle_scheduler.sjf()[0]
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        except Exception as e:
            messagebox.showerror(title='Error', message='Enter data first')
            self.file_render()

    def srtf_render(self):
        try:
            self.clear()
            fig = self.handle_scheduler.srtf()[0]
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        except Exception as e:
            messagebox.showerror(title='Error', message='Enter daa first')
            self.file_render()

    def hrrf_render(self):
        try:
            self.clear()
            fig = self.handle_scheduler.hrrf()[0]
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        except Exception as e:
            messagebox.showerror(title='Error', message='Enter data first')
            self.file_render()

    def rr_render(self):
        try:
            self.clear()
            fig = self.handle_scheduler.rr(int(self.tsvalue.get()))[0]
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        except Exception as e:
            messagebox.showerror(title='Error', message='Enter data first')
            self.file_render()

    def pp_render(self):
        try:
            self.clear()
            pdlarrint = self.__read_pdl()
            if len(pdlarrint) != len(self.input_data1):
                messagebox.showerror(title='Error', message='Priority distribution inappropriate. Check guidelines for help')
                self.file_render()
                return
            fig = self.handle_scheduler.prio_preemptive(pdlarrint)[0]
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        except Exception as e:
            messagebox.showerror(title='Error', message='Enter data first')
            self.file_render()

    def pnp_render(self):
        try:
            self.clear()
            pdlarrint = self.__read_pdl()
            if len(pdlarrint) != len(self.input_data1):
                messagebox.showerror(title='Error', message='Priority distribution inappropriate. Check guidelines for help')
                self.file_render()
                return
            fig = self.handle_scheduler.prio_no_preemptive(pdlarrint)[0]
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        except Exception as e:
            messagebox.showerror(title='Error', message=f'Enter data first {e}')
            self.file_render()

    def mlq_render(self):
        try:
            self.clear()
            pdlarrint = self.__read_pdl()
            if len(pdlarrint) != len(self.input_data1):
                messagebox.showerror(title='Error', message='Priority distribution inappropriate. Check guidelines for help')
                self.file_render()
                return
            fig = self.handle_scheduler.mlq(pdlarrint, int(self.qtsvalue.get()), int(self.tsvalue.get()))[0]
            canvas = FigureCanvasTkAgg(fig, master=self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        except Exception as e:
            messagebox.showerror(title='Error', message='Enter data first')
            self.file_render()

    def pra_data_render(self):
        self.clear()
        self.seq_entry = ttk.Entry(self.content, textvariable=self.seq_str, font=('Ubuntu Mono', 13))
        self.seq_entry.place(relx=0.3, rely=0.4, relwidth=0.4, relheight=0.1)
        self.frame_count_label = ttk.Label(self.content, text=f'Frame={self.frame_count.get()}', font=('Ubuntu Mono', 13))
        self.frame_count_label.place(relx=0.6, rely=0.6, relwidth=0.1, relheight=0.1)
        self.frame_count_scale = ttk.Scale(self.content, from_=1, to=100, variable=self.frame_count, command=lambda x : self.frame_count_label.configure(text=f'Frame={x}'))
        self.frame_count_scale.place(relx=0.3, rely=0.6, relwidth=0.3, relheight=0.1)

    def pra_fifo_render(self):
        self.clear()
        seq = self.seq_str.get()
        if len(seq) > 0 and all([x.isdigit() for x in seq.split(',')]):
            fig, page_list, hit_count, miss_count = self.pra_instance.fifo(seq, self.frame_count.get())
            canvas = FigureCanvasTkAgg(fig, self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        else:
            messagebox.showerror(title='Error', message='Wrong Input Sequence')
            self.pra_data_render()

    def pra_lru_render(self):
        self.clear()
        seq = self.seq_str.get()
        if len(seq) > 0 and all([x.isdigit() for x in seq.split(',')]):
            fig, page_list, hit_count, miss_count = self.pra_instance.lru(seq, self.frame_count.get())
            canvas = FigureCanvasTkAgg(fig, self.content)
            canvas_widget = canvas.get_tk_widget()
            canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.animation = getattr(fig, 'animation', None)
        else :
            messagebox.showerror(title='Error', message='Wrong Input Sequence')
            self.pra_data_render()
    

if __name__ == '__main__':
    app = App()
    app.mainloop()