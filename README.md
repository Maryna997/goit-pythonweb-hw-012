## GOIT Python Web Homework 12

### Requirements

- Python 3.10
- Docker and Docker Compose
- Poetry

### Installation

````shell
git clone https://github.com/Maryna997/goit-pythonweb-hw-012.git
```

```shell
cd goit-pythonweb-hw-012
````

### Running the Application

```shell
docker compose up -d --build
```

### Testing

Make sure that docker compose of the project is running.

Install project dependencies:

```shell
poetry install
```

Run the test and coverage command:

```shell
pytest --cov --cov-report=term-missing --disable-warnings
```

#### Most recent test coverage report

```
---------- coverage: platform linux, python 3.10.12-final-0 ----------
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
api/__init__.py                               0      0   100%
api/auth.py                                  26      0   100%
api/contacts.py                              35      0   100%
api/instances.py                             15      0   100%
api/test_auth_api.py                         70      1    99%   53
api/test_contacts_api.py                    135      2    99%   68, 70
api/test_users_api.py                        47      0   100%
api/users.py                                 31      3    90%   21-22, 51
clients/cloudinary_client.py                 14      3    79%   47-48, 60
clients/fast_api_mail_client.py              20      7    65%   56-69
clients/redis_client.py                      13      3    77%   42, 56, 68
main.py                                      21      2    90%   19, 33
repositories/__init__.py                      0      0   100%
repositories/contact_repository.py           63      0   100%
repositories/test_contact_repository.py     120      0   100%
repositories/test_user_repository.py         86      0   100%
repositories/user_repository.py              58      0   100%
schemas/auth.py                               7      0   100%
schemas/contacts.py                          23      0   100%
schemas/users.py                             19      0   100%
services/__init__.py                          0      0   100%
services/auth_service.py                    151     24    84%   29, 33, 37, 41, 47, 53, 57, 61, 67, 103, 106, 109-110, 125, 164-166, 170, 174, 186, 196, 199, 202-203
services/contact_service.py                  42      7    83%   10, 14, 18, 22, 26, 31, 35
services/test_auth_service.py               129      0   100%
services/test_contact_service.py             67      0   100%
services/test_user_service.py                72      0   100%
services/user_service.py                     41      4    90%   12, 16, 22, 26
-----------------------------------------------------------------------
TOTAL                                      1305     56    96%
```
