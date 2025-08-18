
def mk_html_pdf(file, content, conf:dict = {}):

    options = {
      'margin-top'    : str(conf.get( 'margin-top'    , '0.0in' )),
      'margin-right'  : str(conf.get( 'margin-right'  , '0.0in' )),
      'margin-bottom' : str(conf.get( 'margin-bottom' , '0.0in' )),
      'margin-left'   : str(conf.get( 'margin-left'   , '0.0in' )),
    }

    try:
        import pdfkit
        
        file.write(pdfkit.from_string(
            content,
            False,
            options = options
        ))
        return True
    except OSError as e:
        file.write(content.encode('utf-8'))
        print(
           "[pdfkit] failed to create file, "
           "please install all the depedencies required!"
        )
        return False


def mk_svg_png(file,content,conf:dict = {}):
    _content = content.encode('utf-8')
    try:
        from cairosvg import svg2png
        file.write(svg2png(bytestring=_content))
        return True
    except Exception as e:
        file.write(_content)

        print(
            '[cairosvg] failed to create file, '
            'please install all the depedencies required!'
        )
        return False

def mk_md_html(file,content,conf:dict = {}):
    _content = content.encode('utf-8')
    try:
        import markdown
        file.write(markdown.markdown(content).encode('utf-8'))
        return True
    except Exception as e:
        file.write(_content)
        print(
            '[markdown] failed to create file, '
            'please install all the depedencies required!'
        )
        return False


def make(expect:str,into:str, file, content, conf:dict = {}):
    if   expect == "html" and into == 'pdf':
        return mk_html_pdf(file, content , conf )
    elif expect == 'svg'  and into == 'png':
        return mk_svg_png( file, content , conf )
    elif expect == 'md'   and into == 'html':
        return mk_md_html( file, content , conf )

    return False
