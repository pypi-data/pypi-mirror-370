from ..imports import *
def get_args_kwargs(*args,**kwargs):
    return args,kwargs
def addWidgets(layout,addFunc, *args, **kwargs):
    addFunc = getattr(layout, addFunc)
    for arg in args:
        if isinstance(arg, tuple) and len(arg) == 2 and isinstance(arg[1], dict):
            widget, options = arg
            if isinstance(widget, str):
                widget = QLabel(widget)
            addFunc(widget, **options)
        elif isinstance(arg, str):
            widget = QLabel(arg)
            addFunc(widget, **kwargs)
        else:
            addFunc(arg, **kwargs)
def createLayout(label,widgetFunc,addFunc,*args,**kwargs):
    layout = widgetFunc()
    label = QLabel(label)
    args =  (label,*args)  
    addWidgets(layout,addFunc,*args,**kwargs)
    return layout

def createWidget(layout, label, widgetFunc, addFunc, getLayout, widgets, addSubFunc='addLayout'):
    sublayout = createLayout(label, widgetFunc, addFunc, **getLayout)
    addWidgets(sublayout, addFunc, *widgets)
    if layout is not None:
        add_sub_method = getattr(layout, addSubFunc)
        add_sub_method(sublayout)
    return sublayout

def add_func(tabs,addFunc,*args,**kwargs):
    add_sub_method = getattr(tabs, addFunc)
    add_sub_method(*args,**kwargs)
def add_tab(tabs,**kwargs):
    tabs.addTab(**kwargs)
def add_layout(layout,*args,**kwargs):
    add_func(layout,'addLayout',*args,**kwargs)
