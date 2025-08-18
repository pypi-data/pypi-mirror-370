## DB Class 패키지

db/
├── interfaces/
│   └── base_repository.py   # 공통 인터페이스
├── repositories/
│   ├── base.py              # SQLAlchemy 기반 추상 Repository
│   └── stock_repository.py  # 실제 도메인별 구현체
├── engine.py                # DB 커넥션 엔진 설정
└── session.py               # 세션 팩토리 제공# mjdb
