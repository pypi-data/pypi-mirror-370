import requests
import SignerPy
import json
import secrets
import uuid
import binascii
import os
import time
import random

class Email2UsernameTikTok:
    def __init__(self, email):
        self.email = email
        self.secret = secrets.token_hex(16)
        self.s = requests.session()
    
    def xor(self, string):
        return "".join([hex(ord(c) ^ 5)[2:] for c in string])
    
    def get_ksj(self):
        xor_email = self.xor(self.email)
        params = {
            "request_tag_from": "h5",
            "fixed_mix_mode": "1",
            "mix_mode": "1",
            "account_param": xor_email,
            "scene": "1",
            "device_platform": "android",
            "os": "android",
            "ssmix": "a",
            "type": "3736",
            "_rticket": str(round(random.uniform(1.2, 1.6) * 100000000) * -1) + "4632",
            "cdid": str(uuid.uuid4()),
            "channel": "googleplay",
            "aid": "1233",
            "app_name": "musical_ly",
            "version_code": "370805",
            "version_name": "37.8.5",
            "manifest_version_code": "2023708050",
            "update_version_code": "2023708050",
            "ab_version": "37.8.5",
            "resolution": "1600*900",
            "dpi": "240",
            "device_type": "SM-G998B",
            "device_brand": "samsung",
            "language": "en",
            "os_api": "28",
            "os_version": "9",
            "ac": "wifi",
            "is_pad": "0",
            "current_region": "TW",
            "app_type": "normal",
            "sys_region": "US",
            "last_install_time": "1754073240",
            "mcc_mnc": "46692",
            "timezone_name": "Asia/Baghdad",
            "carrier_region_v2": "466",
            "residence": "TW",
            "app_language": "en",
            "carrier_region": "TW",
            "timezone_offset": "10800",
            "host_abi": "arm64-v8a",
            "locale": "en-GB",
            "ac2": "wifi",
            "uoo": "1",
            "op_region": "TW",
            "build_number": "37.8.5",
            "region": "GB",
            "ts": str(round(random.uniform(1.2, 1.6) * 100000000) * -1),
            "iid": str(random.randint(1, 10**19)),
            "device_id": str(random.randint(1, 10**19)),
            "openudid": str(binascii.hexlify(os.urandom(8)).decode()),
            "support_webview": "1",
            "okhttp_version": "4.2.210.6-tiktok",
            "use_store_region_cookie": "1",
            "app_version": "37.8.5"
        }
        
        cookies = {
            "passport_csrf_token": self.secret,
            "passport_csrf_token_default": self.secret,
            "install_id": params["iid"],
        }

        cookies = {
            '_ga_3DVKZSPS3D': 'GS2.1.s1754435486$o1$g0$t1754435486$j60$l0$h0',
            '_ga': 'GA1.1.504663773.1754435486',
            '__gads': 'ID=0cfb694765742032:T=1754435487:RT=1754435487:S=ALNI_MbIZNqLgouoeIxOQ2-N-0-cjxxS1A',
            '__gpi': 'UID=00001120bc366066:T=1754435487:RT=1754435487:S=ALNI_MaWgWYrKEmStGHPiLiBa1zlQOicuA',
            '__eoi': 'ID=22d520639150e74a:T=1754435487:RT=1754435487:S=AA-AfjZKI_lD2VnwMipZE8ienmGW',
            'FCNEC': '%5B%5B%22AKsRol8AtTXetHU2kYbWNbhPJd-c3l8flgQb4i54HStVK8CCEYhbcA3kEFqWYrBZaXKWuO9YYJN53FddyHbDf05q1qY12AeNafjxm2SPp7mhXZaop_3YiUwuo_WHJkehVcl5z4VyD7GHJ_D8nI2DfTX5RfrQWIHNMA%3D%3D%22%5D%5D',
        }

        headers = {
            'accept': '*/*',
            'accept-language': 'en,ar;q=0.9,en-US;q=0.8',
            'application-name': 'web',
            'application-version': '4.0.0',
            'content-type': 'application/json',
            'origin': 'https://temp-mail.io',
            'priority': 'u=1, i',
            'referer': 'https://temp-mail.io/',
            'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
            'x-cors-header': 'iaWg3pchvFx48fY',
        }

        json_data = {
            'min_name_length': 10,
            'max_name_length': 10,
        }

        response = requests.post('https://api.internal.temp-mail.io/api/v3/email/new', cookies=cookies, headers=headers, json=json_data)
        try:
            name = response.json()["email"]
            url = "https://api16-normal-c-alisg.tiktokv.com/passport/account_lookup/email/"

            self.s.cookies.update(cookies)
            m = SignerPy.sign(params=params, cookie=cookies)

            headers = {
                'User-Agent': "com.zhiliaoapp.musically/2023708050 (Linux; U; Android 9; en_GB; SM-G998B; Build/SP1A.210812.016;tt-ok/3.12.13.16)",
                'x-ss-stub': m['x-ss-stub'],
                'x-tt-dm-status': "login=1;ct=1;rt=1",
                'x-ss-req-ticket': m['x-ss-req-ticket'],
                'x-ladon': m['x-ladon'],
                'x-khronos': m['x-khronos'],
                'x-argus': m['x-argus'],
                'x-gorgon': m['x-gorgon'],
                'content-type': "application/x-www-form-urlencoded",
                'content-length': m['content-length'],
            }

            response = requests.post(url, headers=headers, params=params, cookies=cookies)
            try:
                passport_ticket = response.json()["data"]["accounts"][0]["passport_ticket"]

                name_xor = self.xor(name)
                url = "https://api16-normal-c-alisg.tiktokv.com/passport/email/send_code/"
                params.update({"not_login_ticket": passport_ticket, "email": name_xor})
                m = SignerPy.sign(params=params, cookie=cookies)
                headers = {
                    'User-Agent': "com.zhiliaoapp.musically/2023708050 (Linux; U; Android 9; en_GB; SM-G998B; Build/SP1A.210812.016;tt-ok/3.12.13.16)",
                    'Accept-Encoding': "gzip",
                    'x-ss-stub': m['x-ss-stub'],
                    'x-ss-req-ticket': m['x-ss-req-ticket'],
                    'x-ladon': m['x-ladon'],
                    'x-khronos': m['x-khronos'],
                    'x-argus': m['x-argus'],
                    'x-gorgon': m['x-gorgon'],
                }

                response = self.s.post(url, headers=headers, params=params, cookies=cookies)
                if "email_ticket" in response.text:
                    time.sleep(5)

                    cookies = {
                        '_ga': 'GA1.1.504663773.1754435486',
                        '__gads': 'ID=0cfb694765742032:T=1754435487:RT=1754435487:S=ALNI_MbIZNqLgouoeIxOQ2-N-0-cjxxS1A',
                        '__gpi': 'UID=00001120bc366066:T=1754435487:RT=1754435487:S=ALNI_MaWgWYrKEmStGHPiLiBa1zlQOicuA',
                        '__eoi': 'ID=22d520639150e74a:T=1754435487:RT=1754435487:S=AA-AfjZKI_lD2VnwMipZE8ienmGW',
                        'FCNEC': '%5B%5B%22AKsRol8AtTXetHU2kYbWNbhPJd-c3l8flgQb4i54HStVK8CCEYhbcA3kEFqWYrBZaXKWuO9YYJN53FddyHbDf05q1qY12AeNafjxm2SPp7mhXZaop_3YiUwuo_WHJkehVcl5z4VyD7GHJ_D8nI2DfTX5RfrQWIHNMA%3D%3D%22%5D%5D',
                        '_ga_3DVKZSPS3D': 'GS2.1.s1754435486$o1$g0$t1754435503$j43$l0$h0',
                    }

                    headers = {
                        'accept': '*/*',
                        'accept-language': 'en,ar;q=0.9,en-US;q=0.8',
                        'application-name': 'web',
                        'application-version': '4.0.0',
                        'content-type': 'application/json',
                        'origin': 'https://temp-mail.io',
                        'priority': 'u=1, i',
                        'referer': 'https://temp-mail.io/',
                        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-site',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                        'x-cors-header': 'iaWg3pchvFx48fY',
                    }

                    response = requests.get(
                        'https://api.internal.temp-mail.io/api/v3/email/{}/messages'.format(name),
                        cookies=cookies,
                        headers=headers,
                    )
                    try:
                        username = response.json()[0]["body_text"].split('This email was generated for')[1].split("\n")[0].strip().rstrip(".")
                        return {"status": "success", "username": username, "email": self.email}
                    except:
                        return {"status": "error", "message": "ksj"}
                else:
                    return {"status": "error", "message": "ksj"}
            except:
                return {"status": "error", "message": "ksj"}
        except:
            return {"status": "error", "message": "ksj"}


