FROM stackstorm/stackstorm:3.1

# Install uwsgi (with python plugin) and kerberos user
RUN apt update && apt-get install -y uwsgi-plugin-python

# Disable st2auth upstart init file
RUN echo manual > /etc/init/st2auth.override

# Prepare uwsgi and stackstorm hacks directory
RUN mkdir -p /etc/uwsgi/vassals /opt/stackstorm/hacks

# Change auth mode to proxy
RUN crudini --set /etc/st2/st2.conf auth mode proxy

# Remove default nginx conf, so localhost will also serve stackstorm
RUN rm -f /etc/nginx/conf.d/default.conf

# Install uwsgi vassals (slaves under the uwsgi emperor)
# We run st2auth and an auth_proxy as uwsgi vassals.
# Using this setup, we can transform authentication headers
# (X-Forwarded-User) in nginx to uwsgi parameters (required by
# st2auth). Internal stackstorm components only support standalone
# mode (basic auth). The auth proxy is a hack around this problem. It
# proxies all requests on the default st2auth port (9100) to the
# actual st2auth service, correcting requests where necessary, to
# support proxy mode.
COPY vassals/ /etc/uwsgi/vassals

# Install auth proxy
COPY auth_proxy.py /opt/stackstorm/hacks

# Install upstart init file for uwsgi
COPY uwsgi.init.conf /etc/init/uwsgi.conf

# Install modified nginx configuration
COPY st2.conf /etc/nginx/conf.d/st2.conf

# Ensure basic packs (core, default, linux, packs) are registered
COPY register_content.sh /st2-docker/entrypoint.d/

# Auth.html prepares the localStorage with an auth token, so the
# stackstorm front end knows that its logged in. This page will be
# loaded by the modified nginx configuration, if the auth-token cookie
# is not set. This hack is added to support SSO logins. It can be
# removed once stackstorm comes with support for this use case.
COPY auth.html /opt/stackstorm/static/webui/
