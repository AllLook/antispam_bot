# antispam_bot
Бот для управления чатом
  Это Telegram-бот, предназначенный для управления чатом. Он предоставляет функции, такие как кик, мут и размут пользователей, а также мониторинг статистики сообщений для каждого чата отдельно. Бот также проверяет сообщения на наличие спам-слов и автоматически               предупреждает и кикает пользователей при обнаружении спама.

#Функции
  ##Кик пользователей: 
  Кикнуть пользователя из чата, если пользователь, который кикает другого пользователя имеет не менее 50 сообщений в чате.
  Мут пользователей: 
  Замутить пользователя на указанное время (по умолчанию 1 минута).
  Размут пользователей:  
  Размутить ранее замученного пользователя.
##Обнаружение спама: 
  Проверка сообщений на наличие предопределенных спам-слов и предупреждение пользователя. Если сообщение не будет исправлено, пользователь будет кикнут из чата через 1 минуту.
##Команды
  /start - Начать взаимодействие с ботом.
  /help - Показать доступные команды.
  /kick - Кикнуть пользователя (нужно ответить на сообщение пользователя, и он должен отправить не менее 50 сообщений).
  /mute - Замутить пользователя на указанное время (нужно ответить на сообщение пользователя).
  /unmute - Размутить ранее замученного пользователя (нужно ответить на сообщение пользователя).

##Использование
  1.Добавьте бота в чат с правами администратора. Имя бота @AS_TG_AL_bot
  2.Используйте команду /start, чтобы запустить бота.
  3.Используйте различные команды, описанные выше, для управления чатом.

##Заметки
  Убедитесь, что у бота есть необходимые разрешения в чате для выполнения действий, таких как кик и мут пользователей.
  Бот использует многопоточность для обработки предупреждений и киков без блокировки других операций.
##Лицензия
  Этот проект лицензирован под лицензией MIT.
