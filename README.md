# Топ 100 статей с википедии с максимальным количеством картинок
Изменив домен третьего уровня в переменной root можно так же анализировать другие языковые версии википедии.<br>
Программа работает, используя API википедии для получения всех статей, колличества картинок в них и т.д.<br>
Программа по ходу выполнения выводит url обрабатываемых страниц. В случае прерыва анализа в переменную last_article можно написать название статьи или начало этого названия, и при последующем запуске анализ начнётся с этой статьи.<br>
При работе используется база данных sqlite3<br>
