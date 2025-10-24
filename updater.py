import json, requests, zipfile, os, time, sys
def run():
    try:
        conf = json.load(open('config.json'))
        base = conf.get('github_repo')
        if not base:
            print('Updater: github_repo not set.')
            return
        r = requests.get(base + 'config.json', timeout=10)
        if r.status_code!=200:
            print('Updater remote not reachable.')
            return
        remote = r.json()
        cur = conf.get('version','v0')
        rem = remote.get('version',cur)
        if rem != cur:
            print('Updating', cur, '->', rem)
            zurl = f"{base}bot_doky_{rem}.zip"
            r2 = requests.get(zurl, timeout=30)
            open('update_tmp.zip','wb').write(r2.content)
            with zipfile.ZipFile('update_tmp.zip','r') as z:
                z.extractall('.')
            os.remove('update_tmp.zip')
            conf['version']=rem
            json.dump(conf, open('config.json','w'), indent=2)
            print('Updated to', rem, 'restarting...')
            time.sleep(2)
            os.execv(sys.executable, ['python3'] + sys.argv)
        else:
            print('No update available.')
    except Exception as e:
        print('Updater error', e)
if __name__=='__main__': run()
