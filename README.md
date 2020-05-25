# Pubit

Flask app -  public your folders with http.

## Installation

Linux:
```
$ git clone https://github.com/zhazh/pubit.git
$ cd pubit
$ python -m venv env
$ source env/bin/activate
(env)$ pip install -r requirements.txt
```

Windows:
```
> git clone https://github.com/zhazh/pubit.git
> cd pubit
> python -m venv env
> env\Scripts\activate
(env) > pip install -r requirements.txt
```

## Configuration

Create .env file in project root directory, in linux you can do this like:
```
$ cat > .env << EOF
> SECRET_KEY=536f8c98b8f440809cf709fa731c90e6
> ADMIN_NAME=xxx
> ADMIN_PASSWORD=xxx
> EOF
```

## Run

Linux:
```
$ gunicorn --workers=3 --bind=0.0.0.0:5000 wsgi:app
```

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
