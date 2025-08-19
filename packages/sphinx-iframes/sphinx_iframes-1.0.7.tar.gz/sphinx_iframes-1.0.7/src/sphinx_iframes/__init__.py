from __future__ import annotations

import os

from docutils.parsers.rst import directives

from docutils import nodes

from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from typing import Optional

from sphinx.directives.patches import Figure

YOUTUBE_OPTIONS = [
    "autoplay","cc_lang_pref","cc_load_policy","color","controls","disablekb","enablejsapi","end","fs","hl","iv_load_policy","list","listType","loop","modestbranding","origin","playlist","playsinline","rel","start","widget_referrer"
]

def generate_style(width: Optional[str], height: Optional[str],aspectratio: Optional[str],stylediv: Optional[str]):

     styles = ''

     if width:
          styles += f'width: {width};'

     if height:
          styles += f'height: {height};'
     
     if aspectratio:
          styles += f'aspect-ratio: {aspectratio};'

     if stylediv:
         styles += stylediv

     return styles

class IframeDirective(SphinxDirective):
    has_content = False
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        'class': directives.class_option,
        "height": directives.unchanged,
        "width": directives.unchanged,
        "aspectratio": directives.unchanged,
        "stylediv": directives.unchanged,
        "styleframe": directives.unchanged,
        "divclass": directives.class_option
    }

    def run(self) -> list[nodes.Node]:

        assert self.arguments[0] is not None

        iframe_html = generate_iframe_html(self)

        iframe_node = nodes.raw(None, iframe_html, format="html")
        # paragraph_node = nodes.paragraph()
        # paragraph_node.insert(0, iframe_node)

        return [iframe_node]

def generate_iframe_html(source):

    div_class = source.options.get("divclass", None)
    if div_class is not None:
        div_class = " ".join(div_class) if isinstance(div_class, list) else str(div_class)
    else:
        div_class = ""
    iframe_class = source.options.get("class")

    if source.name == "h5p":
        base_class = "sphinx h5p blend"
        if iframe_class is not None:
            if "no-blend" in iframe_class:
                base_class = "sphinx h5p"        
    elif source.name == "video":
        base_class = "sphinx video no-blend"
        if iframe_class is not None:
            if "blend" in iframe_class and "not-blend" not in iframe_class:
                base_class = "sphinx video"
    else:
            base_class = "sphinx"

    if iframe_class is None:
        iframe_class = base_class
    elif isinstance(iframe_class, list):
        iframe_class = base_class+" "+" ".join(iframe_class)
    else:
        iframe_class = base_class+""+str(iframe_class)
    
    if source.name == 'h5p':
        style = generate_style(
            None, None,"auto",None
        )
        check_style = style
    else:
        style = generate_style(
            source.options.get("width", None), source.options.get("height", None),source.options.get("aspectratio",None),source.options.get("stylediv",None)
        )
        check_style = generate_style(
            source.options.get("width", None), source.options.get("height", None),source.options.get("aspectratio",None),None
        )
    if style != '':
        style = 'style="%s"'%(style)
    if ('width' in check_style) or ('height' in check_style) or ('aspect-ratio' in check_style):
        add_user = True
    else:
        add_user = False
    frame_style = source.options.get("styleframe",None)
    if frame_style is not None:
        frame_style = 'style="%s"'%(frame_style)

    # load source and check for validity
    url = source.arguments[0]
    if 'youtube' in url:
        if 'watch?' in url:
            tail = url[1+url.find('?'):]
            list_index = tail.find('list=PL')
            if list_index>0: # so list found and not a the beginning
                # add a & before list if it is not present
                if tail[list_index]!='&':
                    tail = tail[:list_index] + '&' + tail[list_index:]
            video = ''
            options = []
            tail = tail.split('&')
            for combo in tail:
                opt = combo.split('=')
                if opt[0]=='v':
                    video = opt[1]
                elif opt[0]=='t':
                    options.insert(0,'start='+opt[1])
                elif opt[0] in YOUTUBE_OPTIONS:
                    options.append(combo)
            options = ';'.join(options)

            url = 'https://www.youtube.com/embed/'+video+'?'+options
    if 'youtu.be' in url:
        tail = url[1+url.find('?'):]
        if list_index>0: # so list found and not a the beginning
            # add a & before list if it is not present
            if tail[list_index]!='&':
                tail = tail[:list_index] + '&' + tail[list_index:]
        base_video = url[:url.find('?')]
        base_video = base_video.replace('.be','be.com/embed')
        options = []
        tail = tail.split('&')
        for combo in tail:
            opt = combo.split('=')
            if opt[0]=='v':
                video = opt[1]
            elif opt[0]=='t':
                options.insert(0,'start='+opt[1])
            elif opt[0] in YOUTUBE_OPTIONS:
                options.append(combo)
        options = ';'.join(options)

        url = base_video+'?'+options

    # Handle H5P URLs - add /embed if not present
    if source.name == 'h5p':
        if '/embed' not in url and url.endswith('/'):
            url = url + 'embed'
        elif '/embed' not in url and not url.endswith('/'):
            url = url + '/embed'

    if source.name == "video":
        if add_user:
            iframe_html = '<div class="video-container user %s" %s>\n'%(div_class, style)
        else:
            iframe_html = '<div class="video-container %s" %s>\n'%(div_class, style)
        iframe_html += f"""
            <iframe class="{iframe_class}" {frame_style} src="{url}" allow="fullscreen *;autoplay *; geolocation *; microphone *; camera *; midi *; encrypted-media *" frameborder="0"></iframe>
        """
        iframe_html += '\n</div>'
    elif source.name == 'h5p':
        if add_user:
            iframe_html = '<div class="iframe-container user %s" %s>\n'%(div_class, style)
        else:
            iframe_html = '<div class="iframe-container %s" %s>\n'%(div_class, style)
        iframe_html += f"""
            <iframe class="{iframe_class}" {frame_style} src="{url}" allow="fullscreen *;autoplay *; geolocation *; microphone *; camera *; midi *; encrypted-media *" frameborder="0"></iframe>
        """
        iframe_html += '\n</div>'
    else:
        if add_user:
            iframe_html = '<div class="iframe-container user %s" %s>\n'%(div_class, style)
        else:
            iframe_html = '<div class="iframe-container %s" %s>\n'%(div_class, style)
        iframe_html += f"""
            <iframe class="{iframe_class}" {frame_style} src="{url}" allow="fullscreen *;autoplay *; geolocation *; microphone *; camera *; midi *; encrypted-media *" frameborder="0"></iframe>
        """
        iframe_html += '\n</div>'

    return iframe_html
    
    
