# pugdebug

pugdebug is (well, should be) a PHP standalone debugger.

A python 3.4.x, pyqt5 project.

# setting up the environment

The main dependencies are Python 3.4,
[QT5.4](http://doc.qt.io/qt-5/gettingstarted.html),
[SIP4.6](http://www.riverbankcomputing.com/software/sip/download)
and [PyQt5.4](http://www.riverbankcomputing.com/software/pyqt/download5).

I wrote a [blog post](http://robertbasic.com/blog/install-pyqt5-in-python-3-virtual-environment)
about setting up a virtual environment for it.

Clone this repo and after setting up the virtual environment simply doing a
`python app.py` should start up pugdebug.

[@ihabunek](https://github.com/ihabunek) and [@vranac](https://github.com/vranac)
report that this process is pretty painless on Ubuntu and OSX machines. Some
package names might differ from what I used, but a document explaining the venv
setup process on different systems should be available soon.

Do note that I'm trying to figure out how to build executables for this beast.

# setting up xdebug

To be able to debug PHP with pugdebug, you need to have [xdebug](http://xdebug.org/docs/remote)
propely set up for remote debugging.

A minimal configuration would be something like:

```
xdebug.idekey=netbeans-xdebug
xdebug.remote_enable=1
xdebug.remote_port=9000
xdebug.remote_host=127.0.0.1
```

If the project you want to debug is in a vagrant virtual machine, your xdebug
config should be something like:

```
xdebug.idekey=netbeans-xdebug
xdebug.remote_enable=1
xdebug.remote_port=9000
xdebug.remote_connect_back=1
```

Do note that pugdebug's settings are hardcoded at the moment so it's always
port 9000. This will change in the future.

# using pugdebug

In a terminal go to the directory where you have pugdebug cloned and start it by
issuing a `python app.py` command.

On the left side you can see a simple file browser that should list your home
directory.

Under it is an input field with the label `Root:`, containing the path to your
home directory.

By entering a new root path in the `root` input field will change the root
directory of the file browser.

For example, on my laptop it starts with `/home/robert` and the file browser
lists my home directory. If I enter `/home/robert/www/pugdebug` into the `root`
input field, the file browser will change to the pugdebug web project.

But this is just temporary, it will be nicer in the future.

# debugging sessions

To start a debugging session, click the "Start" button in the top left corner.

Load your web project in your browser and start a
[HTTP debugging session](http://xdebug.org/docs/remote#browser_session).

pugdebug should pick up that session and display the index file of your web
project, while stopping the execution on the first line.

Using the `Run`, `Over`, `In`, `Out` continuation commands you can step through
your PHP code.

Setting breakpoints is possible by double clicking the line where a breakpoint
should be placed.

The correspoding line number should be highlighted and a new breakpoint should
be listed in the breakpoint viewer (bottom right corner).

Double clicking the line with a breakpoint should remove that breakpoint.

## debugging cli scripts

It is also possible to debug CLI scripts with pugdebug.

Start pugdebug as stated in the previous section, click `Start` to
start a debugging session and then in a second terminal type:

```
export XDEBUG_CONFIG="idekey=netbeans-xdebug"
```

(or whatever you set the `xdebug.idekey` setting to) and then start
your PHP CLI script normally:

```
php script.php
```

pugdebug should pick up the debugging session and let you debug your script.

# executables

I'm trying to make executables with
[pyqtdeploy](http://www.riverbankcomputing.com/software/pyqtdeploy/download).
So far I managed to create one for Fedora 21.

# todo

Take a look at the [issue tracker](https://github.com/robertbasic/pugdebug/issues).

# contributions

Contributions are more than welcome! Report bugs, tell me your ideas and needs,
write code, test it on different platforms ...
