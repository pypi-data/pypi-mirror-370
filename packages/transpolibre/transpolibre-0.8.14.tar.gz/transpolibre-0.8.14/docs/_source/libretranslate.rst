==============
LibreTranslate
==============
transpolibre uses a LibreTranslate server for translations.

* https://libretranslate.com/
* https://github.com/LibreTranslate/LibreTranslate

Local Server
============
You can run your own LibreTranslate server.

Server Installation
-------------------
To install your own server, you can do it thusly on Debian:

.. code-block:: bash

  sudo apt install python3-venv python-is-python3
  mkdir libretranslate
  cd libretranslate/
  python -m venv venv
  source venv/bin/activate
  pip install -U setuptools pip wheel
  pip install libretranslate

Note, the first time it is run, it will download the translation models.
The web URL won't be available until this is complete.
It will download (currently) approximately 9 gigs of data.

Translation model files download to here:

.. code-block:: bash

  ~/.local/share/argos-translate/packages

systemd
-------
You can set up the server to start on boot with systemd.
It will need a startup script and a systemd file.

Edit the systemd service file:

.. code-block:: bash

  ${EDITOR} /etc/systemd/system/libretranslate.service

Add contents such as this, adjusting path and user to where you put the
startup script:

.. code-block:: bash

  [Unit]
  Description=LibreTranslate
  After=network-online.target
  Wants=network-online.target
  
  [Service]
  ExecStart=/usr/local/bin/libretranslate-start
  WorkingDirectory=/tmp
  User=debian
  Group=debian
  Restart=no
  ExecReload=/bin/kill -HUP $MAINPID
  
  [Install]
  WantedBy=multi-user.target

Create the startup script:

.. code-block:: bash

  ${EDITOR} /usr/local/bin/libretranslate-start

Add contents such as this, adjusting to the correct path:

.. code-block:: bash

  #!/bin/bash
  
  cd /home/debian/libretranslate
  
  source venv/bin/activate
  
  libretranslate \
    --host 0.0.0.0 \
    --port 8000 \
    --frontend-language-source en \
    --frontend-language-target es \
    --update-models

Web Access
----------
You can then access your model remotely via the server's IP
or from localhost, such as:

* http://localhost:8000/
* http://192.168.1.1:8000