def include_js(app: Sphinx):
     
     if app.config.iframe_h5p_autoresize:
          app.add_js_file("h5p-resizer.js") # to support auto-width for h5p

     return

def setup(app: Sphinx):

    app.add_directive("iframe", IframeDirective)
    app.add_directive("h5p", IframeDirective)
    app.add_directive("video", IframeDirective)
    app.add_directive("iframe-figure", IframeFigure)

    app.add_config_value("iframe_h5p_autoresize",True,'env')
    app.connect('builder-inited',include_js)

    app.add_config_value("iframe_blend",True,'env')
    app.add_config_value("iframe_saturation",1.5,'env')
    app.add_config_value("iframe_background","#ffffff",'env')
    app.add_config_value("iframe_width","calc(100% - 2.8rem)",'env')
    app.add_config_value("iframe_aspectratio","auto 2 / 1",'env')
    
    app.add_css_file('sphinx_iframe.css')

    app.connect("build-finished",write_css)
    app.connect("build-finished",write_js)

    return

def write_css(app: Sphinx,exc):
    # now set the CSS
    CSS_content = "div.video-container {\n\tbox-sizing: border-box;\n}\n\n"
    CSS_content += "div.video-container:not(.user) {\n\twidth: %s;\n\taspect-ratio: auto 16 / 9;\n}\n\n"%(app.config.iframe_width)
    CSS_content += "iframe.sphinx.video {\n\twidth: 100%;\n\theight: 100%;\n\tbox-sizing: border-box;\n}\n\n"
    CSS_content += "div.iframe-container {\n\tbox-sizing: border-box;\n}\n\n"
    CSS_content += "div.iframe-container:not(.user) {\n\twidth: %s;\n\taspect-ratio: %s;\n}\n\n"%(app.config.iframe_width,app.config.iframe_aspectratio)
    CSS_content += "div.iframe-container > iframe:not(.h5p) {\n\twidth: 100%;\n\theight: 100%;\n\tbox-sizing: border-box;\n}\n\n"
    
    # add blend or no-blend option if required
    if app.config.iframe_blend:
        CSS_content += "iframe.sphinx:not(.no-blend) {\n\tbackground: transparent;\n\tmix-blend-mode: darken;\n}\n\n" # blend all except no-blend
        CSS_content += "html[data-theme=dark] iframe.sphinx:not(.no-blend) {\n\tfilter: invert(1) hue-rotate(180deg) saturate(%s);\n\tbackground: transparent;\n\tmix-blend-mode: lighten;\n}\n\n"%(app.config.iframe_saturation) # blend all except no-blend
        CSS_content += "iframe.sphinx.no-blend:not(.video) {\n\tbackground: %s;\n\tborder-radius: .25rem;\n}\n\n"%(app.config.iframe_background)
        CSS_content += "iframe.sphinx.no-blend.video {\n\tbackground: transparent;\n\tborder-radius: .25rem;\n}\n"
    else:
        CSS_content += "iframe.sphinx.blend {\n\tbackground: transparent;\n\tmix-blend-mode: darken;\n}\n\n" # blend none except blend
        CSS_content += "html[data-theme=dark] iframe.sphinx.blend {\n\tfilter: invert(1) hue-rotate(180deg) saturate(%s);\n\tbackground: transparent;\n\tmix-blend-mode: lighten;\n}\n\n"%(app.config.iframe_saturation) # blend none except blend
        CSS_content += "iframe.sphinx:not(.blend):not(.video) {\n\tbackground: %s;\n\tborder-radius: .25rem;\n}\n\n"%(app.config.iframe_background)
        CSS_content += "iframe.sphinx:not(.blend).video {\n\tbackground: transparent;\n\tborder-radius: .25rem;\n}\n\n"
    
    # write the css file
    staticdir = os.path.join(app.builder.outdir, '_static')
    filename = os.path.join(staticdir,'sphinx_iframe.css')
    with open(filename,"w") as css:
        css.write(CSS_content)

    return

