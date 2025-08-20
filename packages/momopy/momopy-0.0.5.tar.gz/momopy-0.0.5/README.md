# momopy
API Wrapper for MTN Mobile Money 

# Sanbox Keys Generation
```sh
1. First create an API USER at /apiuser {POST} using headers
- X-Reference-Id -- A UUID
- Ocp-Apim-Subscription-Key -- Your subscription (Primary or Secondary)

2. Use API USER to then generate an API KEY

3. Then proceed to use the API KEY to generate a "TOKEN" for the Bearer Token you want to use in any of the product

The API KEY expires in 3600 seconds, and you need to dynamically check and regenerate one if it expires on the fly

# Contributing
```sh
pip install -e . --no-deps

```


