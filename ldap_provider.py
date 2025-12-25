from keycloak_util import *
import argparse
import json

# Ansible実行サンプル
# - name: Create/update LDAP provider
#   command: >
#     python3 {{ role_path }}/scripts/ldap_provider.py
#     create {{ keycloak_host }} {{ keycloak_port }}
#     {{ keycloak_admin_user }} {{ keycloak_admin_password }}
#     {{ realm_name }} {{ ldap_provider_name }}
#     --config '{{ ldap_provider_config | to_json }}'
#   register: ldap_cmd
#   changed_when: (ldap_cmd.stdout | from_json).changed


def __configure(token, host, port, realm_name, provider_name, config):
    changed = 0

    for k, v in config.items():
        if renovare_ldap_provider(
            token, host, port, realm_name,
            provider_name, k, v
        ):
            changed += 1

    return changed


def __get(token, host, port, realm_name, provider_name):
    print(json.dumps(accipere_ldap_provider(
        token, host, port, realm_name, provider_name
    )))


def __create(token, host, port, realm_name, provider_name, config_json):
    changed = 0

    config = json.loads(config_json)

    try:
        asserere_ldap_provider_exists(
            token, host, port, realm_name,
            provider_name
        )
    except AssertionError:
        if creare_ldap_provider(
            token, host, port, realm_name,
            provider_name, config
        ):
            changed += 1

    changed += __configure(
        token, host, port, realm_name,
        provider_name, config
    )

    return changed


def __assert(token, host, port, realm_name, provider_name, config_json):
    config = json.loads(config_json)

    asserere_ldap_provider_exists(
        token, host, port, realm_name,
        provider_name
    )
    for k, v in config.items():
        asserere_ldap_provider_config(
            token, host, port, realm_name,
            provider_name, k, v
        )


def __build_args():
    parser = argparse.ArgumentParser(
        description='\n'.join([
            "KeyCloakのLDAP Provider作成スクリプト",
            "  get: 設定を表示",
            "  create: LDAP Providerを作成",
            "  assert: 設定値チェック",
        ])
    )

    parser.add_argument(
        'operation', choices=['get', 'create', 'assert'],
        help='実行内容. get: 設定表示 | create: LDAP Provider作成 | assert: 設定値チェック'
    )
    parser.add_argument(
        'host', help='KeyCloakのホストorIPアドレス'
    )
    parser.add_argument(
        'port', help='KeyCloakのListenポート'
    )
    parser.add_argument(
        'admin_user', help='KeyCloakのAdminユーザー'
    )
    parser.add_argument(
        'admin_password', help='KeyCloakのAdminパスワード'
    )
    parser.add_argument(
        'realm_name', help='対象のレルム名'
    )
    parser.add_argument(
        'provider_name', help='対象のLDAP Provider名'
    )
    parser.add_argument(
        '--config', help='LDAP Providerの設定(JSON). create/assertで必須'
    )

    return parser.parse_args()


if __name__ == '__main__':
    args = __build_args()

    token = accipere_token(
        args.host, args.port,
        args.admin_user, args.admin_password
    )

    if args.operation == 'get':
        __get(
            token, args.host, args.port,
            args.realm_name, args.provider_name
        )

    elif args.operation == 'create':
        if not args.config:
            raise SystemExit("--config is required for create")
        changed = __create(
            token, args.host, args.port,
            args.realm_name, args.provider_name, args.config
        )
        if changed == 0:
            print(json.dumps({
                'host': args.host,
                'port': args.port,
                'realm': args.realm_name,
                'provider': args.provider_name,
                'config': json.loads(args.config),
                'changed': False
            }))
        else:
            print(json.dumps({
                'host': args.host,
                'port': args.port,
                'realm': args.realm_name,
                'provider': args.provider_name,
                'config': json.loads(args.config),
                'changed': True
            }))

    elif args.operation == 'assert':
        if not args.config:
            raise SystemExit("--config is required for assert")

        try:
            __assert(
                token, args.host, args.port,
                args.realm_name, args.provider_name, args.config
            )
            print(json.dumps({'ok': True}))
        except:
            print(json.dumps({'ok': False}))
            raise
