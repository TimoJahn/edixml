"""D18A"""
import json
from tkinter import *
from tkinter.ttk import Combobox
from tkinter.scrolledtext import ScrolledText
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showerror
from ast import literal_eval
from edixml import *

# Segment definitions D18A with Service Segments V4
SD = {**json.loads(open('d18a_segments.json').read()), **json.loads(open('V42-9735-10_service_segments.json').read())}
# Element definitions D18A with Service Elements V4
ED = {**json.loads(open('d18a_codes.json').read()), **json.loads(open('V42-9735-10_service_codes.json').read())}
# Message definitions D18A
MD = json.loads(open('d18a_messages.json').read())


class Editor(Toplevel):
    @property
    def text(self):
        return self.sc_text.get('1.0', END)

    @text.setter
    def text(self, value):
        pos = self.sc_text.yview()
        self.sc_text.delete('1.0', END)
        self.sc_text.insert(END, value)
        self.sc_text.yview_moveto(pos[0])

    def __init__(self, master):
        super().__init__(master)

        self.index_matches = None
        self.current_index = None

        self.search_content = StringVar()
        self.sc_text = ScrolledText(self, wrap=NONE)

        self.x_scrollbar_content_text = Scrollbar(self, orient=HORIZONTAL, command=self.sc_text.xview)
        self.sc_text.configure(xscrollcommand=self.x_scrollbar_content_text.set)
        self.wrap_text = IntVar()
        self.wrap_text.set(False)

        Button(self, text='<-', command=self.click_prev_button).grid(row=0, column=0)
        self.search_content_entry = Entry(self, textvariable=self.search_content)
        self.search_content_entry.bind('<KeyRelease>', lambda event : self.highlight_pattern(event.widget.get()))
        self.search_content_entry.grid(row=0, column=1, sticky=W + E)
        Button(self, text='->', command=self.click_next_button).grid(row=0, column=2)
        Checkbutton(self, text="Wrap Text", variable=self.wrap_text,
                    command=lambda: self.sc_text.config(wrap=NONE if not self.wrap_text.get() else WORD)
                    ).grid(row=1, column=0)
        self.sc_text.grid(row=2, column=0, columnspan=3, sticky=N + S + E + W)
        self.x_scrollbar_content_text.grid(row=3, column=0, columnspan=3, sticky=W + E)

        self.columnconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', lambda t=self: t.withdraw())

    def click_next_button(self):
        if not self.index_matches:
            return
        if self.current_index is None:
            self.current_index = 0
        else:
            self.current_index += 1
        self.current_index %= len(self.index_matches)
        self.sc_text.see(self.index_matches[self.current_index])

    def click_prev_button(self):
        if not self.index_matches:
            return
        if self.current_index is None:
            self.current_index = len(self.index_matches) - 1
        else:
            self.current_index -= 1
        self.current_index %= len(self.index_matches)
        self.sc_text.see(self.index_matches[self.current_index])

    def highlight_pattern(self, pattern, start="1.0", end="end"):
        for t in self.sc_text.tag_names():
            self.sc_text.tag_delete(t)

        if not pattern:
            return
        self.index_matches = []
        self.current_index = None

        self.sc_text.tag_config('found', background="green")
        start = self.sc_text.index(start)
        end = self.sc_text.index(end)
        self.sc_text.mark_set("matchStart", start)
        self.sc_text.mark_set("matchEnd", start)
        self.sc_text.mark_set("searchLimit", end)
        count = IntVar()
        while True:
            index = self.sc_text.search(pattern, "matchEnd", "searchLimit", count=count)
            if index == "":
                break
            self.sc_text.mark_set("matchStart", index)
            match_index = "%s+%sc" % (index, count.get())
            self.index_matches.append(match_index)
            self.sc_text.mark_set("matchEnd", match_index)
            self.sc_text.tag_add('found', "matchStart", "matchEnd")


