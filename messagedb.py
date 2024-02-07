import sqlite3
from datetime import datetime


class MessageDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS phone_numbers (
                phone_id INTEGER PRIMARY KEY,
                phone_number TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY,
                message_sid TEXT,
                from_phone_id INTEGER,
                to_phone_id INTEGER,
                body TEXT,
                timestamp TEXT,
                FOREIGN KEY (from_phone_id) REFERENCES phone_numbers (phone_id),
                FOREIGN KEY (to_phone_id) REFERENCES phone_numbers (phone_id)
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_prompts (
                system_prompt_id INTEGER PRIMARY KEY,
                system_prompt TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                model_id INTEGER PRIMARY KEY,
                model_name TEXT
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                phone_id INTEGER PRIMARY KEY,
                system_prompt_id INTEGER,
                model_id INTEGER,
                stop_sequence TEXT,
                max_tokens INTEGER,
                temperature FLOAT,
                top_p FLOAT,
                frequency_penalty FLOAT,
                presence_penalty FLOAT,                        
                FOREIGN KEY (phone_id) REFERENCES phone_numbers (phone_id),
                FOREIGN KEY (system_prompt_id) REFERENCES system_prompts (system_prompt_id),
                FOREIGN KEY (model_id) REFERENCES models (model_id)
            )
        ''')

        self.conn.commit()

#### GETTING IDs FROM VALUES####
    def get_phone_id(self, phone_number):
        self.cursor.execute(
            'SELECT phone_id FROM phone_numbers WHERE phone_number = ?', (phone_number,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"[DB]: Phone number '{phone_number}' not found.")
            return None

    def get_system_prompt_id(self, system_prompt):
        self.cursor.execute(
            'SELECT system_prompt_id FROM system_prompts WHERE system_prompt = ?', (system_prompt,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"[DB]: System prompt '{system_prompt}' not found.")
            return None

    def get_model_id(self, model_name):
        self.cursor.execute(
            'SELECT model_id FROM models WHERE model_name = ?', (model_name,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"[DB]: Model '{model_name}' not found.")
            return None

#### ADDING TO DB ####
    def add_phone_number(self, phone_number):
        phone_id = self.get_phone_id(phone_number)
        if phone_id is not None:
            print(
                f"[DB]: Phone number '{phone_number}' already exists in the database.")
            return phone_id
        self.cursor.execute(
            'INSERT INTO phone_numbers (phone_number) VALUES (?)', (phone_number,))
        self.conn.commit()
        phone_id = self.cursor.lastrowid
        print(
            f"[DB]: Phone number '{phone_number}' added successfully. Phone ID: {phone_id}")
        return phone_id

    def add_message(self, message_sid, from_phone_number, to_phone_number, body):
        from_phone_id = self.add_phone_number(from_phone_number)
        to_phone_id = self.add_phone_number(to_phone_number)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute('''
            INSERT INTO messages (message_sid, from_phone_id, to_phone_id, body, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (message_sid, from_phone_id, to_phone_id, body, timestamp))
        self.conn.commit()
        message_id = self.cursor.lastrowid
        print(f"[DB]: Message added successfully. Message ID: {message_id}")
        return Message(message_id, message_id, from_phone_number, to_phone_number, body, timestamp)

    def add_system_prompt(self, system_prompt):
        system_prompt_id = self.get_system_prompt_id(system_prompt)
        if system_prompt_id is not None:
            print(
                f"[DB]: System prompt '{system_prompt}' already exists in the database.")
            return system_prompt_id
        self.cursor.execute(
            'INSERT INTO system_prompts (system_prompt) VALUES (?)', (system_prompt,))
        self.conn.commit()
        system_prompt_id = self.cursor.lastrowid
        print(
            f"[DB]: System prompt '{system_prompt}' added successfully. System Prompt ID: {system_prompt_id}")
        return system_prompt_id

    def add_model(self, model_name):
        model_id = self.get_model_id(model_name)
        if model_id is not None:
            print(
                f"[DB]: Model '{model_name}' already exists in the database.")
            return model_id
        self.cursor.execute(
            'INSERT INTO models (model_name) VALUES (?)', (model_name,))
        self.conn.commit()
        model_id = self.cursor.lastrowid
        print(
            f"[DB]: Model '{model_name}' added successfully. Model ID: {model_id}")
        return model_id

    def _handle_settings_kwargs(self, **kwargs):
        system_prompt = kwargs.pop('system_prompt', None)
        if system_prompt:
            system_prompt_id = self.add_system_prompt(system_prompt)
            kwargs['system_prompt_id'] = system_prompt_id

        model = kwargs.pop('model', None)
        if model:
            model_id = self.add_model(model)
            kwargs['model_id'] = model_id

        return kwargs

    def add_settings(self, phone_number, **kwargs):
        phone_id = self.get_phone_id(phone_number)
        if phone_id is not None:
            kwargs = self._handle_settings_kwargs(**kwargs)
            values = tuple(kwargs.values())
            set_keys = ', '.join(kwargs.keys())
            sql_question_marks = ', '.join(
                ['?' for _ in range(len(values) + 1)])
            query = f'INSERT INTO settings (phone_id, {set_keys}) VALUES ({sql_question_marks})'
            self.cursor.execute(query, (phone_id, *values))
            self.conn.commit()
            settings_id = self.cursor.lastrowid
            print(
                f"[DB]: Settings for phone number '{phone_number}' added successfully.")
            return settings_id
        else:
            print(f"[DB]: Phone number '{phone_number}' not found.")

#### UPDATING DB ####
    def update_settings_for_phone_number(self, phone_number, **kwargs):
        phone_id = self.get_phone_id(phone_number)
        if phone_id is not None:
            kwargs = self._handle_settings_kwargs(**kwargs)
            values = tuple(kwargs.values())
            set_values = ', '.join([f'{key} = ?' for key in kwargs])
            query = f'UPDATE settings SET {set_values} WHERE phone_id = ?'
            self.cursor.execute(query, (*values, phone_id))
            self.conn.commit()
            print(
                f"[DB]: Settings for phone number '{phone_number}' updated successfully.")
        else:
            print(f"[DB]: Phone number '{phone_number}' not found.")


#### GETTING FROM DB ####

    def get_phone_number(self, phone_id):
        self.cursor.execute(
            'SELECT phone_number FROM phone_numbers WHERE phone_id = ?', (phone_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"[DB]: Phone number with ID '{phone_id}' not found.")
            return None

    def get_messages_for_phone_number(self, phone_number):
        phone_id = self.get_phone_id(phone_number)
        if phone_id is not None:
            self.cursor.execute(
                'SELECT * FROM messages WHERE from_phone_id = ? OR to_phone_id = ?', (phone_id, phone_id))
            results = self.cursor.fetchall()
            messages = []
            for row in results:
                message_id, message_sid, from_phone_id, to_phone_id, body, timestamp = row
                from_phone_number = self.get_phone_number(from_phone_id)
                to_phone_number = self.get_phone_number(to_phone_id)
                # timestamp  = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                message = Message(
                    message_id, message_sid, from_phone_number, to_phone_number, body, timestamp)
                messages.append(message)
            return messages
        else:
            print(f"[DB]: Phone number '{phone_number}' not found.")
            return []

    def get_system_prompt(self, system_prompt_id):
        self.cursor.execute(
            'SELECT system_prompt FROM system_prompts WHERE system_prompt_id = ?', (system_prompt_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            print(
                f"[DB]: System prompt with ID '{system_prompt_id}' not found.")
            return None

    def get_model(self, model_id):
        self.cursor.execute(
            'SELECT model_name FROM models WHERE model_id = ?', (model_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            print(f"[DB]: Model with ID '{model_id}' not found.")
            return None

    def get_settings_for_phone_number(self, phone_number):
        phone_id = self.get_phone_id(phone_number)
        if phone_id is not None:
            self.cursor.execute(
                'SELECT * FROM settings WHERE phone_id = ?', (phone_id,))
            result = self.cursor.fetchone()
            if result:
                phone_id, system_prompt_id, model_id, stop_sequence, max_tokens, temperature, top_p, frequency_penalty, presence_penalty = result
                system_prompt = self.get_system_prompt(system_prompt_id)
                model = self.get_model(model_id)
                # return Settings(system_prompt, stop_sequence, max_tokens, temperature, top_p, frequency_penalty, presence_penalty)
                return {
                    'model': model,
                    'system_prompt': system_prompt,
                    'stop_sequence': stop_sequence,
                    'max_tokens': max_tokens,
                    'temperature': temperature,
                    'top_p': top_p,
                    'frequency_penalty': frequency_penalty,
                    'presence_penalty': presence_penalty
                }
            else:
                print(
                    f"[DB]: Settings for phone number '{phone_number}' not found.")
                return None
        else:
            print(f"[DB]: Phone number '{phone_number}' not found.")
            return None

    def delete_messages_for_phone_number(self, phone_number):
        phone_id = self.get_phone_id(phone_number)
        if phone_id is not None:
            self.cursor.execute(
                'DELETE FROM messages WHERE from_phone_id = ? OR to_phone_id = ?', (phone_id, phone_id))
            self.conn.commit()
            print(
                f"[DB]: Messages for phone number '{phone_number}' removed successfully.")
        else:
            print(f"[DB]: Phone number '{phone_number}' not found.")

    def close(self):
        self.conn.close()


class Message:
    def __init__(self, message_id, message_sid, from_phone_number, to_phone_number, body, timestamp):
        self.message_id = message_id
        self.message_sid = message_sid
        self.from_phone_number = from_phone_number
        self.to_phone_number = to_phone_number
        self.body = body
        self.timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')

    def __repr__(self):
        return f"Message(from_phone_number={self.from_phone_number}\nto_phone_number={self.to_phone_number}\nbody={self.body}\ntimestamp={self.timestamp}))"


class Settings:
    def __init__(self, system_prompt, stop_sequence, max_tokens, temperature, top_p, frequency_penalty, presence_penalty):
        self.system_prompt = system_prompt
        self.stop_sequence = stop_sequence
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty

    def __repr__(self):
        return f'{type(self)}(' + ','.join(f'{key}={value}' for key, value in self.__dict__.items()) + ')'
