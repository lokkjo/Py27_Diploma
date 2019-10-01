import requests
import time
import json
import sys


class VkUser:
    def __init__(self, data=None, n=0):
        self.access_token = input('Введите токен OAuth: \n')
        self.data = data
        self.n = n

    def get_user_id(self):
        if self.data is None:
            self.data = input('Введите UserID: \n')
        time.sleep(0.5)
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
        if user_dict['response'][0].get('deactivated') == 'deleted':
            print('\nСтраница пользователя удалена')
            sys.exit()
        user_id = (user_dict['response'][0]['id'])
        return user_id

    def set_params(self):
        params = {
            'access_token': self.access_token,
            'user_id': self.get_user_id(),
            'v': 5.101
        }
        return params

    def get_friends_list(self):
        time.sleep(0.5)
        friends_response = requests.get(
            'https://api.vk.com/method/friends.get',
            params=self.set_params()
        )
        friends = friends_response.json()
        friends_list = friends['response']['items']
        return friends_list

    def get_groups_list(self):
        time.sleep(0.5)
        groups_response = requests.get(
            'https://api.vk.com/method/groups.get',
            params=self.set_params()
        )
        groups = groups_response.json()
        groups_list = groups['response']['items']
        return groups_list

    def get_group_membership(self):
        groups_list = self.get_groups_list()
        group_membership = {}
        for group in groups_list:
            time.sleep(0.5)
            print(
                f'\rОбрабатывается {groups_list.index(group) + 1} '
                f'группа из {len(groups_list)}', end="", flush=True)
            g_mms_params = {
                'group_id': f'{group}',
                'filter': 'friends',
                # 'user_ids': self.get_friends_list(),
                'access_token': self.access_token,
                'v': 5.101
            }
            g_mms_resp = requests.get(
                'https://api.vk.com/method/groups.getMembers',
                params=g_mms_params,
            )
            g_mms_mid_dict = g_mms_resp.json()
            if g_mms_mid_dict.get('error') is not None:
                if g_mms_mid_dict.get('error')['error_code'] == 6:
                    print('Слишком много обращений в секунду!')
                    sys.exit()
                print(f'\n{group}: ERROR '
                      f'{g_mms_mid_dict.get("error")["error_msg"]}'
                      f'\n')
                pass
            elif g_mms_mid_dict.get('response')is not None:
                group_membership[group] = g_mms_mid_dict['response']
        return group_membership

    def sort_groups(self):
        groups_dict = self.get_group_membership()
        sorted_groups = []
        for key, group in groups_dict.items():
            group_count = group['count']
            if group_count <= self.n:
                sorted_groups.append(key)
        return sorted_groups

    def get_group_info(self):
        # Получаем из ВК информацию по группам
        groups = self.sort_groups()
        group_media = []
        print('\n')
        for group in groups:
            time.sleep(0.5)
            print(
                f'\rСбор информации: {groups.index(group) + 1} '
                f'группа из {len(groups)}', end="", flush=True)
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

        return group_media

    def build_json_output(self):
        group_info = self.get_group_info()
        output_info = []
        for record in group_info:
            output_group = {
                'name': str(record['response'][0]['name']),
                'gid': record['response'][0]['id'],
                'members_count': record['response'][0][
                    'members_count']
            }
            output_info.append(output_group)
        return output_info

    def write_json_output(self):
        output_info = self.build_json_output()
        with open('groups.json', 'w',
                  encoding='utf-8') as groups_file:
            json.dump(output_info, groups_file,
                      ensure_ascii=False, indent=2)
        print('\n \nФайл записан!')


if __name__ == '__main__':
    eshmargunov = VkUser(3182173)
    eshmargunov.write_json_output()
