# from urllib.parse import urlencode
import requests
import time
import json

# Получение ссылки для аутентификации

# OAUTH_URL = 'https://oauth.vk.com/authorize'
# OAUTH_DATA = {
#     'client_id': 7151671,
#     'redirect_uri': 'https://oauth.vk.com/blank.html',
#     'display': 'page',
#     'scope': 'friends,groups',
#     'response_type': 'token',
#     'v': 5.101
# }
# print('?'.join((OAUTH_URL, urlencode(OAUTH_DATA))))

# Начало полезного кода

access_token = input('Вставьте токен OAuth: \n')
params = {
    'access_token': access_token,
    'v': 5.101
}

temp_groups_zero = {134709480: [], 8564: [],
                    101522128: []}  # Временный словарь для быстрых тестов


def get_friends_list():
    friends_response = requests.get(
        'https://api.vk.com/method/friends.get',
        params
    )
    friends = friends_response.json()
    friends_list = friends['response']['items']
    return friends_list


def get_groups_list():
    groups_response = requests.get(
        'https://api.vk.com/method/groups.get',
        params
    )
    groups = groups_response.json()
    groups_list = groups['response']['items']
    return groups_list


def get_group_membership():
    friends_list = get_friends_list()
    groups_list = get_groups_list()
    groups_membership = {}
    for group in groups_list:
        groups_membership[group] = []
        for friend in friends_list:
            print(
                f'\rОбрабатывается {groups_list.index(group) + 1} '
                f'группа из {len(groups_list)}; '
                f'{friends_list.index(friend) + 1} друг из '
                f'{len(friends_list)}', end="", flush=True)
            g_mms_params = {
                'group_id': f'{group}',
                'user_id': friend,
                'access_token': access_token,
                'v': 5.101
            }
            g_mms_resp = requests.get(
                'https://api.vk.com/method/groups.isMember',
                params=g_mms_params,
            )
            g_mms_media_dict = g_mms_resp.json()
            mms = g_mms_media_dict['response']
            if mms == 1:
                groups_membership[group].append(friend)
            time.sleep(0.3)
    return groups_membership


def sort_groups(n=0):
    groups_dict = get_group_membership()
    sorted_groups = {}
    for key, group in groups_dict.items():
        if len(group) <= n:
            sorted_groups[key] = group
    return sorted_groups


def get_group_info():
    # Получаем из ВК информацию по группам
    # groups = temp_groups_zero.keys() # TODO: Заменить потом эту строку - она тут для быстрых тестов
    groups = sort_groups()
    group_media = []
    for group in groups:
        gi_params = {'group_id': str(group),
                     'fields': ['id', 'name', 'description',
                                'members_count'],
                     'access_token': access_token,
                     'v': 5.101, }
        group_info_resp = requests.get(
            'https://api.vk.com/method/groups.getById',
            params=gi_params
        )
        group_media.append(group_info_resp.json())
        time.sleep(0.3)
    return group_media


def build_json_output():
    group_info = get_group_info()
    output_info = []
    for record in group_info:
        output_group = {
            'name': str(record['response'][0]['name']),
            'gid': record['response'][0]['id'],
            'members_count': record['response'][0]['members_count']
        }
        output_info.append(output_group)
    return output_info


def write_json_output():
    output_info = build_json_output()
    with open('groups.json', 'w', encoding='utf-8') as groups_file:
        json.dump(output_info, groups_file,
                  ensure_ascii=False, indent=2)


if __name__ == '__main__':
    # print(sort_groups(0))
    write_json_output()
