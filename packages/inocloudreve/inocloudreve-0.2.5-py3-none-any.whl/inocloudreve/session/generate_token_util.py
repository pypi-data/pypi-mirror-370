#import jwt

def decode_token(
    self,
    master_key: str,
    access_token: str
) -> dict:
    #decoded = jwt.decode(
    #    access_token,
    #    master_key,
    #    algorithms=["HS256"],
    #    options={"verify_exp": False, "verify_nbf": False}
    #)
    decoded = None
    return {
        "success": True,
        "token": decoded
    }
    