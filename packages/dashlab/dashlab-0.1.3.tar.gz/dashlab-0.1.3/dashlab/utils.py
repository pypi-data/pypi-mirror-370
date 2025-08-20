import inspect
import ipywidgets as ipw


def _fix_trait_sig(cls):
    "Avoid showing extra kwargs by having a class attribute _no_kwargs"
    params = [inspect.Parameter(key, inspect.Parameter.KEYWORD_ONLY, default=value) 
        for key, value in cls.class_own_traits().items() if not key.startswith('_')] # avoid private
    
    if not hasattr(cls,'_no_kwargs'):
        params.append(inspect.Parameter('kwargs', inspect.Parameter.VAR_KEYWORD)) # Inherited widgets traits
    cls.__signature__ = inspect.Signature(params)
    return cls

def _inline_style(kws_or_widget):
    "CSS inline style from keyword arguments having _ inplace of -. Handles widgets layout keys automatically."
    if isinstance(kws_or_widget, ipw.DOMWidget):
        kws = {k:v for k,v in kws_or_widget.layout.get_state().items() if v and (k[0]!='_')}
    elif isinstance(kws_or_widget, dict):
        kws = kws_or_widget
    else:
        raise TypeError("expects dict or ipywidgets.Layout!")
    out = ''.join(f"{k.replace('_','-')}:{v};" for k,v in kws.items())
    return f'style="{out}"' if kws else ''

def _fix_init_sig(cls):
    # widgets ruin signature of subclass, let's fix it
    cls.__signature__ = inspect.signature(cls.__init__)
    return cls