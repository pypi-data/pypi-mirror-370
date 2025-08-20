from ...imports import *

def getRunner(self,layout):


    createWidget(
            layout=layout,
            label="User:",
            widgetFunc=QHBoxLayout,
            getLayout={},
            addFunc='addWidget',
            widgets = (
                (self.user_in, {"stretch":2}),
                ("Path:"),
                (self.path_in, {"stretch":3}),
                self.run_btn,
                self.rerun_btn,
                self.clear_btn
            )
        )

    createWidget(
            layout=layout,
            label="Log Output:",
            widgetFunc=QHBoxLayout,
            getLayout={"stretch":1},
            addFunc='addWidget',
            widgets = (
                self.rb_all,
                self.rb_err,
                self.rb_wrn,
                self.cb_try_alt_ext
            )
        )

     
    addWidgets(layout, 'addWidget', self.log_view, stretch=3)
    left = createWidget(
            layout=None,
            label="Errors (file:line:col):",
            widgetFunc=QVBoxLayout,
            getLayout={"stretch":1},
            addFunc='addWidget',
            widgets=(self.errors_list,)
            )
    right = createWidget(
            layout=None,
            label="Warnings (file:line:col):",
            widgetFunc=QVBoxLayout,
            getLayout={"stretch":1},
            addFunc='addWidget',
            widgets=(self.warnings_list,)
            )

    lists_row = getRow(left, right)
    add_layout(layout,lists_row, stretch=2)

    tabs.addTab(page, "Runner")
