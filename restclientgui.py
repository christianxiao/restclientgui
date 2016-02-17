#python3
import tkinter
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import tkinter.scrolledtext
from tkinter import filedialog

import urllib.parse
from urllib.parse import urlparse
import http.client

import json

def http_client(schema,host,port,method,url,body,headers):
    if schema == 0:
        conn = http.client.HTTPConnection(host,port)
    else:
        conn = http.client.HTTPSConnection(host,port)
    if body:
        # if body is string, it will be encoded as ISO-8851-1,not utf-8
        body = body.encode("utf-8")
    conn.request(method,url,body,headers)
    response = conn.getresponse()
    headers = response.getheaders()
    html = response.read().decode('utf-8')
    conn.close()
    return html,headers

def http_client_context(conn,method,url,body,headers):
    if body:
        # if body is string, it will be encoded as ISO-8851-1,not utf-8
        body = body.encode("utf-8")
    conn.request(method,url,body,headers)
    response = conn.getresponse()
    html = response.read().decode('utf-8')
    return html

def headers_to_str(headers):
    s = ""
    if headers:
        for h in headers:
            s = s + h[0] + ":" + h[1] +"\n"
    else:
        s = "\n"
    return s[0:-1]

def str_to_headers(strh):
    headers = {}
    strh = strh.strip()
    if strh:
        hlist = strh.splitlines()
        for h in hlist:
            key,p,value = h.partition(":")
            headers[key] = value
    return headers

def json_pretty(jtext):
    jo = json.loads(jtext.get(1.0,END).strip())
    pj = json.dumps(jo,indent=4)
    jtext.delete(1.0,END)
    jtext.insert(END,pj)

def centerWindow(root,w,h):
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    
    x = (sw - w)/2
    y = (sh - h)/2
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))

class MainFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.grid(column=0, row=0, sticky=(W,E,N,S))
        self['borderwidth'] = 2
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.initUI()
        
    def send(self):
        schema = self.schemavar.get()
        sch = 0
        if schema == "https://":
            sch = 1
        url = schema + self.urlvar.get()
        url = urlparse(url)
        method = self.methodvar.get()
        sheaders = str_to_headers(self.datah_text.get(1.0,END).strip())
        html = None
        headers = None
        if method == "GET":
            html,headers = http_client(sch,url.hostname,url.port,self.methodvar.get(),url.path,self.data_text.get(1.0,END).strip(),sheaders)
        elif method == "POST":
            html,headers = http_client(sch,url.hostname,url.port,self.methodvar.get(),url.path,self.data_text.get(1.0,END).strip(),sheaders)
        elif method == "DELETE":
            html,headers = http_client(sch,url.hostname,url.port,self.methodvar.get(),url.path,self.data_text.get(1.0,END).strip(),sheaders)
        elif method == "PUT":
            html,headers = http_client(sch,url.hostname,url.port,self.methodvar.get(),url.path,self.data_text.get(1.0,END).strip(),sheaders)
        elif method == "HEAD":
            html,headers = http_client(sch,url.hostname,url.port,self.methodvar.get(),url.path,self.data_text.get(1.0,END).strip(),sheaders)
        else :
            pass
        self.response_data.delete(1.0,END)
        self.response_data.insert(END,html)
        self.response_headers.delete(1.0,END)
        self.response_headers.insert(END,headers_to_str(headers))

    def onError(self,message):
        messagebox.showerror("Error", message)
        
    def onWarn(self,message):
        messagebox.showwarning("Warning", message)
        
    def onQuest(self,message):
        messagebox.askquestion("Question", message)
        
    def onInfo(self,message):
        messagebox.showinfo("Information", message)

    def save(self):
        filename = filedialog.asksaveasfilename(initialdir="data/")
        if filename:
            o = {}
            o["method"] = self.methodvar.get()
            o["schema"] = self.schemavar.get()
            o["url"] = self.urlvar.get()
            o["sheaders"] = self.datah_text.get(1.0,END)
            o["data"] = self.data_text.get(1.0,END)
            o["response_headers"] = self.response_headers.get(1.0,END)
            o["response_data"] = self.response_data.get(1.0,END)
            with open(filename,"w") as f:
                json.dump(o,f,indent=4)

    def open(self):
        filename = filedialog.askopenfilename(initialdir="data/")
        if filename:
            with open(filename, 'r') as f:
                o = json.load(f)
                self.methodvar.set(o["method"])
                self.schemavar.set(o["schema"])
                self.urlvar.set(o["url"])
                self.datah_text.delete(1.0,END)
                self.datah_text.insert(END,o["sheaders"])
                self.data_text.delete(1.0,END)
                self.data_text.insert(END,o["data"])
                self.response_headers.delete(1.0,END)
                self.response_headers.insert(END,o["response_headers"])
                self.response_data.delete(1.0,END)
                self.response_data.insert(END,o["response_data"])

    def createMenu(self):
        self.parent.option_add('*tearOff', FALSE)
        menubar = Menu(self.parent)
        self.parent['menu'] = menubar

        menu_file = Menu(menubar)
        menubar.add_cascade(menu=menu_file, label='File')

        menu_file.add_command(label='save', command=self.save)
        menu_file.add_command(label='open...', command=self.open)

    def initUI(self):
        frame1 = ttk.Frame(self)
        frame1.columnconfigure(0,weight=1)
        frame1.columnconfigure(1,weight=1)
        frame1.columnconfigure(2,weight=3)
        frame1.columnconfigure(3,weight=1)
        frame1.rowconfigure(0,weight=1)
        frame1.grid(row=0,column=0,sticky=(W,E,N,S))

        self.methodvar = StringVar()
        self.methodvar.set('GET')
        methodcomb = ttk.Combobox(frame1, textvariable=self.methodvar,width=6)
        methodcomb['values'] = ('GET', 'POST', 'PUT','DELETE','HEAD')
        methodcomb.grid(row=0,column=0,sticky=(W,E,N,S))

        self.schemavar = StringVar()
        self.schemavar.set('http://')
        schemacomb = ttk.Combobox(frame1, textvariable=self.schemavar,width=6)
        schemacomb['values'] = ('http://', 'https://')
        schemacomb.grid(row=0,column=1,sticky=(W,E,N,S))

        self.urlvar = StringVar()
        urlentry = ttk.Entry(frame1, textvariable=self.urlvar,width=70)
        urlentry.grid(row=0,column=2,sticky=(W,E,N,S))

        send_button = ttk.Button(frame1, text='send', command=self.send,width=6)
        send_button.grid(row=0,column=3,sticky=(W,E,N,S))

        frame2 = ttk.Frame(self)
        frame2.columnconfigure(0,weight=1)
        frame2.columnconfigure(1,weight=3)
        frame2.rowconfigure(0,weight=1)
        frame2.rowconfigure(1,weight=1)
        frame2.grid(row=1,column=0,sticky=(W,E,N,S))

        datah_label = ttk.Label(frame2, text='add headers(key:value per line)\n(content-length may be auto added):')
        datah_label.grid(row=0,column=0,sticky=(W))

        data_label = ttk.Label(frame2, text='send data(utf-8 encoded):')
        data_label.grid(row=0,column=1,sticky=(W))

        self.datah_text = tkinter.scrolledtext.ScrolledText(frame2,width=30,height=10)
        self.datah_text.grid(row=1,column=0,sticky=(W,E,N,S))

        self.data_text = tkinter.scrolledtext.ScrolledText(frame2,width=60,height=10)
        self.data_text.grid(row=1,column=1,sticky=(W,E,N,S))

        json_button = ttk.Button(frame2, text='json format', command=lambda jtext=self.data_text:json_pretty(jtext))
        json_button.grid(row=0,column=1,sticky=(E))

        frame3 = ttk.Frame(self)
        frame3.grid(row=2,column=0,sticky=(W,E,N,S))
        frame3.columnconfigure(0,weight=1)
        frame3.columnconfigure(1,weight=3)
        frame3.rowconfigure(0,weight=1)
        frame3.rowconfigure(1,weight=1)

        responseh_label = ttk.Label(frame3, text='response headers:')
        responseh_label.grid(row=0,column=0,sticky=(W))

        response_label = ttk.Label(frame3, text='response data(utf-8 encoded):')
        response_label.grid(row=0,column=1,sticky=(W))

        self.response_headers = tkinter.scrolledtext.ScrolledText(frame3,width=30)
        self.response_headers.grid(row=1,column=0,sticky=(W,E,N,S))

        self.response_data = tkinter.scrolledtext.ScrolledText(frame3,width=60)
        self.response_data.grid(row=1,column=1,sticky=(W,E,N,S))

        json_button1 = ttk.Button(frame3, text='json format', command=lambda jtext=self.response_data:json_pretty(jtext))
        json_button1.grid(row=0,column=1,sticky=(E))

        self.createMenu()

if __name__ == '__main__':

    root = Tk()
    root.title("rest client")
    root.columnconfigure(0,weight=1)
    root.rowconfigure(0,weight=1)
    centerWindow(root,800,600)

    m = MainFrame(root)

    root.mainloop()