import tkinter as tk
import ttkbootstrap as ttk
from .SCRIPTS import screen_position
from .CUSTOM_FRAMES import BorderFrame


class BaseTopLevelWidget(tk.Toplevel):
    """
    Basic TopLevel Widget for Message Boxes
    Input:
        parent: widget over which the widget will be positioned
        icon_path: path to the icon for the widget
        title: title message for the widget
        message = text to be shown as an alert to the user
    """

    def __init__(self, parent, icon_path=None, title=None, message=None):

        # Configuration
        super().__init__(parent)

        if icon_path:
            self.iconbitmap(icon_path)
        if title:
            self.title(title)

        self.minsize(300, 150)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)  # Label with the message
        self.rowconfigure(1, weight=0)  # Separator
        self.rowconfigure(2, weight=0)  # Action buttons
        self.lift()

        # Label
        self.label = ttk.Label(self, text=message, justify='left', padding=5, wraplength=280)
        self.label.grid(row=0, column=0, sticky='nsew')

        # Separator
        separator = ttk.Separator(self, orient='horizontal', style='secondary.Horizontal.TSeparator')
        separator.grid(row=1, column=0, sticky='nsew')

        # Frame for the buttons
        self.buttons_frame = ttk.Frame(self, padding=5)
        self.buttons_frame.grid(row=2, column=0, sticky='nsew')
        self.buttons_frame.rowconfigure(0, weight=1)
        self.buttons_frame.columnconfigure(0, weight=1)

        # Determine relative position
        self.geometry(screen_position(self, parent))

        # Grabs focus
        self.grab_set()

        # Control variable for the buttons
        self.control_var = tk.IntVar(value=0)

    def adjust_var(self, option):
        self.control_var.set(option)
        self.destroy()

    def show(self):
        self.deiconify()
        self.wait_window()
        value = self.control_var.get()
        self.grab_release()
        return value


class OkCancelBox(BaseTopLevelWidget):
    """
    Creates an OK/CANCEL message box with the same style as the main application
    Input:
        parent: widget over which the progress bar will be positioned
        icon_path: path to the icon for the widget
        title: title message for the widget
        message: text to be shown as an alert to the user
        language: language for the buttons text
    """

    def __init__(self, parent, icon_path, title, message, language='en'):

        super().__init__(parent, icon_path, title, message)

        if language == 'br':
            cancel_text, ok_text = 'CANCELAR', 'OK'
        else:
            cancel_text, ok_text = 'CANCEL', 'OK'

        cancel_button = ttk.Button(self.buttons_frame, text=cancel_text, command=lambda: self.adjust_var(0), width=8,
                                   style='danger.TButton')
        cancel_button.grid(row=0, column=1, sticky='nsew', padx=5)

        ok_button = ttk.Button(self.buttons_frame, text=ok_text, command=lambda: self.adjust_var(1), width=8,
                               style='success.TButton')
        ok_button.grid(row=0, column=2, sticky='nsew')


class YesNoBox(BaseTopLevelWidget):
    """
    Creates a Yes/No message box with the same style as the main application
    Input:
        parent: widget over which the progress bar will be positioned
        icon_path: path to the icon for the widget
        title: title message for the widget
        message: text to be shown as an alert to the user
        language: language for the buttons text
    """

    def __init__(self, parent, icon_path, title, message, language='en'):

        super().__init__(parent, icon_path, title, message)

        if language == 'br':
            no_text, yes_text = 'NÃO', 'SIM'
        else:
            no_text, yes_text = 'NO', 'YES'

        no_button = ttk.Button(self.buttons_frame, text=no_text, command=lambda: self.adjust_var(0), width=8,
                               style='danger.TButton')
        no_button.grid(row=0, column=1, sticky='nsew', padx=5)

        yes_button = ttk.Button(self.buttons_frame, text=yes_text, command=lambda: self.adjust_var(1), width=8,
                                style='success.TButton')
        yes_button.grid(row=0, column=2, sticky='nsew')


