import re
import os.path
import sys
import urlparse
import xml.sax.handler

from jinja2 import Template, Environment, FileSystemLoader


# CONVERTS XML TO PYTHON OBJECT REPRESENTATION
# from http://code.activestate.com/recipes/534109-xml-to-python-data-structure/
def xml2obj(src):
    """
    A simple function to converts XML data into native Python object.
    """

    non_id_char = re.compile('[^_0-9a-zA-Z]')

    def _name_mangle(name):
        return non_id_char.sub('_', name)

    class DataNode(object):

        def __init__(self):
            self._attrs = {}    # XML attributes and child elements
            self.data = None    # child text data

        def __len__(self):
            # treat single element as a list of 1
            return 1

        def __getitem__(self, key):
            if isinstance(key, basestring):
                return self._attrs.get(key, None)
            else:
                return [self][key]

        def __contains__(self, name):
            return self._attrs.has_key(name)

        def __nonzero__(self):
            return bool(self._attrs or self.data)

        def __getattr__(self, name):
            if name.startswith('__'):
                # need to do this for Python special methods???
                raise AttributeError(name)
            return self._attrs.get(name, None)

        def _add_xml_attr(self, name, value):
            if name in self._attrs:
                # multiple attribute of the same name are represented by a list
                children = self._attrs[name]
                if not isinstance(children, list):
                    children = [children]
                    self._attrs[name] = children
                children.append(value)
            else:
                self._attrs[name] = value

        def __str__(self):
            return self.data or ''

        def __repr__(self):
            items = sorted(self._attrs.items())
            if self.data:
                items.append(('data', self.data))
            return u'{%s}' % ', '.join([u'%s:%s' % (k, repr(v)) for k, v in items])

    class TreeBuilder(xml.sax.handler.ContentHandler):

        def __init__(self):
            self.stack = []
            self.root = DataNode()
            self.current = self.root
            self.text_parts = []

        def startElement(self, name, attrs):
            self.stack.append((self.current, self.text_parts))
            self.current = DataNode()
            self.text_parts = []
            # xml attributes --> python attributes
            for k, v in attrs.items():
                self.current._add_xml_attr("caca" + _name_mangle(k), v)

        def endElement(self, name):
            text = ''.join(self.text_parts).strip()
            if text:
                self.current.data = text
            if self.current._attrs:
                obj = self.current
            else:
                # a text only node is simply represented by the string
                obj = text or ''
            self.current, self.text_parts = self.stack.pop()
            self.current._add_xml_attr(_name_mangle(name), obj)

        def characters(self, content):
            self.text_parts.append(content)

    builder = TreeBuilder()
    if isinstance(src, basestring):
        xml.sax.parseString(src, builder)
    else:
        xml.sax.parse(src, builder)
    return builder.root._attrs.values()[0]


# FUNCTIONS THAT JUST TALK
def blabla_ga():
    if ga is None:
        print ">>> Google analytics ID : Not found, skipping..."
        print "        Use 'python generate.py <Tracking ID> " + \
              "to activate google analytics"
    else:
        print "Google analytics : Enabled (ID: %s)" % (ga)


def blabla_projects():
    projects = get_projects()
    if len(projects) == 0:
        print ">>> No project found, skipping..."
        print "        Duplicate the '_template' folder, rename it " + \
              "and edit data.xml"
        print "        The project folder name must be lowercase " + \
              "and spaces by _underscores_."


###############################################################
# ACTUAL PRESSKIT STUFF
now_project = "."
ga = sys.argv[1] if len(sys.argv) == 2 else None
blabla_ga()


# HELPERS
def get_images(extensions, rejects=None):
    rejects = rejects or []
    files, images_path  = [], os.path.join(now_project, "images")
    try:
        os.mkdir(images_path)
    except OSError:  # Images folder already exists
        pass
    for f in os.listdir(images_path):
        _, ext = os.path.splitext(f)
        ext = ext[1:]
        if ext in extensions and f not in rejects:
            files.append(f)

    return files


def get_projects():
    projects = []
    for folder_name in os.listdir('.'):
        # FILTER OUT
        if os.path.isfile(folder_name):
            continue
        if ' ' in folder_name:
            continue
        if folder_name[0] == '_':
            continue
        if len([l for l in folder_name if l.isupper()]) > 0:
            continue

        # SEARCH FOR data.xml
        for f in os.listdir(folder_name):
            if f == "data.xml":
                projects.append(folder_name)
    return projects


def file_exists(filepath):
    return os.path.isfile(os.path.join(now_project, filepath))


def filesize(filepath):
    return os.path.getsize(os.path.join(now_project, filepath))


def parse_url(url):
    if url[:7] != "http://" and url[:8] != "https://":
        url = "http://" + url
    return url

def clean_url(url):
    if url.startswith("http://"):
        url = url[7:]
    if url.startswith("https://"):
        url = url[8:]
    if url.startswith("www."):
        url = url[4:]
    return url.rstrip('/')

def get_site(url):
    parsed_url = urlparse.urlparse(url)
    if parsed_url.netloc == '' and parsed_url.scheme == '':
        parsed_url = urlparse.urlparse("//" + url)
    site = parsed_url.netloc
    if site.startswith("www."):
        site = site[4:]
    return site

env = Environment(loader=FileSystemLoader(""))
env.filters['clean_url'] = clean_url
env.filters['get_site'] = get_site


def do_compile(project_name, company_datas=None):
    global now_project
    now_project = project_name

    # CLEAN XML FROM DASHES
    def undash(match):
        return match.group().replace("-", "_")

    xml_datas = open(os.path.join(project_name, 'data.xml'), 'r')
    regex = re.compile('\<[^?!].*?\>')
    xml_datas = regex.sub(undash, xml_datas.read())

    # PARSE
    xml_obj = xml2obj(xml_datas)

    # DETECT LAYOUT NAME
    if project_name == ".":
        layout_name = "layout_company.html"
    else:
        layout_name = "layout_project.html"

    if project_name == ".":
        company_datas = xml_obj

    # WRITE ON DISK
    t = env.get_template(layout_name)
    output = t.render(
        company=company_datas, project=xml_obj, common=xml_obj,
        file_exists=file_exists, filesize=filesize,
        get_images=get_images, get_projects=get_projects, google_analytics=ga,
        parse_url=parse_url)

    path = os.path.join(project_name, "index.html")
    with open(path, "wb") as fh:
        fh.write(output.encode('utf-8'))

    print ">>> generated : " + path
    return xml_obj


# COMPILE COMPANY PAGE
company_datas = do_compile(".")
# COMPILE ALL PROJECT PAGES
for project in get_projects():
    do_compile(project, company_datas)
blabla_projects()
