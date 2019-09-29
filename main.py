import requests
import time
import json

class VkUser:
    def __init__(self, data=None):
        self.access_token = input('Введите токен OAuth: \n')
        self.data = data

    def get_user_id(self):
        if self.data is None:
            self.data = input('Введите UserID: \n')
        u_init_params = {
            'user_ids': str(self.data),
            'fields': 'screen_name,user_id',
            'access_token': self.access_token,
            'v': 5.101
        }
        u_init_resp = requests.get(
            'https://api.vk.com/method/users.get',
            params=u_init_params
        )
        user_dict = u_init_resp.json()
        user_id = (user_dict['response'][0]['id'])
        user_name = (user_dict['response'][0]['screen_name'])
        return user_id

    def set_params(self):
        params = {
            'access_token': self.access_token,
            'user_id': self.get_user_id(),
            'v': 5.101
            }
        return params

    def get_friends_list(self):
        friends_response = requests.get(
            'https://api.vk.com/method/friends.get',
            params=self.set_params()
        )
        friends = friends_response.json()
        friends_list = friends['response']['items']
        return friends_list

    def get_groups_list(self):
        groups_response = requests.get(
            'https://api.vk.com/method/groups.get',
            params=self.set_params()
        )
        groups = groups_response.json()
        groups_list = groups['response']['items']
        return groups_list

    def get_group_membership(self):
        friends_list = self.get_friends_list()
        groups_list = self.get_groups_list()
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
                    'access_token': self.access_token,
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

    def sort_groups(self, n=0):
        groups_dict = self.get_group_membership()
        sorted_groups = {}
        for key, group in groups_dict.items():
            if len(group) <= n:
                sorted_groups[key] = group
        return sorted_groups

    def get_group_info(self):
        # Получаем из ВК информацию по группам
        groups = self.sort_groups()
        group_media = []
        for group in groups:
            gi_params = {'group_id': str(group),
                         'fields': ['id', 'name', 'description',
                                    'members_count'],
                         'access_token': self.access_token,
                         'v': 5.101, }
            group_info_resp = requests.get(
                'https://api.vk.com/method/groups.getById',
                params=gi_params
            )
            group_media.append(group_info_resp.json())
            time.sleep(0.3)
        return group_media

    def build_json_output(self):
        group_info = self.get_group_info()
        output_info = []
        for record in group_info:
            output_group = {
                'name': str(record['response'][0]['name']),
                'gid': record['response'][0]['id'],
                'members_count': record['response'][0]['members_count']
            }
            output_info.append(output_group)
        return output_info

    def write_json_output(self):
        output_info = self.build_json_output()
        with open('groups.json', 'w', encoding='utf-8') as groups_file:
            json.dump(output_info, groups_file,
                      ensure_ascii=False, indent=2)


if __name__ == '__main__':
    eshmargunov = VkUser('eshmargunov')
    eshmargunov.write_json_output()

