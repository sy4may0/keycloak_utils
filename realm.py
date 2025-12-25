from keycloak_util import *
import argparse
import json

# Ansible実行サンプル
# - name: Create/update realm
#   command: >
#     python3 {{ role_path }}/scripts/realm.py
#     create {{ keycloak_host }} {{ keycloak_port }}
#     {{ keycloak_admin_user }} {{ keycloak_admin_password }}
#     {{ realm_name }}
#     --config '{{ realm_config | to_json }}'
#   register: realm_cmd
#   changed_when: (realm_cmd.stdout | from_json).changed

def __configure(token, host, port, realm_name, config):
    changed = 0

    for k, v in config.items():
        if renovare_realm(
            token, host, port, realm_name, k, v
        ):
            changed += 1

    return changed

def __get(token, host, port, realm_name):
    print(json.dumps(accipere_realm(
        token, host, port, realm_name
    )))

def __create(token, host, port, realm_name, config_json):
    changed = 0

    config = json.loads(config_json)

    try:
        asserere_realm_exists(
            token, host, port, realm_name
        )
    except AssertionError:
        if creare_realm(token, host, port, realm_name):
            changed += 1

    changed += __configure(
        token, host, port, realm_name, config
    )

    return changed

def __assert(token, host, port, realm_name, config_json):
    config = json.loads(config_json)

    asserere_realm_exists(token, host, port, realm_name)
    for k, v in config.items():
        asserere_realm_config(
            token, host, port, realm_name,
            k, v
        )

def __build_args():
    parser = argparse.ArgumentParser(
        description='\n'.join([
            "KeyCloakのRealm作成スクリプト",
            "  get: 設定を表示",
            "  create: Realmを作成",
            "  assert: 設定値チェック",
        ])
    )

    parser.add_argument(
        'operation', choices=['get', 'create', 'assert'],
        help='実行内容. get: 設定表示 | create: REALM作成 | assert: 設定値チェック'
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
        '--config', help='レルムの設定(JSON). create/assertで必須'
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
            args.realm_name,
        )

    elif args.operation == 'create':
        if not args.config:
            raise SystemExit("--config is required for create")
        changed = __create(
            token, args.host, args.port,
            args.realm_name, args.config
        )
        if changed == 0:
            print(json.dumps({
                'host': args.host,
                'port': args.port,
                'realm': args.realm_name,
                'config': json.loads(args.config),
                'changed': False
            }))
        else:
            print(json.dumps({
                'host': args.host,
                'port': args.port,
                'realm': args.realm_name,
                'config': json.loads(args.config),
                'changed': True
            }))

    elif args.operation == 'assert':
        if not args.config:
            raise SystemExit("--config is required for assert")
 
        try:
            __assert(
                token, args.host, args.port,
                args.realm_name, args.config
            )
            print(json.dumps({'ok': True}))
        except:
            print(json.dumps({'ok': False}))
            raise
 




     

     
