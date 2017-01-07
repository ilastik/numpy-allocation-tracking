import os
import traceback
import inspect
from jinja2 import Template

from numpy_allocation_tracking.track_allocations import AllocationTracker

class PrettyAllocationTracker(AllocationTracker):
    """
    Subclass of AllocationTracker that produces a nicer-looking output file, along with stack trace information.
    """
    def __init__(self, threshold=1000, traceback_length=5):
        super(PrettyAllocationTracker, self).__init__(threshold)
        self.traceback_length = traceback_length
        self.current_stack = None
    
    def get_code_line(self):
        # first frame is this line, then check_line_changed(), then 2 callbacks,
        # then actual code.
        try:
            return inspect.stack()[5][1:]
        except:
            return inspect.stack()[0][1:]

    def check_line_changed(self):
        oldline = self.current_line
        oldstack = self.current_stack
        if self.current_stack is None:
            self.current_stack = traceback.format_stack()

        # Base class detects line changes
        super(PrettyAllocationTracker, self).check_line_changed()
        
        # Did the line change?
        if oldline is not None and self.current_line != oldline:
            # Append stack info to the last completed line
            self.allocation_trace[-1] += (self.current_stack,)

            # Save current traceback text for the current line
            self.current_stack = traceback.format_stack()

    def __enter__(self):
        # Base class doesn't return self, but we do.
        super(PrettyAllocationTracker, self).__enter__()
        return self
    
    def __exit__(self, type, value, traceback):
        super(PrettyAllocationTracker, self).__exit__(type, value, traceback)

    def write_html(self, output_filepath):
        columns = [ 'event #',
                    'line',
                    'bytes allocated',
                    'bytes freed',
                    '# allocations',
                    '# frees',
                    'max memory usage',
                    'long lived bytes',
                    'stack trace' ]

        event_rows = []
        for row_index, event in enumerate(self.allocation_trace):
            # Init
            row = dict( zip(columns[1:], event) )
            row['event #'] = row_index
            
            line_info, bytes_allocated, bytes_freed, num_allocations, num_frees, max_memory_usage, long_lived_bytes, stack_trace = event

            # Special handling for object items
            try:
                srcfile, line, module, code, index = line_info
                line_text = "{0}({1}):\n<br><code>    {2}</code>".format(srcfile, line, code[index])
            except:
                # sometimes this info is not available (from eval()?)
                line_text = str(line_info)

            num_tracker_frames = 3 # Don't show frames for hook(), check_line_changed(), etc.
            start_frame = -(self.traceback_length+num_tracker_frames)
            stop_frame = -num_tracker_frames
            stack_trace = stack_trace[start_frame:stop_frame]

            # Add formatting
            stack_trace = [s.split('\n') for s in stack_trace]
            for item in stack_trace:
                item[0] += '<br>\n'
                item[1] = '&nbsp;&nbsp;&nbsp;&nbsp;' + item[1] + '<br>\n'
            
            # Drop last newline
            stack_trace[-1][1] = stack_trace[-1][1][:-len('<br>\n')]
            
            stack_trace = [''.join(items) for items in stack_trace]
            
            stack_trace_text = ''.join( stack_trace )
            stack_trace_text = '<code>' + stack_trace_text + '</code>'

            # Overwrite
            row['line'] = line_text
            row['stack trace'] = stack_trace_text
            row['bytes allocated'] = _format_bytecount(bytes_allocated)
            row['bytes freed'] = _format_bytecount(bytes_freed)
            row['max memory usage'] = _format_bytecount(max_memory_usage)
            row['long lived bytes'] = _format_bytecount(long_lived_bytes)
            
            event_rows.append(row)

        template_path = os.path.split(__file__)[0] + '/allocation-table.html.jinja'
        
        with open(template_path, 'r') as f_template:
            template = Template(f_template.read())
        
        rendered_html = template.render( columns=columns,
                                         event_rows=event_rows )

        with open(output_filepath, 'w') as f_output:
            f_output.write(rendered_html)


##
## Formatting utility functions
##
_magnitude_strings = {0: "B", 1: "KB", 2: "MB", 3: "GB", 4: "TB"}

def _format_bytecount(ram, trailing_digits=1):
    mant, exp = _toScientific(ram)
    desc = _magnitude_strings[exp]
    fmt_str = "{:.%uf}{}" % (trailing_digits,)
    return fmt_str.format(mant, desc)

def _toScientific(ram, base=1024, expstep=1, explimit=4):
    exp = 0
    mant = float(ram)
    step = base**expstep
    while mant >= step and exp + expstep <= explimit:
        mant /= step
        exp += expstep
    return mant, exp

if __name__ == '__main__':
    print(os.getcwd())
    
    import numpy as np
    tracker = PrettyAllocationTracker(1000, traceback_length=5)
    with tracker:
        for i in range(100):
            np.zeros(i * 100)
            np.zeros(i * 200)
    tracker.write_html("allocations.html")

    import subprocess
    import platform
    if platform.platform() == "Darwin":
        subprocess.check_call("open allocations.html", shell=True)
    if platform.platform() == "Linux":
        subprocess.check_call("xdg-open allocations.html", shell=True)
