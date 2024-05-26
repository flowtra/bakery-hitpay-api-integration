from fastapi import FastAPI
from main import *

app = FastAPI()


@app.get('/')
async def index():
    return "Nothing to see here!"

@app.on_event("startup")
@app.get('/reset-auth')
async def resetAuth():
    global LoginSession, newCSRF
    while True:
        recaptchaToken = getRecaptchaToken()
        LoginSession, csrf = getValidCookies(recaptchaToken)
        if LoginSession:
            break

    newCSRF = getNewCSRF(LoginSession, csrf)
    if newCSRF:
        return "Successfully reset authentication cookies!"
    else:
        return "ERROR - Something went wrong during log in."

@app.get('/mark-picked-up/{orderid}')
async def markPickedUp(orderid: str):

    status = markAsPickedUp(LoginSession, orderid, newCSRF)
    if status:
        return f"Successfully marked as Picked Up! Order {orderid}"
    return f"ERROR - Failed to mark as picked up - order {orderid}"

