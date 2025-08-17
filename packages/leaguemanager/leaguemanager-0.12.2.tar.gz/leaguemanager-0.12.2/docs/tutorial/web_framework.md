(building-web-app)=
# Build A Web App

You can use League Manager from within a web application like [Litestar](https://litestar.dev), [Flask](https://flask.palletsprojects.com/en/stable/), or [FastAPI](https://fastapi.tiangolo.com).

For this tutorial, I will be using Litestar, but the same concepts can be applied with other frameworks.

(installing-litestar)=
## Installing Litestar

:::{important}
Each time terminal commands are used, it is with the expectation that your virtual environment [has been activated](#using-virtual-environment).
:::

To install Litestar, use this command:

```shell
python -m pip install litestar[standard]
```

Adding `[standard]` to the `litestar` package ensures that a few additional dependencies are installed, including the `uvicorn` web server that will allow you to serve you application

(app-structure)=
## App Structure

Up to this point, you don't have much in your `new-project` directory, outside of the `.venv` virtual environment directory.

Ordinarily, you'll want to include a few more files in your project root that might include `.gitignore`, `pyproject.toml`, and/or a `requirements.txt` file.

None of these are _required_ to build your application, but they generally become **extremely** important for a maturing project.

For now, we will skip these optional files.

(source-directory)=
### Source Directory

While you are in the `new-project` directory, you _could_ create a `.py` file here and start building your app, but again, for a maturing project, that is not the best idea.

Instead, let's create a directory called `app` where we will start building our Python modules.

:::{hint}
A _module_ refers to any Python file that contains definitions and statements. Or in other words, a file that ends in `.py`
:::

Create an `app` directory:

```shell
# create the directory
mkdir app

# change into that directory
cd app
```

Now it's time to start creating some files.

You _could_ use a simple text editor to create these files, but by this point, it's likely better to start using a code editor or IDE (integrated development environment) if you're not using one already.

(first-module)=
### First Module

Create a file in your `app` directory and call it `main.py`.

And while you're at it, create another file and call it `__init__.py`.

You're ordinarily going to create a blank `__init__.py` in any directory within the `app`. Python uses the `__init__.py` file to treat that directory as a _package_.

Now, open the main.py file and create a minimal Litestar application.

```python
# new-project/app/main.py

from litestar import Litestar, get


@get("/")
async def hello_world() -> str:
    return "Hello, world!"


app = Litestar([hello_world])
```

This is the most basic web app you could build. Though not very practical, it serves as the foundation to your application.

In order to see it working, open up your terminal and **navigate once again** to your `new-project` directory.

Type `litestar run` into the terminal. This command _serves_ the application locally on your machine.

:::{attention}
:class: dropdown
When using the terminal, it is important to remember _where you are_ in the directory. Some commands you type might have expectations of what is or isn't located within certain directories, relative to where you are (or your _current working directory_). If you were to try the command `litestar run` while in the `app` directory, the command would not _find_ the Litestar instance.
:::

You can now visit http://127.0.0.1:8000 in your web browser and you'll see the message written at the top of the browser screen.
