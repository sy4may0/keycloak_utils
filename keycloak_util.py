import requests
import pprint

test_param = {
    'host': "localhost",
    'port': 8050,
    'user': 'admin',
    'pass': 'admin#admin#',
}

def accipere_token(host, port, user, password):
    url = f"http://{host}:{port}/realms/master/protocol/openid-connect/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "client_id": "admin-cli",
        "username": user,
        "password": password,
        "grant_type": "password"
    }
    response = requests.post(url, headers=headers, data=data)

    response.raise_for_status()
    return response.json()['access_token']

def creare_realm(token, host, port, realm_name):
    url = f"http://{host}:{port}/admin/realms"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    realm_payload = {
        "realm": realm_name,
        "enabled": True
    }
    
    response = requests.post(
        url,
        headers=headers,
        json=realm_payload
    )

    if response.status_code == 201:
        return True
    elif response.status_code == 409:
        return False
    else:
        raise Exception(f"Failed to create realm: {response.text}")

def renovare_realm(token, host, port, realm_name, key, value):
    try:
        asserere_realm_config(
            token, host, port, realm_name, key, value
        )
        return False
    except AssertionError:
        pass

    url = f"http://{host}:{port}/admin/realms/{realm_name}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    payload = {
        key: value
    }

    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 204:
        return True
    else:
        raise Exception(
            f"Failed to update realm ({response.status_code}): {response.text}"
        )

def creare_ldap_provider(
    token, host, port, realm_name,
    name, config
):
    url = f"http://{host}:{port}/admin/realms/{realm_name}/components"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    realm_id = accipere_realm_id(
        token, host, port, realm_name
    )
    
    payload = {
        "name": name,
        "providerId": "ldap",
        "providerType": "org.keycloak.storage.UserStorageProvider",
        "parentId": realm_id,
        "config": config
    }

    exists = accipere_ldap_provider(
        token, host, port, realm_name, name
    )

    if len(exists) > 0:
        return False

    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 201:
        return True
    else:
        raise Exception(f"Failed to create LDAP provider: {response.text}")

def renovare_ldap_provider(
    token, host, port, realm_name,
    name, key, value
):
    try:
        asserere_ldap_provider_config(
            token, host, port, realm_name, name,
            key, value
        )
        return False
    except AssertionError:
        pass

    component_id = accipere_ldap_provider_id(
        token, host, port, realm_name, name
    )

    url = f"http://{host}:{port}/admin/realms/{realm_name}/components/{component_id}"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    current = requests.get(url, headers=headers)
    current.raise_for_status()
    obj = current.json()

    if isinstance(value, bool):
        v = "true" if value else "false"
    else:
        v = str(value)

    obj.setdefault("config", {})
    obj["config"][key] = [v]


    resp = requests.put(url, headers=headers, json=obj)
    if resp.status_code in (204, 200):
        return True

    raise Exception(f"Failed to update component ({resp.status_code}): {resp.text}")

def accipere_realm_id(token, host, port, realm_name):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
 
    realm_resp = requests.get(f"http://{host}:{port}/admin/realms/{realm_name}", headers=headers)
    realm_resp.raise_for_status()
    realm_id = realm_resp.json()["id"]
    return realm_id

def accipere_realm(token, host, port, realm_name):
    url = f"http://{host}:{port}/admin/realms/{realm_name}"

    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    return response.json()

def accipere_ldap_provider(token, host, port, realm_name, component_name):
    url = f"http://{host}:{port}/admin/realms/{realm_name}/components"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    realm_id = accipere_realm_id(
        token, host, port, realm_name
    )
 

    params = {
        "name": component_name,
        "parent": realm_id,
        "type": "org.keycloak.storage.UserStorageProvider" 
    }
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def accipere_ldap_provider_id(
    token, host, port, realm_name, component_name
):
    components = accipere_ldap_provider(
        token, host, port, realm_name, component_name
    )
    if len(components) == 0:
        raise Exception(f"component {realm_name}:{component_name} not found")
    elif len(components) != 1:
        raise Exception(f"Duplicate component {realm_name}:{component_name} found")

    return components[0]['id']

def asserere_realm_exists(
    token, host, port, realm_name
):
    url = f"http://{host}:{port}/admin/realms/{realm_name}"

    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
         raise AssertionError(f"Realm {realm_name} does not exist")

    response.raise_for_status()

def asserere_realm_config(
    token, host, port, realm_name,
    key, value
):
    conf = accipere_realm(token, host, port, realm_name)
    if not key in conf:
        raise AssertionError(f"Invalid key found. {key} not found in config")
    if not conf[key] == value:
        raise AssertionError(f"Invalid realm config. {key}: Expected: {value} Actual: {conf[key]}")

def asserere_ldap_provider_exists(
    token, host, port, realm_name, component_name,
):
    components = accipere_ldap_provider(
        token, host, port, realm_name, component_name
    )
    if not len(components) >= 1:
        raise AssertionError(f"No ldap provider. Cannot find {realm_name}:{component_name}.")

def asserere_ldap_provider_config(
    token, host, port, realm_name, component_name,
    key, value
):
    components = accipere_ldap_provider(
        token, host, port, realm_name, component_name
    )
    if not len(components) >= 1:
        raise AssertionError(f"No ldap provider. Cannot find {realm_name}:{component_name}.")
    if not len(components) == 1:
        raise AssertionError(f"Duplicate ldap provider. Not supported.")

    config = components[0]['config']

    if not key in config:
        raise AssertionError(f"No config key found. key={key}.")

    if isinstance(value, bool):
        v = "true" if value else "false"
    else:
        v = str(value)

    if not config[key] == [v]:
        raise AssertionError(f"Invalid provider config. {key}: Expected: {[v]} Actual: {config[key]}")


if __name__ == "__main__":
    token = accipere_token(
        test_param['host'],
        test_param['port'],
        test_param['user'],
        test_param['pass']
    )

    print(token)

    creare_realm(
        token, test_param['host'], test_param['port'],
        'test_realm_01'
    )

    realm_conf = accipere_realm(
        token, test_param['host'], test_param['port'],
        'test_realm_01'
    )

    asserere_realm_config(
        token, test_param['host'], test_param['port'],
        'test_realm_01', "internationalizationEnabled", True
    )
    asserere_realm_config(
        token, test_param['host'], test_param['port'],
        'test_realm_01', "supportedLocales", ['ja', 'en']
    )
    asserere_realm_config(
        token, test_param['host'], test_param['port'],
        'test_realm_01', "defaultLocale", 'ja'
    )

    print(accipere_realm_id(
        token, test_param['host'], test_param['port'],
        'master'
    ))
    creare_ldap_provider(
        token, test_param['host'], test_param['port'],
        'master', 'my-ldap', {}
    )
    asserere_ldap_provider_config(
        token, test_param['host'], test_param['port'],
        'master', 'my-ldap', 
        'bindDn', 'cn=manager,dc=example,dc=com'
    )
    asserere_ldap_provider_config(
        token, test_param['host'], test_param['port'],
        'master', 'my-ldap', 
        'editMode', 'WRITABLE'
    )
    result = renovare_realm(
        token, test_param['host'], test_param['port'],
        'master', "internationalizationEnabled", True
    )
    print(result)

    result = renovare_ldap_provider(
        token, test_param['host'], test_param['port'],
        'master', 'my-ldap',
        "editMode", 'WRITABLE'
    )

    print(result)
 