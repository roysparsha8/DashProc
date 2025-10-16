from tkinter import *
from tkinter import ttk, filedialog, messagebox
from schedulers import Scheduler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv, random

#iwc = Initial Window Configuration = (width, height, x_topleft, y_topleft, name, background_color)
class App(Tk):
    def __init__(self):
        super().__init__()
        self.iwc = (1000, 600, 100, 50, 'My App', '#ffffff')
        self.default_font = ('Ubuntu Mono', 15)
        self.title(self.iwc[4])
        self.geometry(f'{self.iwc[0]}x{self.iwc[1]}+{self.iwc[2]}+{self.iwc[3]}') # Sets witdh=1000, height=600, x_topleft=100, y_topleft=50 of main window
        self.configure(background=self.iwc[5])
        
        self.navbar2 = Frame(self, background="#272626")
        self.navbar2.place(relx=0, rely=0, relwidth=0.08, relheight=1)
        self.navbar2_content = Frame(self, background='#ffffff')
        self.navbar2_content.place(relx=0.08, rely=0, relwidth=0.92, relheight=1)
        self.navbar2_tab1 = ttk.Button(self.navbar2, text='Scheduler', command=self.scheduler)
        self.navbar2_tab1.place(relx=0, rely=0, relwidth=1, relheight=0.08 * (self.iwc[0] / self.iwc[1]))
        self.tsvalue = DoubleVar(value=1); self.qtsvalue = DoubleVar(value=1) # Auto synchronized variable
        self.pdlstr = StringVar(value='') # Auto synchronized variable
        self.scheduler()

    def clear_navbar2_content(self):
        for wg in self.navbar2_content.winfo_children():
            wg.destroy()

    def scheduler(self):
        self.clear_navbar2_content()
        self.navbar1 = Frame(self.navbar2_content, background="#777575")
        self.navbar1.place(relx=0, rely=0, relwidth=1, relheight=0.05)
        self.content = Frame(self.navbar2_content, background='#ffffff')
        self.content.place(relx=0, rely=0.05, relwidth=1, relheight=0.95)

        button_list = ['file','fifo','sjf','srtf','hrrf','rr','pp','pnp','mlq']
        self.button_handle = dict()
        for id, button_name in enumerate(button_list):
            self.button_handle[button_name] = ttk.Button(self.navbar1, text=button_name, command=getattr(self, button_name+'_render'))
            self.button_handle[button_name].place(relx=id / len(button_list), rely=0, relwidth=(1 / len(button_list)), relheight=1)
        self.file_render()

    def clear(self):
        for wg in self.content.winfo_children():
            wg.destroy()
    def file_render(self):
        self.clear()
        # self.label = ttk.Label(self.content, text='From File tab', font=self.default_font)
        # self.label.place(relx=0.4, rely=0.45, relwidth=0.2, relheight=0.1)
        self.file_entry = ttk.Entry(self.content)
        self.file_entry.place(relx=0.3, rely=0.1, relwidth=0.2, relheight=0.1)
        self.browse_button = ttk.Button(self.content, text='Browse', command=self.open_file_browser)
        self.browse_button.place(relx=0.5, rely=0.1, relwidth=0.1, relheight=0.1)
        self.read_button = ttk.Button(self.content, text='Read', command=self.read_file)
        self.read_button.place(relx=0.6, rely=0.1, relwidth=0.1, relheight=0.1)

        self.pdl_entry = ttk.Entry(self.content, textvariable=self.pdlstr)
        self.pdl_entry.place(relx=0.3, rely=0.3, relwidth=0.2, relheight=0.1)
        self.pdl_label = ttk.Label(self.content, text='', font=('Ubuntu Mono', 10))
        self.pdl_label.place(relx=0.5, rely=0.3, relwidth=0.2, relheight=0.1)

        self.tsscale = ttk.Scale(self.content, from_=1, to=50, orient='horizontal', variable=self.tsvalue, command=self.change_ts_label)
        self.tsscale.place(relx=0.2, rely=0.5, relwidth=0.2, relheight=0.1)
        self.ts_label = ttk.Label(self.content, text='', font=('Ubuntu Mono', 10))
        self.ts_label.place(relx=0.4, rely=0.5, relwidth=0.1, relheight=0.1)
        self.qtsscale = ttk.Scale(self.content, from_=1, to=50, orient='horizontal', variable=self.qtsvalue, command=self.change_qts_label)
        self.qtsscale.place(relx=0.5, rely=0.5, relwidth=0.2, relheight=0.1)
        self.qts_label = ttk.Label(self.content, text='', font=('Ubuntu Mono', 10))
        self.qts_label.place(relx=0.7, rely=0.5, relwidth=0.1, relheight=0.1)
        
        self.change_ts_label(self.tsvalue.get())
        self.change_qts_label(self.qtsvalue.get())

    def change_ts_label(self, v): 
        hasattr(self, 'ts_label') and self.ts_label.winfo_exists() and self.ts_label.configure(text=f'ts={v}')
    
    def change_qts_label(self, v):
        hasattr(self, 'qts_label') and self.qts_label.winfo_exists() and self.qts_label.configure(text=f'qts={v}')

    def open_file_browser(self):
        file_path = filedialog.askopenfilename(title='Select a file', filetypes=[('CSV', '*.csv')])
        self.file_entry.insert(0, file_path)

    def read_file(self):
        file_path = self.file_entry.get()
        self.input_data = []
        try:
            with open(file_path, 'r') as f:
                csvreader = csv.reader(f)
                for row in csvreader:
                    self.input_data.append(tuple(int(x) if x.isdigit() else x for x in row))
            self.handle_scheduler = Scheduler(self.input_data)
            self.pdl_label.configure(text=f'Enter {len(self.input_data)} priorities >= 0 seperated by comma without spaces')
        except Exception as e:
            messagebox.showerror(title='Error', message=f'{e}')

    def __read_pdl(self):
        pdlstr = self.pdlstr.get()
        if len(pdlstr) == 0:
            return []
        elif ',' in pdlstr:
            pdlarr = pdlstr.split(',')
            return [int(x) if x.isdigit() else 0 for x in pdlarr]
        else:
            return [0]

    def fifo_render(self):
        self.clear()
        fig = self.handle_scheduler.fifo()[0]
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)

    def sjf_render(self):
        self.clear()
        fig = self.handle_scheduler.sjf()[0]
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)

    def srtf_render(self):
        self.clear()
        fig = self.handle_scheduler.srtf()[0]
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)

    def hrrf_render(self):
        self.clear()
        fig = self.handle_scheduler.hrrf()[0]
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)

    def rr_render(self):
        self.clear()
        fig = self.handle_scheduler.rr(int(self.tsvalue.get()))[0]
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)

    def pp_render(self):
        self.clear()
        pdlarrint = self.__read_pdl()
        if len(pdlarrint) != len(self.input_data):
            messagebox.showerror(title='Error', message=f'Priority distribution length must be {len(self.input_data)}')
            self.file_render()
            return
        fig = self.handle_scheduler.prio_preemptive(pdlarrint)[0]
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)

    def pnp_render(self):
        self.clear()
        pdlarrint = self.__read_pdl()
        if len(pdlarrint) != len(self.input_data):
            messagebox.showerror(title='Error', message=f'Priority distribution length must be {len(self.input_data)}')
            self.file_render()
            return
        fig = self.handle_scheduler.prio_no_preemptive(pdlarrint)[0]
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)

    def mlq_render(self):
        self.clear()
        pdlarrint = self.__read_pdl()
        if len(pdlarrint) != len(self.input_data):
            messagebox.showerror(title='Error', message=f'Priority distribution length must be {len(self.input_data)}')
            self.file_render()
            return
        fig = self.handle_scheduler.mlq(pdlarrint, int(self.qtsvalue.get()), int(self.tsvalue.get()))[0]
        canvas = FigureCanvasTkAgg(fig, master=self.content)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.place(relx=0, rely=0, relwidth=1, relheight=1)


if __name__ == '__main__':
    app = App()
    app.mainloop()