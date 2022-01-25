from datetime import date
import jwt
pv_key = 'NTNv7j0TuYARvmNMmWXo6fKvM4o6nv/aUi9ryX38ZH+L1bkrnD1ObOQ8JAUmHCBq7Iy7otZcyAagBLHVKvvYaIpmMuxmARQ97jUVG16Jkpkp1wXOPsrF9zwew6TpczyHkHgX5EuLg2MeBuiT/qJACs1J0apruOOJCg/gOtkjB4c='
adminToken= 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IjEiLCJhZG1pbiI6dHJ1ZSwiaWF0IjoxNjQzMTAyNjgwLCJleHAiOjE2NDkxMDYyODB9.8hG9I2nTxNTXuYRVy46q-LDvvSG7IJtyOz5LdKRtPzs'


encoded_jwt = jwt.encode({
  "id": "2",
  "admin": False,
  "iat": 1643103048,
  "exp": 1649106280
}, pv_key, algorithm="HS256")
print(encoded_jwt)
