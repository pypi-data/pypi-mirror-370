# Pling Publisher
Tool to upload to [gnome-look.org](https://gnome-look.org), [store.kde.org](https://store.kde.org), [www.pling.com](https://https://www.pling.com/).

![Build Status](https://github.com/dmzoneill/pling-publisher/actions/workflows/main.yml/badge.svg)


You can find this python module on [https://pypi.org/project/pling-publisher/](https://pypi.org/project/pling-publisher/)


## Install
```console
pip install pling-publisher
```

## How to use
```console
pling build # build an archive from the current folder.
pling publish --username <USERNAME> --password <PASSWORD> --project-id <PROJECT_ID> --file <PATH>
pling --help # for help :)
```

You can also provide your username, password and project_id via environment variables (PLING_USERNAME, PLING_PASSWORD, PLING_PROJECT_ID).


## Support
Feel free to submit a pull request.
