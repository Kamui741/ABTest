<!--
 * @Author: ChZheng
 * @Date: 2025-02-12 04:52:29
 * @LastEditTime: 2025-02-12 04:52:31
 * @LastEditors: ChZheng
 * @Description:
 * @FilePath: /code/ABTest/api/qushu/readme.md
-->
project/
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── auth.py
│   ├── mapper.py
│   └── exceptions.py
├── api/
│   ├── __init__.py
│   ├── routers.py
│   ├── schemas.py
│   ├── services.py
│   ├── clients.py
│   └── dependencies.py
├── config/
│   └── mappings/
│       ├── create_experiment_request.json
│       └── create_experiment_response.json
├── .env
└── main.py