def find_tiktok_username(email):
    """
    دالة للعثور على اسم المستخدم في TikTok باستخدام البريد الإلكتروني
    
    Args:
        email (str): البريد الإلكتروني المراد البحث عنه
    
    Returns:
        dict: نتيجة البحث تحتوي على الحالة واسم المستخدم
    """
    finder = Email2UsernameTikTok(email)
    return finder.get_ksj()


# مثال على الاستخدام
if __name__ == "__main__":
    # يمكنك تغيير البريد الإلكتروني هنا
    email_to_search = input("أدخل البريد الإلكتروني للبحث عن اسم المستخدم في TikTok: ")
    
    print(f"جاري البحث عن اسم المستخدم للبريد الإلكتروني: {email_to_search}")
    print("انتظر قليلاً...")
    
    result = find_tiktok_username(email_to_search)
    
    print("\n" + "="*50)
    print("النتيجة:")
    print("="*50)
    
    if result["status"] == "success":
        print(f"✅ تم العثور على اسم المستخدم بنجاح!")
        print(f"📧 البريد الإلكتروني: {result['email']}")
        print(f"👤 اسم المستخدم: {result['username']}")
    else:
        print(f"❌ فشل في العثور على اسم المستخدم")
        print(f"📝 الرسالة: {result['message']}")
    
    print("="*50)