def write_js(app: Sphinx,exc):
    if app.config.iframe_h5p_autoresize:
        JS_content = """
            // H5P iframe Resizer
            (function () {
            if (!window.postMessage || !window.addEventListener || window.h5pResizerInitialized) {
                return; // Not supported
            }
            window.h5pResizerInitialized = true;

            // Map actions to handlers
            var actionHandlers = {};

            /**
            * Prepare iframe resize.
            *
            * @private
            * @param {Object} iframe Element
            * @param {Object} data Payload
            * @param {Function} respond Send a response to the iframe
            */
            actionHandlers.hello = function (iframe, data, respond) {
                // Make iframe responsive
                iframe.style.width = '100%';

                // Bugfix for Chrome: Force update of iframe width. If this is not done the
                // document size may not be updated before the content resizes.
                iframe.getBoundingClientRect();

                // Tell iframe that it needs to resize when our window resizes
                var resize = function () {
                if (iframe.contentWindow) {
                    // Limit resize calls to avoid flickering
                    respond('resize');
                }
                else {
                    // Frame is gone, unregister.
                    window.removeEventListener('resize', resize);
                }
                };
                window.addEventListener('resize', resize, false);

                // Respond to let the iframe know we can resize it
                respond('hello');
            };

            /**
            * Prepare iframe resize.
            *
            * @private
            * @param {Object} iframe Element
            * @param {Object} data Payload
            * @param {Function} respond Send a response to the iframe
            */
            actionHandlers.prepareResize = function (iframe, data, respond) {
                // Do not resize unless page and scrolling differs
                if (iframe.clientHeight !== data.scrollHeight ||
                    data.scrollHeight !== data.clientHeight) {

                // Reset iframe height, in case content has shrinked.
                iframe.style.height = data.clientHeight + 'px';
                respond('resizePrepared');
                }
            };

            /**
            * Resize parent and iframe to desired height.
            *
            * @private
            * @param {Object} iframe Element
            * @param {Object} data Payload
            * @param {Function} respond Send a response to the iframe
            */
            actionHandlers.resize = function (iframe, data) {
                // Resize iframe so all content is visible. Use scrollHeight to make sure we get everything
                iframe.style.height = data.scrollHeight + 'px';
            };

            /**
            * Keyup event handler. Exits full screen on escape.
            *
            * @param {Event} event
            */
            var escape = function (event) {
                if (event.keyCode === 27) {
                exitFullScreen();
                }
            };

            // Listen for messages from iframes
            window.addEventListener('message', function receiveMessage(event) {
                if (event.data.context !== 'h5p') {
                return; // Only handle h5p requests.
                }

                // Find out who sent the message
                var iframe, iframes = document.getElementsByTagName('iframe');
                for (var i = 0; i < iframes.length; i++) {
                if (iframes[i].contentWindow === event.source) {
                    iframe = iframes[i];
                    break;
                }
                }

                if (!iframe) {
                return; // Cannot find sender
                }

                // Find action handler handler
                if (actionHandlers[event.data.action]) {
                actionHandlers[event.data.action](iframe, event.data, function respond(action, data) {
                    if (data === undefined) {
                    data = {};
                    }
                    data.action = action;
                    data.context = 'h5p';
                    event.source.postMessage(data, event.origin);
                });
                }
            }, false);

            // Let h5p iframes know we're ready!
            var iframes = document.getElementsByTagName('iframe');
            var ready = {
                context: 'h5p',
                action: 'ready'
            };
            for (var i = 0; i < iframes.length; i++) {
                if (iframes[i].src.indexOf('h5p') !== -1) {
                iframes[i].contentWindow.postMessage(ready, '*');
                }
            }

            })();
            """
        # write the css file
        staticdir = os.path.join(app.builder.outdir, '_static')
        filename = os.path.join(staticdir,'h5p-resizer.js')
        with open(filename,"w") as js:
            js.write(JS_content)

class IframeFigure(Figure):
    option_spec = Figure.option_spec.copy()
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec.update(
        {
            'class': directives.class_option,
            "height": directives.unchanged,
            "width": directives.unchanged,
            "aspectratio": directives.unchanged,
            "stylediv": directives.unchanged,
            "styleframe": directives.unchanged
        }
    )
    
    def run(self):
        label = self.options.pop('label', None)
        if label is not None:
            self.options.set('name', label)
        (figure_node,) = Figure.run(self)
        iframe_html = generate_iframe_html(self)
        iframe_node = nodes.raw(None, iframe_html, format="html")
        figure_node[0] = iframe_node

        return [figure_node]
