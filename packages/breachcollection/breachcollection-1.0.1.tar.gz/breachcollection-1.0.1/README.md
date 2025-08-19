# breachcollection

A package that wraps the [Breachcollection](https://breachcollection.com) [API](https://breachcollection.com/api_docs/). 

The Leaked Passwords API has a vast collection of credentials previously leaked on data breaches. 

Via this package, it can be integrated in your website's signup page to ensure your users do not sign up using insecure passwords. 

It supports configurable K-Anonimity, meanign that the password is hashed before being sent, and only a portion of the hash is sent, to ensure maximum privacy.

## Installation
To install the package, run the following command in your terminal:
```
pip install breachcollection
```

## Usage
How you can integrate this package in your signup process.
```
from breachcollection import is_password_safe

bc_call = is_password_safe(password, breachcollection_api_key, n_chars_to_send)
if bc_call == True or bc_call == None:
...
```

The function will return True if the password has not been found
in any leaked databases, and False if it has.

If an error occurs, the error will be printed to the terminal
and the function will return None.

By default, n_chars_to_send is 10, so you do not need to specify a value for n_chars_to_send, but you can choose any value between 7 and 32. 

The smaller the value, the more private your search will be, but potentially more computationally expensive on your side (therefore, slower, by a couple of milliseconds).



## Dependencies
This package requires the requests library to function. It will be automatically installed when you install breachcollection via pip.
```
requests
```

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Author
BreachCollection