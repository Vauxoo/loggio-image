Docker - logio.io
---

Streams the logs files mounted in the /logs volume to the logioserver

## Usage

### With docker-compose

- Change the user and pass in the compose file to your needs:

    AUTH_USER=user

    AUTH_PASS=pass

- Then change the volume to match the folder with the logs files you want to stream.

### Using the command line

    ```bash
    docker run -d --name logio_streamer -p 28777:28777 -p 28778:28778 -v /host/path:/logs vauxoo/logio 
    ```

**NOTE** : Remember tha in both cases you must define the auth credentials and the NODE env var.
