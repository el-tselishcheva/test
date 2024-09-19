import os, psycopg2

class DatabaseHandler:
    def __init__(self):
        self.dbname = "doc-archive-sys"
        self.user = "postgres"
        self.password = "1234"
        self.host = "localhost"
        self.port = "5432"
        self.conn = None
        self.cur = None

    def connect(self):
        try:
            self.conn = psycopg2.connect(
                dbname = self.dbname,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )
            self.cur = self.conn.cursor()
            print('Подключение к базе данных успешно')
        except psycopg2.Error as e:
            print(f"Ошибка при подключении к базе данных: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()
            print('Отключение от базы данных')

    def execute_query(self, query):
        try:
            self.cur.execute(query)
            self.conn.commit()
            print('Запрос выполнен успешно')
        except psycopg2.Error as e:
            print(f"Ошибка при выполнении запроса: {e}")

    def fetch_data(self):
        return self.cur.fetchall()
    
    def check_auth_data(self, username, password):
        self.connect()

        sql = f"""
            SELECT * FROM users
            WHERE username = '{username}' AND password = '{password}';
        """

        try:
            self.cur.execute(sql)
            result = self.cur.fetchone()
            return result

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()

    def delete_docs(self, id):
        self.connect()

        sql = f"""
            SELECT v.file_path
            FROM doc_versions v
            WHERE v.ver_id = {id};
        """

        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()

            sql = f"""
                DELETE FROM doc_versions WHERE ver_id = {id};
            """

            self.cur.execute(sql)
            self.conn.commit()

            for file_path in result:
                try:
                    os.remove(file_path[0])
                    print(f"Файл {file_path[0]} успешно удален.")
                except FileNotFoundError:
                    print(f"Файл {file_path[0]} не существует.")
                except PermissionError:
                    print(f"Нет прав на удаление файла {file_path[0]}.")
                except Exception as e:
                    print(f"Произошла ошибка при удалении файла {file_path[0]}: {e}")

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()

    def search_docs(self, projects=None, categories=None):
        self.connect()

        condition = ''
        condition_1 = []
        condition_2 = []

        if projects[0] != '':
            for project in projects:
                condition_1.append(f"m.module_name = '{project}'")
        if categories[0] != '':
            for category in categories:
                condition_2.append(f"c.category_name = '{category}'")
        
        if condition_1:
            condition += "(" + " OR ".join(condition_1) + ")"
        if condition_2:
            if condition_1:
                condition += " AND "
            condition += "(" + " OR ".join(condition_2) + ")"
        
        if condition:
            sql = f"""
                SELECT
                    v.ver_id,
                    d.doc_name,
                    c.category_name,
                    m.module_name,
                    v.file_path
                FROM
                    modules m
                    JOIN doc_versions v ON m.module_id = v.module_id
                    JOIN documents d ON v.doc_id = d.doc_id
                    JOIN doc_categories dc ON d.doc_id = dc.doc_id
                    JOIN categories c ON dc.category_id = c.category_id
                WHERE {condition};
            """
        else:
            sql = f"""
                SELECT
                    v.ver_id,
                    d.doc_name,
                    c.category_name,
                    m.module_name,
                    v.file_path
                FROM
                    modules m
                    JOIN doc_versions v ON m.module_id = v.module_id
                    JOIN documents d ON v.doc_id = d.doc_id
                    JOIN doc_categories dc ON d.doc_id = dc.doc_id
                    JOIN categories c ON dc.category_id = c.category_id;
            """

        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
            return result

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()

    def get_all_modules(self):
        self.connect()

        sql = f"""
            SELECT module_name FROM modules;
        """

        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
            return result

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()
    
    def get_module_path(self, m_name):
        self.connect()

        sql = f"""
            SELECT dir_path FROM modules
            WHERE module_name = '{m_name}';
        """

        try:
            self.cur.execute(sql)
            result = self.cur.fetchone()
            return result

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()

    def get_all_categories(self):
        self.connect()

        sql = f"""
            SELECT * FROM categories;
        """

        try:
            self.cur.execute(sql)
            result = self.cur.fetchall()
            return result

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()
    
    def add_project(self, p_name, d_path, u_id):
        self.connect()

        sql = f"""
            INSERT INTO modules (module_name, dir_path, created_by) VALUES ('{p_name}', '{d_path}', {u_id}) RETURNING module_id;
        """

        try:
            self.cur.execute(sql)
            p_id = self.cur.fetchone()
            self.conn.commit()
            return p_id[0]

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()

    def add_doc_templates(self, p_id, p_path, c_id, c_name, u_id):
        self.connect()

        d_path = f"{p_path}{c_name}.docx"

        sql = f"""
            DO $$
                DECLARE
                    new_doc_id INT;
                BEGIN
                    INSERT INTO documents (doc_name, created_by) VALUES
                    ('{c_name}', {u_id}) RETURNING doc_id INTO new_doc_id;

                    INSERT INTO doc_categories (doc_id, category_id) VALUES
                    (new_doc_id, {c_id});

                    INSERT INTO doc_versions (doc_id, module_id, ver_number, file_path, uploaded_by) VALUES
                    (new_doc_id, {p_id}, 1, '{d_path}', {u_id});
            END $$;
        """

        try:
            self.cur.execute(sql)
            self.conn.commit()
            return d_path

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()

    def copy_modules(self, p_id, m_name, u_id):
        self.connect()

        sql = f"""
            INSERT INTO module_hierarchy (child_id, parent_id) VALUES
            ((SELECT module_id FROM modules WHERE module_name = '{m_name}'), {p_id});

            DO $$
                DECLARE
                    child_id INT;
                    parent_id INT;
                    doc RECORD;
                    new_doc_id INT;
                    new_file_path VARCHAR;
                    p_dir_path VARCHAR;
                BEGIN
                    SELECT module_id INTO child_id FROM modules WHERE module_name = '{m_name}';
                    SELECT dir_path INTO p_dir_path FROM modules WHERE module_id = '{p_id}';
                    
                    FOR doc IN (
                        SELECT d.doc_id, d.doc_name, d.description, d.created_by, v.ver_number, v.file_path, m.module_name, m.dir_path
                        FROM doc_versions v
                        JOIN documents d ON v.doc_id = d.doc_id
                        JOIN modules m ON v.module_id = m.module_id
                        WHERE v.module_id = child_id
                    )
                    LOOP
                        IF NOT EXISTS (SELECT 1 FROM documents WHERE doc_name = doc.doc_name) THEN
                            INSERT INTO documents (doc_name, description, created_by, created_at)
                            VALUES (doc.doc_name, doc.description, doc.created_by, NOW())
                            RETURNING doc_id INTO new_doc_id;
                        ELSE
                            SELECT doc_id INTO new_doc_id FROM documents WHERE doc_name = doc.doc_name;
                        END IF;

                        new_file_path := p_dir_path || '\\\\' || substring(doc.file_path from strpos(doc.file_path, doc.module_name));

                        INSERT INTO doc_versions (doc_id, module_id, ver_number, file_path, uploaded_by, uploaded_at)
                        VALUES (new_doc_id, {p_id}, doc.ver_number + 1, new_file_path, {u_id}, NOW());
                    END LOOP;
            END $$;
        """

        try:
            self.cur.execute(sql)
            self.conn.commit()

        except Exception as E:
            self.conn.rollback()
            return E

        finally:
            self.conn.close()
