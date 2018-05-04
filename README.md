## Hasker - A&Q Site

Hasker is website for asking Questions on any theme.
You can ask a question, answer to a question, vote for a question, vote for an answer, mark the answer as right one.

To start server you should clone this repo to your local machine, change directory to **hasker** and type:

```bash
make prod
```

After that script creates **hasker** database in volume **hasker_pg_data** in your docker file system.
Then it builds docker image **hasker** with web-server and start docker-compose with postgres and hasker web-server.

By default server starts on your localhost:8000. 
You can create account and start asking and answering.

If you want to add notifications to users when their question receive new answer please add your email service in settings.py.
By default settings.py configured for **sendgrid** mail service. 
If you provide your login ans password the email notifications will be up.

### Site features

To create question you should be authorized. 
Then you should complete ask form with no more then 3 tags separated by comma.

The same approach is provided for create answer for a question.

If you want to vote for a question or for an answer you should be authorized too.
You can't vote down or up, but only with one voice.
You can't vote on your own question or answer. 
If you are author of the question you can choose correct answer and mark it is a right one. 
You can choose only one answer as right one.

On your settings page you can change your email and add avatar to your user profile.

To make a search query you can type keywords separated by space in search input.
If you want search by tag you can click on tag of the question or type in search input:
```
tag:<tag-to-search-for>
```