class WarningBox(BaseTopLevelWidget):
    """
    Creates a warning message box with the same style as the main application
    Input:
        parent: widget over which the progress bar will be positioned
        icon_path: path to the icon for the widget
        title: title message for the widget
        message: text to be shown as an alert to the user
        language: language for the buttons text
    """

    def __init__(self, parent, icon_path, title, message, language='en'):

        super().__init__(parent, icon_path, title, message)

        self.label.config(style='danger.TLabel')
        ok_button = ttk.Button(self.buttons_frame, text="OK", command=lambda: self.destroy(), width=8,
                               style='danger.TButton')
        ok_button.grid(row=0, column=2, sticky='nsew')


class SuccessBox(BaseTopLevelWidget):
    """
    Creates a success message box with the same style as the main application
    Input:
        parent: widget over which the progress bar will be positioned
        icon_path: path to the icon for the widget
        title: title message for the widget
        message: text to be shown as an alert to the user
        language: language for the buttons text
    """

    def __init__(self, parent, icon_path, title, message, language='en'):

        super().__init__(parent, icon_path, title, message)

        self.label.config(style='success.TLabel')
        ok_button = ttk.Button(self.buttons_frame, text="OK", command=lambda: self.destroy(), width=8,
                               style='success.TButton')
        ok_button.grid(row=0, column=2, sticky='nsew')


class ProgressBar(tk.Toplevel):
    """
    Creates a progress bar to follow the program tasks
    Input:
        parent: widget over which the progress bar will be positioned
        message: text to be shown above the progress bar
        final_value: number that represents the final value of the progress bar (100% value)
    Method:
        update_bar(value): updates the progress bar to the current value
    """

    def __init__(self, parent, message='Processing...', final_value=100):

        # self configuration
        if True:
            super().__init__(parent)
            self.minsize(350, 100)
            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=1)
            self.rowconfigure(1, weight=0)
            self.overrideredirect(True)
            self.config(padx=10, pady=10, bd=1, relief='raised')
            self.lift()

        # Label configuration
        if True:
            self.label = ttk.Label(self, text=message, justify='left', padding=10)
            self.label.grid(row=0, column=0, sticky='nsew')
            if self.label.winfo_reqwidth() > self.minsize()[0]:
                self.minsize(self.label.winfo_reqwidth() + 20, 100)
                self.update()

        # Progress bar
        if True:
            local_frame = ttk.Frame(self)
            local_frame.grid(row=1, column=0, sticky='nsew')
            local_frame.columnconfigure(0, weight=1)
            local_frame.rowconfigure(0, weight=1)

            self.final_value = final_value
            initial_value = 0
            self.progress_var = tk.DoubleVar(value=initial_value/self.final_value)
            progress_bar = ttk.Progressbar(local_frame, variable=self.progress_var, maximum=1, orient=tk.HORIZONTAL,
                                           style='info.Striped.Horizontal.TProgressbar')
            progress_bar.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)

        # Relative position
        self.geometry(screen_position(self, parent))

        # Grabs focus
        self.grab_set()

    def update_bar(self, value):
        self.progress_var.set(value/self.final_value)
        self.update_idletasks()

    def show(self):
        self.deiconify()
        self.wait_window()
        self.grab_release()


