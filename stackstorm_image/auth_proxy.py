import httplib


def application(env, start_response):
  headers = {k[len("HTTP_"):].title().replace("_", "-"): v
             for k, v in env.items()
             if k.startswith("HTTP_")}

  if env["REQUEST_URI"] == "/tokens" and "HTTP_AUTHORIZATION" in env:
    encoded_user = env["HTTP_AUTHORIZATION"].split(" ")[1]
    username, _ = encoded_user.decode("base64").split(":")
    env["REQUEST_METHOD"] = "POST"
    cookies = env.get("Cookie", "")
    headers.update({"X-Forwarded-User": username,
                    "X-Real-Ip": "127.0.0.1",
                    "Content-Type": "application/json",
                    "Cookie": cookies + ("; " if cookies else "") + "auth-token="})

  conn = httplib.HTTPConnection("localhost")
  conn.request(env["REQUEST_METHOD"], "/auth" + env["REQUEST_URI"], headers=headers)

  resp = conn.getresponse()
  data = resp.read()
  conn.close()

  start_response("{} {}".format(resp.status, resp.reason), resp.getheaders())

  return data
