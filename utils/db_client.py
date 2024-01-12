import pymysql


class DBClient:
    def __init__(self):
        self.conn = None
        self.cur = None
        self.db = ''
        self.table_list = []

    def __del__(self):
        try:
            self.conn.close()
        except Exception as e:
            print('db close error: ', e)

    def initialize(self, host, port, user, password, db, charset):
        self.db = db
        self.conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            db=db,
            charset=charset
        )
        print(f'{host}:{port} - 연결 성공')
        self.cur = self.conn.cursor()
        # self.table_list = self._table_check(db)

    def _table_check(self, db):
        self.conn.select_db('mysql')
        sql = f"SELECT table_name FROM innodb_table_stats WHERE database_name = '{db}'"
        data = self.read_query(sql)
        table_list = []
        for t in data:
            table_list.append(t[0])
        self.conn.select_db(db)
        # print(table_list)
        print(f'{db} - 테이블 목록 불러오기 성공')
        return table_list

    def _send_query(self, qry, cmt=False, re=True):
        try:
            self.cur.execute(qry)
            data = self.cur.fetchall()
            if cmt:
                self.conn.commit()
        except Exception as e:
            print(f'query error: {e}')
            print(f'query: {qry}')
        return data if re else None

    def commit(self):
        self.conn.commit()
        print('변경 정보 반영 성공 - commit')

    def read_query(self, qry):
        data = self._send_query(qry, False, True)
        return data

    def write_query(self, qry, cmt=False):
        self._send_query(qry, cmt, False)

    def create_table(self, name, column, key):
        name = name.lower()
        if name in self.table_list:
            print(f"{self.db} - 테이블 '{name}'이 이미 존재합니다.")
        else:
            columns_lines = []
            typ = ''
            for n, t in column.items():
                if t[0] == 'boolean':
                    typ = 'BOOLEAN'
                elif t[0] == 'int':
                    typ = 'INT'
                elif t[0] == 'float':
                    typ = 'FLOAT'
                elif t[0] == 'string':
                    typ = 'VARCHAR(50)'
                elif t[0] == 'datetime':
                    typ = 'DATETIME(6)'
                elif type(t[0]) == dict:
                    typ = 'JSON'
                elif type(t[0]) == set:
                    typ = f'SET{tuple(t[0])}'

                k = ''
                if n in key:
                    if key[n] == 'primary':
                        k = ' PRIMARY KEY'

                columns_lines.append(f"`{n}` {typ} {t[1]}{k}")

            columns_info = ", ".join(columns_lines)

            sql = f"CREATE TABLE `{name}` ({columns_info});"
            self.write_query(sql)

            print(f"{self.db} - 테이블 '{name}' 생성 성공")
            self.table_list.append(name)