class Tooltip:
    """ It creates a tooltip window for a given widget as the mouse goes over it. """

    def __init__(self, widget, text='widget info', bg='#FFFF8B', fg='black',
                 wait_time=500, wrap_length=250, hide_time=5000):

        self.style = widget.winfo_toplevel().style
        self.style.configure('custom.TLabel', background=bg, foreground=fg)
        self.widget = widget
        self.root = widget.winfo_toplevel()
        self.text = text
        self.wait_time = wait_time
        self.wrap_length = wrap_length
        self.hide_time = hide_time

        self.id = None
        self.top_level = None

        if not self.text:
            self.widget.unbind("<Enter>")
            self.widget.unbind("<Leave>")
            self.widget.unbind("<Motion>")
            self.remove_message()
        else:
            self.widget.bind("<Enter>", self._enter)
            self.widget.bind("<Leave>", self._leave)
            self.widget.bind("<Motion>", self._move_tip)

    def _enter(self, event=None):
        self.schedule()

    def _leave(self, event=None):
        self.unschedule()
        self.hide()

    def _move_tip(self, event=None):
        if self.top_level:
            x = self.widget.winfo_pointerx() + 25
            y = self.widget.winfo_pointery() + 10
            self.top_level.geometry(f"+{x}+{y}")

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.wait_time, self.show)

    def unschedule(self):
        if self.id:
            self.widget.after_cancel(self.id)
        self.id = None

    def show(self):

        if self.top_level:
            return
        x = self.widget.winfo_pointerx() + 25
        y = self.widget.winfo_pointery() + 10

        self.top_level = ttk.Toplevel(self.widget, position=(x, y))
        self.top_level.wm_overrideredirect(True)
        self.top_level.rowconfigure(0, weight=1)
        self.top_level.columnconfigure(0, weight=1)
        self.top_level.configure(bg=self.style.colors.primary)

        label = ttk.Label(self.top_level, text=self.text, justify="left",
                          wraplength=self.wrap_length, style='custom.TLabel')
        label.grid(row=0, column=0, sticky='nsew', padx=1, pady=1)

        self.top_level.after(self.hide_time, func=self.hide)

    def get_widget_under_cursor(self):
        """Gets the widget under the current mouse cursor."""

        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        widget = self.root.winfo_containing(x, y)
        return widget

    def hide(self):
        if self.get_widget_under_cursor() == self.widget:
            self.top_level.after(self.hide_time, func=self.hide)
            return

        if self.top_level:
            self.top_level.destroy()
        self.top_level = None

    def remove_message(self):
        self.unschedule()
        self.hide()


class TimedBox(tk.Toplevel):
    """
    TopLevel widget for timed message boxes.
    Input:
        parent = widget over which the progress bar will be positioned
        message = text to be shown as an alert to the user
        time = time in seconds for the pop-up window display
        style = color scheme for the window
    """

    def __init__(self, parent, message, time=1, style=None):

        # Configuration
        if True:
            super().__init__(parent)
            self.overrideredirect(True)
            self.total_time_ms = 1000 * time
            self.minsize(250, 120)

            self.columnconfigure(0, weight=1)
            self.rowconfigure(0, weight=1)

            style_list = ('danger', 'warning', 'info', 'success', 'secondary', 'primary', 'light', 'dark', 'default')
            if style not in style_list:
                self.style = 'default'
            else:
                self.style = style

            container = BorderFrame(self, border_style=style)
            container.grid(row=0, column=0, sticky='nsew')

            container.columnconfigure(0, weight=1)
            container.columnconfigure(1, weight=0)
            container.rowconfigure(0, weight=1)
            container.rowconfigure(1, weight=0)
            container.rowconfigure(2, weight=0)

        # Widgets
        if True:
            label = ttk.Label(container, text=message, justify='left', bootstyle=self.style)
            label.grid(row=0, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)

            self.progressbar_var = tk.DoubleVar(value=0)
            self.progressbar = ttk.Progressbar(container, maximum=self.total_time_ms, orient='horizontal',
                                               mode='determinate', bootstyle=self.style,
                                               variable=self.progressbar_var)
            self.progressbar.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10)

            button = ttk.Button(container, text='CLOSE', bootstyle=self.style, command= lambda: self.destroy())
            button.grid(row=2, column=1, sticky='nsew', pady=10, padx=10)

            if label.winfo_reqwidth() > self.minsize()[0]:
                self.minsize(label.winfo_reqwidth() + 40, 120)
                self.update()

        # Determine relative position
        self.geometry(screen_position(self, parent))

        # Grabs the focus
        self.lift()
        self.focus_set()
        self.grab_set()

    def update_progress_bar(self):

        step_number = 50
        step = int(self.total_time_ms / step_number)

        for i in range(step_number):
            self.after(step)
            self.progressbar_var.set((i + 1) * step)
            self.progressbar.update()
        self.destroy()

    def show(self):
        self.update()
        self.deiconify()
        self.update_progress_bar()
        self.grab_release()
        return
