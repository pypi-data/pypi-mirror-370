def build_url(domain, port, username, password, protocol="https") -> str:
    endpoint = domain
    if port is not None:
        endpoint = f"{domain}:{port}"

    if password is None:
        return f"{protocol}://{endpoint}"
    else:
        return f"{protocol}://{username}:{password}@{endpoint}"


def build(http, https) -> dict:
    result = {}
    if http is not None:
        result['http'] = http
    if https is not None:
        result['https'] = https
    return result
