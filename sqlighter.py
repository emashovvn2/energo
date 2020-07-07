import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status = True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `status` = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def users_with_subscribe(self):
        """Форминуем список пользователей у которых включена подписка"""
        with self.connection:
            result = self.cursor.execute('SELECT user_id FROM subscriptions WHERE status = 1').fetchall()
            return result

    def add_subscriber(self, user_id, status = True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscriptions` (`user_id`, `status`) VALUES(?,?)", (user_id,status))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?", (status, user_id))

    def get_subscription(self, user_id):
        """Выдаем статус подписки пользователя"""
        with self.connection:
            """print((self.cursor.execute('SELECT status FROM `subscriptions` WHERE `user_id` = ?', (user_id,))))
            if (self.cursor.execute('SELECT status FROM `subscriptions` WHERE `user_id` = ?', (user_id,)))[0] == (1,0):
                return True
            else:
                return False"""
            return self.cursor.execute('SELECT status FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()

    def add_address(self, user_id, street, house):
        """Добавляем адрес в подписки пользователя"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `Address` (`user_id`, `street`, `house`) VALUES(?,?,?)", (user_id,street,house))

    def clear_all_address(self, user_id):
        """Удаляем ВСЕ адреса заведенные конкретным пользователем"""
        user_id = str(user_id)
        with self.connection:
            return self.cursor.execute("DELETE FROM `Address` WHERE `user_id` = ?", (user_id,))

    def delete_addr(self, user_id, addr):
        """Удаляем ОДИН адрес из заведенных конкретным пользователем"""
        if (len(addr) == 2):
            with self.connection:
                return self.cursor.execute("DELETE FROM `Address` WHERE user_id = ? AND street = ? AND house = ?", (user_id,addr[0],addr[1]))
        else:
            return "Некорректная длина переданных данных"

    def list_address(self, user_id):
        """Выдаем список адресов на которые подписан пользователь"""
        user_id = str(user_id)
        with self.connection:
            return self.cursor.execute("SELECT street, house FROM `Address` WHERE `user_id` = ?", (user_id,))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
