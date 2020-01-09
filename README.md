# Introduction
This repository contains a docker-based stackstorm setup that enables
passing authorized usernames via HTTP headers instead of WSGI
parameters.

# Why?
Most Single Sign On frameworks I've seen use a header
(e.g. X-Forwarded-User) to pass usernames to the backend, after the
authentication and authorization procedures. The backend accepts this
header and does what is needed to setup a session for this user.

The authentication backend from stackstorm does not accept these
headers. When ran in proxy mode, it assumes that the application
framework will send the username as a WSGI parameter to the
application.

In the docker setup, st2auth runs behind gunicorn. Gunicorn only
accepts HTTP connection and does not support custom transformations
from header to parameters. So, to accept usernames through headers,
some major modifications were needed.

# How?
Basically, we replace gunicorn with uwsgi and use nginx uwsgi
support to transform the incoming header to a uwsgi parameter. Uwsgi
is configured to run in master mode, with it's vassals living under
/etc/uwsgi/vassals.

We provide two vassals: st2auth and `auth_proxy`. The first vassal is
the gunicorn to uwsgi replacement and runs under a unix socket. The
second is needed to allow the internal tooling to login. The internal
stackstorm tools do not know how to cooperate with st2auth in proxy
mode. For instance, `st2 login <username>` will always try to do a
regular authentication request to `localhost:9100`. In proxy mode,
however, st2auth will not accept these requests. To get around this
issue, we created `auth_proxy`. This proxy accepts connection on
`localhost:9100` extracts the username and forwards this request to
reverse proxy for dispatching.

The last problem we encountered was the default stackstorm
webinterface. This interface assumes that the user provides a username
and password, unless a session cookie is set (or more accurately, a
session in the local browser storage). To circumvent this problem,
we've added a static `auth.html` page. This page is loaded by nginx if
no session cookie is found, instead of the default index page. This
page loads the session details from the st2auth backend, prepares the
local storage and cookies and, finally, reloads the page. Nginx
detects that a session is active via the auth cookie and loads the
normal index page, continuing the usual stackstorm flow.

# Understanding the source
To form a better understanding of how this all works together I advise
you to read the `Dockerfile` and the (last few blocks of) `st2.conf`
nginx configuration. These files give a broad overview of how this
solution works!
