Manage your application services and parallelize start and stop.


Quickstart
==========


Define your services classes and commands
-----------------------------------------

```python
from servicectl import service, command

class myservice(service):

    dependencies = (
        "myproject.myotherservice:myotherservice",
    )

    @command()
    def start(self):
        # Magic stuff to start your demon
        return True/False

    @command()
    def stop(self):
        # Magic stuff to stop your demon
        return True/False
```


Package all your services in a python package
---------------------------------------------

```python
from servicectl.setup import setup

setup(
    name="myproject",
    packages=find_packages(),
)
```


Install your services package
-----------------------------

```bash
python setup.py install
```


And endjoy
----------

```bash
myproject.myservice start
```

```bash
myproject.myservice stop
```


Examples
========

Mapserver
---------

Small example of mapproxy server using redis cache served by nginx server.

[link](examples/mapproxy)


Django
------

Skeleton of django project using a postgres database and nginx.

[link](examples/django)
