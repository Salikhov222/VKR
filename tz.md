# Техническое задание

### 1 Тема
Веб-сервиса по поиску работы, сотрудников и исполнителей для решения бытовых и бизнес-задач

### 2 Словесное описание предметной области и актуальность 

В условиях современного мира большинство людей испытывает трудности с поиском работы своей мечты. Каждый желает найти вакансию, которая подходит именно ему, будет высокооплачиваемой и интересной. Сделать это с помощью данного веб-приложения будет нетрудно, так как агентство предоставляет большой выбор позиций в различных отраслях деятельности. Используйте данное веб-приложение - и подходящая работа отыщется быстро.

### 3 Сбор информации

Назначение сайта – помощь для людей в поиске постоянной работы или временного выполнения услуг. Целевой аудиторией сайта являются безработные люди, работодатели и специалисты различных областей.

### 4 Спецификация

Сервис должен предоставлять в полном объеме следующие возможности:
1) Работа сайтом незарегистрированным пользователям, но без допуска к некоторым функциям (просмотр вакансий, заданий, исполнителей и т.д)
2) Регистрация всех пользователей
3 Публикация вакансий и заданий с определенном набором параметров
4) Отклик на вакансию и предложение своих услуг
5) Доступ к личным кабинетам и изменение личных данных

### 3 Описание данных, хранящихся в БД
База данных должна содержать следующие данные:

* Список фирм, с указанием счёта фирмы, с которого автоматически снимается определенная сумма при размещении вакансии или при просмотре резюме.
* Данные о соискателях, работодателях, исполнителей и заказчиков.
* Вакансии, размещенные фирмами.
* Резюме, опубликованные соискателями.
* Журналы просмотров резюме, вакансий и услуг.
* Категория отраслей.
* Должности, указанные в вакансиях и резюме и классифицированные по отраслям.
* Предложения временной подработки и бытовых услуг.
* Категория сфер деятельностей. 

### 4 Роли пользователей приложения
* Администратор
* Незарегистрированный пользователь
* Работодатель
* Соискатель
* Заказчик
* Исполнитель

### 5 Развернутое описание функционала приложения для каждой из ролей

 #### Администратор
Администратор, пройдя аутентификацию, может редактировать информацию в журналах просмотров, в категориях отраслей и прочую информацию в БД. Также администратор, после подачи резюме соискателем, оценивают полноту информации и присваивают резюме рейтинг.

 #### Незарегистрированный пользователь
 Незарегистрированный пользователь может просматривать каталог вакансий и каталог заказов без возможности просмотра контактных данных фирм или заказчиков.

 #### Работодатель
 Работодатель имеет возможность размещать вакансии и просматривать резюме. Для этого работодатель должен сперва зарегистрироваться, введя имя, фамилию, название фирмы, ИНН, контактные данные. После этого он может войти в личный кабинет указав логин и пароль. Для размещения вакансии или просмотра резюме фирма должна внести оплату. Для того чтобы произвелась оплата, работодатель должен пополнить счет фирмы в личном кабинете на необходимую сумму любым удобным способом. В вакансии может содержаться следующая информация: пол и возраст кандидата,должность, оклад, опыт работы, занятость (полная/неполная), и т.д.

 #### Соискатель
 Соискатель перед входом в учетную запись должен будет пройти регистрацию, заполнив имя, фамилию, e-mail или телефон. После входа в свою учетную запись имеет право размещать резюме бесплатно, в котором указывается его основная информация (ФИО, пол, возраст, e-mail, телефон), а также желаемая должность, опыт работы, график, навыки, оклад и т.д. Он также имеет право просматривать вакансии с дополнительной возможности отклика на нее и просмотра контактной информации фирмы.

 #### Заказчик
 Заказчик может войти в систему под своей учетной записью (или создать ее, если ее нет). После авторизации ему доступен профиль, где он может изменить информацию о себе: имя, телефон и e-mail. После того, как заказчик заполнил информацию о себе, он может создать задание, перейдя на страницу создания. На ней он указывает отрасль и название задания для исполнителя, описание задания, стоимость и срок выполнения. В стоимость также входит и комиссия веб-сервиса. Задание публикуется нажатием соответствующей кнопки и за ним автоматически закрепляется дата создания. Также заказчик может искать исполнителей в каталоге, перейдя на соответствующую страницу, которая должна быть доступна только для заказчиков. Под каждым исполнителем находится ссылка «Связаться с исполнителем», перейдя по которой, заказчик может открыть страницу с конкретным исполнителем и просмотреть его контактные данные (e-mail, телефон).

 #### Исполнитель
 Исполнитель может войти в систему под своей учетной записью (или создать ее, если ее нет). После авторизации ему доступен профиль, где он может изменить информацию о себе: имя, список отраслей, телефон и e-mail. Исполнитель может искать задания в каталоге, перейдя на соответствующую страницу. На этой странице отображается список заданий, содержащий соответствующую ей отрасль, имя заказчика, стоимость и срок выполнения и дата публикации.  Под каждым заданием находится ссылка «Связаться с заказчиком», перейдя по которой, исполнитель может открыть страницу с конкретным заданием и просмотреть контактные данные заказчика (e-mail, телефон).

### 6 Предполагаемые технологии и платформа реализации

Веб-приложение на библиотеке Flask на языке Python. СУБД – PostgreSQL.


### 7 Срок представления курсовой работы
25.06.2021