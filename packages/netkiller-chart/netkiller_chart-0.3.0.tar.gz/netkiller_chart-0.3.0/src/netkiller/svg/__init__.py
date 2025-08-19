from .ScalableVectorGraphics import Svg


def attribute(kwargs):
    attrs = []
    for key, value in kwargs.items():
        if key in ['klass', 'clazz']:
            key = 'class'
        elif '_' in key:
            key = key.replace('_', '-')
        attrs.append(f'{key}="{value}"')
    return " ".join(attrs)