class GUI(Tk):
    def __init__(self):
        super().__init__()
        self.segments = None
        self.wm_title(__doc__)

        self.menubar = Menu(self)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Open EDI', command=self.open_edi)
        self.filemenu.add_command(label='Open XML', command=self.open_xml)
        self.menubar.add_cascade(label="File", menu=self.filemenu)
        self.config(menu=self.menubar)

        self.lbl_message = Label(self, text='Message')
        self.lbl_message.grid(row=0, column=0)
        self.cb_message = Combobox(self, values=list(MD))
        self.cb_message.bind('<<ComboboxSelected>>', self.select_message)
        self.cb_message.grid(row=1, column=0)

        self.lbl_segment = Label(self, text='Segment')
        self.lbl_segment.grid(row=0, column=1)
        self.cb_segment = Combobox(self, values=list(SD))
        self.cb_segment.bind('<<ComboboxSelected>>', self.select_segment)
        self.cb_segment.grid(row=1, column=1)

        self.lbl_code = Label(self, text='Code')
        self.lbl_code.grid(row=0, column=2)
        self.cb_code = Combobox(self, values=list(ED))
        self.cb_code.bind('<<ComboboxSelected>>', self.select_code)
        self.cb_code.grid(row=1, column=2)

        self.lbl_formats = Label(self, text='Formats')
        self.lbl_formats.grid(row=0, column=3, sticky=W)
        self.formats = Frame(self)
        self.formats.grid(row=1, column=3)
        self.var_edi = IntVar()
        self.chk_edi = Checkbutton(self.formats, text='EDI', variable=self.var_edi, command=self.switch_edi)
        self.chk_edi.pack(side=LEFT)
        self.var_segments = IntVar()
        self.chk_segments = Checkbutton(self.formats, text='Segments', variable=self.var_segments, command=self.switch_segments)
        self.chk_segments.pack(side=LEFT)
        self.var_xml = IntVar()
        self.chk_xml = Checkbutton(self.formats, text='XML', variable=self.var_xml, command=self.switch_xml)
        self.chk_xml.pack(side=LEFT)
        self.var_report = IntVar()
        self.chk_report = Checkbutton(self.formats, text='Report', variable=self.var_report, command=self.switch_report)
        self.chk_report.pack(side=LEFT)

        self.editor_message = Editor(self)
        self.editor_segment = Editor(self)
        self.editor_code = Editor(self)

        self.editor_edi = Editor(self)
        self.editor_edi.sc_text.bind('<KeyRelease>', self.edit_edifact)
        self.editor_edi.title('EDI')

        self.editor_segments = Editor(self)
        self.editor_segments.sc_text.bind('<KeyRelease>', self.edit_segments)
        self.editor_segments.title('Segments')

        self.editor_xml = Editor(self)
        self.editor_xml.sc_text.bind('<KeyRelease>', self.edit_xml)
        self.editor_xml.title('XML')

        self.editor_report = Editor(self)
        self.editor_report.title('Report')

        self.mainloop()

    def switch_edi(self, event=None):
        if self.var_edi.get():
            self.editor_edi.deiconify()
        else:
            self.editor_edi.withdraw()

    def switch_segments(self, event=None):
        if self.var_segments.get():
            self.editor_segments.deiconify()
        else:
            self.editor_segments.withdraw()

    def switch_xml(self, event=None):
        if self.var_xml.get():
            self.editor_xml.deiconify()
        else:
            self.editor_xml.withdraw()

    def switch_report(self, event=None):
        if self.var_report.get():
            self.editor_report.deiconify()
        else:
            self.editor_report.withdraw()

    def select_message(self, event=None):
        msg = self.cb_message.get()
        self.editor_message.deiconify()
        if msg in ED['0065']['table']:
            self.editor_message.title(ED['0065']['table'][msg]['name'])
        else:
            self.editor_message.title(f'MISSING {msg}')
        self.editor_message.text = MD[msg]['description']

    def select_segment(self, event=None):
        seg = self.cb_segment.get()
        self.editor_segment.deiconify()
        self.editor_segment.title(f'{SD[seg]["name"]}')
        self.editor_segment.text = pprint.pformat(SD[seg]['table'], width=200)

    def select_code(self, event=None):
        code = self.cb_code.get()
        self.editor_code.deiconify()
        self.editor_code.title(f'{ED[code]["name"]}')
        if 'table' in ED[code]:
            self.editor_code.text = pprint.pformat(ED[code]['table'])
        else:
            self.editor_code.text = ''

    def report(self):
        self.editor_report.text = report(self.segments, SD, ED)

    def edit_xml(self, event=None):
        try:
            self.segments = parse_xml(ElementTree.fromstring(self.editor_xml.text))
        except Exception as err:
            showerror('Edit XML Error', err)
            return
        self.editor_edi.text = make_edi(self.segments, with_newline=True).decode('utf8')
        self.editor_segments.text = pprint.pformat(self.segments)
        self.report()

    def edit_segments(self, event=None):
        try:
            self.segments = literal_eval(self.editor_segments.text)
        except Exception as err:
            showerror('Edit Segments Error', err)
            return
        self.editor_edi.text = make_edi(self.segments, with_newline=True).decode('utf8')
        self.editor_xml.text = pretty_xml(make_edi_xml(self.segments, SD, ED))
        self.report()

    def edit_edifact(self, event=None):
        try:
            self.segments = parse_edi(self.editor_edi.text.encode('utf8'))
        except Exception as err:
            showerror('Edit EDI Error', err)
            return
        self.editor_segments.text = pprint.pformat(self.segments)
        self.editor_xml.text = pretty_xml(make_edi_xml(self.segments, SD, ED))
        self.report()

    def reload(self):
        if self.var_segments.get():
            self.editor_segments.deiconify()
        if self.var_edi.get():
            self.editor_edi.deiconify()
        if self.var_xml.get():
            self.editor_xml.deiconify()
        if self.var_report.get():
            self.editor_report.deiconify()

        message = [element[1][0] for segment, element in self.segments if segment == 'UNH'] if self.segments else None
        if message:
            self.cb_message.set(message)
            self.select_message()

        self.editor_edi.text = make_edi(self.segments, with_newline=True).decode('utf8')
        self.editor_segments.text = pprint.pformat(self.segments)
        self.editor_xml.text = pretty_xml(make_edi_xml(self.segments, SD, ED))

    def open_edi(self):
        file = askopenfilename(title='Open EDI')
        if not file:
            return
        try:
            self.segments = parse_edi(open(file, 'rb').read())
        except Exception as err:
            showerror('Open EDI Failed', err)
            return
        self.wm_title(file)
        self.reload()
        self.report()
        self.var_edi.set(True)
        self.switch_edi()

    def open_xml(self):
        file = askopenfilename(title='Open XML')
        if not file:
            return
        try:
            self.segments = parse_xml(ElementTree.parse(file).getroot())
        except Exception as err:
            showerror('Open XML Failed', err)
        self.wm_title(file)
        self.reload()
        self.report()
        self.var_xml.set(True)
        self.switch_xml()


if __name__ == '__main__':
    GUI()
