dopresskit-static
=================

dopresskit-static is a static version of the great [Rami Ismail's presskit()](https://github.com/ramiismail/dopresskit).

If you don't wan't to rely on PHP you can use it with the same xml files & directory structure as the original presskit().

You can even **host it on dropbox** : [demo](https://dl.dropboxusercontent.com/u/8211966/presskit-static/index.html)

# Features
* Not PHP
* More comprehensible source (thanks to python being python & the simple jinja syntax)
* Hostable on dropbox or anywhere with a simple drag & drop
* Compatible with the original presskit() xml files & directory structure
* Each non-filled xml tags will hide the appropriate section in the generated page

*Note : One thing you will lose from Vlambeer's version is the ability to make presskit requests through the server-side mail system.*

# Getting started
Go read the original [https://github.com/ramiismail/dopresskit](https://github.com/ramiismail/dopresskit) to see what presskit() is all about.

## Python environment
It requires python 2.7 (2.6 probably works as well) and the jinja2 package.

If you're on OSX/Linux you might already have a proper environment.

* Download python [https://www.python.org/download/releases/2.7.7/](https://www.python.org/download/releases/2.7.7/)
* Install the template engine **jinja2** with `easy_install jinja2` or `pip install jinja2` or even via the windows binary at [http://www.lfd.uci.edu/~gohlke/pythonlibs/#jinja2](http://www.lfd.uci.edu/~gohlke/pythonlibs/#jinja2) (`Jinja2‑2.7.3.win32‑py2.7.exe`)

## Generate your static files
You should be able to compile a project as is with the default `data.xml`.

* Run `python generate.py`, it will generate an `index.html` file at the root of your folder and in each of the project folders (by default, none).
* Open `index.html` and it's done!
* Edit the various `data.xml` files to your needs and run `python generate.py` again.

If you want to add a project, copy the `_template` folder and rename it, re generate the html files and a project should show up in the *Projects* section of the page.

*Note : A project folder will be ignored if its name is starting with an \_uppercase_, if containing any space and if not in lowercase. 'Super Crate Box' would have a folder named `super_crate_box` to be valid.*

## Google Analytics
To add google analytics support simply add your *Tracker ID* as an argument like this `python generate.py UA-1234567-89`
