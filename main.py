import requests
from python3_anticaptcha import NoCaptchaTaskProxyless


def getRecaptchaToken():
    print("[+] Obtaining Recaptcha Token")
    api_key = 'REDACTED'
    site_key = 'REDACTED'
    url = 'https://dashboard.hit-pay.com/login'
    user_answer = NoCaptchaTaskProxyless.NoCaptchaTaskProxyless(anticaptcha_key=api_key) \
        .captcha_handler(websiteURL=url,
                         websiteKey=site_key)

    recaptchaToken = user_answer['solution']['gRecaptchaResponse']

    return recaptchaToken


def getValidCookies(recaptchaToken):
    print("[+] Creating new Requests Session")
    session = requests.session()
    r1 = session.get('https://dashboard.hit-pay.com/login')
    csrf = str(r1.content).split('csrf-token" content="')[1].split('">')[0]
    print(f"[+] Initial CSRF Parsed - {csrf}")

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRF-TOKEN": csrf
    }
    data = {
        "email": "REDACTED",
        "password": "REDACTED",
        "recaptcha_token": recaptchaToken
    }

    r2 = session.post('https://dashboard.hit-pay.com/login', headers=headers, json=data)
    print(r2.content)
    print(r2.headers)
    print(session.cookies)
    if "errors" in str(r2.content):
        print("[-] Login error, likely recaptcha invalid. Retrying...")
        return False, False
    else:
        print("[+] Login Successful.")
        return session, csrf


def getNewCSRF(session, csrf):
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
        "X-CSRF-TOKEN": csrf
    }
    r = session.get("https://dashboard.hit-pay.com", headers=headers)

    try:
        newCSRF = str(r.content).split('name="csrf-token" content="')[1].split('">')[0]
        print(f'[+] New CSRF Parsed - {newCSRF}')

        return newCSRF
    except:
        input("[-] Unable to parse new CSRF. Error on hold.")
        return False


def markAsPickedUp(session, orderID, newCSRF):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15",
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRF-TOKEN": newCSRF
    }

    data = {
        "message": "Pickup completed, thank you!",
        "mark_as_ship": True
        }

    r = session.put(f"https://api.hit-pay.com/v1/business/REDACTED/order/{orderID}/mark-as-picked-up", headers=headers, json=data)
    try:
        if r.json()["status"] == "completed":
            print(f"[+] Pick Up complete - {orderID}")
            return True
    except:
        print(f"[-] Error, Pick Up Failed. Something went wrong - {orderID}")
        print(r.content)
        return False

# if __name__ == '__main__':
#     while True:
#         recaptchaToken = getRecaptchaToken()
#         LoginSession, csrf = getValidCookies(recaptchaToken)
#         if LoginSession:
#             break
#
#     newCSRF = getNewCSRF(LoginSession, csrf)
#     status = markAsPickedUp(LoginSession, "9b2abca6-cad1-4e40-8388-f512e32464a3", newCSRF)


