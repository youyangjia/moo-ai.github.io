import argparse
import github
import json
import wget

DOWNLOAD_FILE = 'env.json'


def download_env_file(keeping=False):
    file = 'task_list.json'
    if keeping:
        file = 'task_list_sleep.json'
    url = ("https://raw.githubusercontent.com/moo-ai/moo-ai.github.io/"
           "master/env_info/%s" % file)
    wget.download(url, DOWNLOAD_FILE)


def update_env_info(job_name, patch_set, ip, result_url, keeping=False):
    with open(DOWNLOAD_FILE, 'r') as json_file:
        exist_data = json.load(json_file)

    exist_data[job_name] = {
        "patch_set": patch_set,
    }
    if keeping:
        exist_data[job_name]["ip"] = ip
        exist_data[job_name]["credential"] = "demo/demo"
    else:
        exist_data[job_name]["result_url"] = result_url

    with open(DOWNLOAD_FILE, 'w') as file:
        json.dump(exist_data, file)


def refresh_env_info(keeping=False):
    with open(DOWNLOAD_FILE, 'r') as env_file:
        cont = env_file.read()
    github_obj = github.Github(args.user,
                               args.password)
    repo = github_obj.get_user().get_repo('moo-ai.github.io')
    env_file_name = 'env_info/task_list.json'
    if keeping:
        env_file_name = 'env_info/task_list_sleep.json'
    try:
        contents = repo.get_contents(env_file_name, ref="master")
    except github.UnknownObjectException:
        exit(1)

    repo.update_file(contents.path, "upload %s ci job" % args.job, cont,
                     contents.sha, branch="master")
    print("Success update %s" % env_file_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='MOO env info refresh tool',
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--user',  metavar='<user_name>', required=True,
                        help="Github user name")
    parser.add_argument('--password', metavar='<password>', required=True,
                        help="Github user password")
    parser.add_argument('--job', metavar='<job>', required=True,
                        help="The webhook server's IP")
    parser.add_argument('--patch', metavar='<patch>', required=True,
                        help="The webhook server's IP")
    parser.add_argument('--ip', metavar='<ip>', required=True,
                        help="Environment IP")
    parser.add_argument('--url', metavar='<url>', required=True,
                        help="Result Url")
    parser.add_argument('--keeping', metavar='<keeping>', required=True,
                        help="Keep the environment or not")
    args = parser.parse_args()

    if args.keeping == 'true':
        keep_env = True
    else:
        keep_env = False

    download_env_file(keep_env)
    update_env_info(args.job, args.patch, args.ip, args.url,
                    keeping=keep_env)
    refresh_env_info(keeping=keep_env)
