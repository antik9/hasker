## Hasker API

There are several available requests for Hasker API. 
All of them starts with **/rest/** uri path and then you should add necessary path to make a certain request.

### 1. GET index of Hasker Api
*full path: /rest/index/*

If you want to get questions sorted by date or rating you should get index page.

Parameters:
* page \<int> *page of list of the questions | default = 1*
* data \<char> *sorting order | default = t | variants:*
    * d - by date
    * t - by trend(rating)
* batch \<int> *number of questions on one page in response | default = 10*

#### Example

```
>>> curl "http://localhost:8000/rest/index/?data=t&page=3&batch=5"

{
    "page": 3,
    "sort by": "rating",
    "has next": true,
    "has prev": true,
    "questions": [
        {
            "id": 273,
            "question_title": "master condition elect",
            "author": "Charles Cooper",
            "pub_date": "04/22/18 12:12:48",
            "question_tags": [
                "condition",
                "elect"
            ],
            "number_of_answers": 2,
            "rating": 23
        },
        ...
    ]
}
```


### 2. GET full information about a question
*full path: /rest/question/*

If you want to get full question you should provide question id.

Parameters:
* question_id \<int> *id of a question | required*

#### Example

```
>>> curl "http://localhost:8000/rest/question/?question_id=253"

{
    "id": 253,
    "question_title": "strange wear recruit counter sky hi protection stair",
    "author": "Olivia Jaxson",
    "pub_date": "04/22/18 12:12:48",
    "question_tags": [
        "protection",
        "recruit",
        "strange"
    ],
    "question_text": "ugly copy record sorry significance wipe yourself universe season...",
    "number_of_answers": 7,
    "rating": 25
}
```

### 3. GET answers to the question
*full path: /rest/answers/*

To get answers you should provide question id and also page and batch size.

Parameters:
* question_id \<int> *id of a question | required*
* page \<int> *page of list of the questions | default = 1*
* batch \<int> *number of questions on one page in response | default = 8*

#### Example

```
>>> curl "http://localhost:8000/rest/answers/?question_id=243&page=2&batch=3"

{
    "question_id": "243",
    "page": "2",
    "has next": true,
    "has prev": true,
    "answers": [
        {
            "author": "Katherine Andrew",
            "right": false,
            "rating": 18,
            "answer_text": "abortion small metal threat golden finding commercial DNA series..."
        },
        ...
    ]
}
```

### 4. GET trending questions
*full path: /rest/trending/*

By this request you can get top 5 questions by rating.

No parameters.

#### Example

```
>>> curl "http://localhost:8000/rest/trending/"

[
    {
        "id": 241,
        "question_title": "source tree besides minute cat",
        "rating": 29
    },
    ...
]

```

### 5. GET search request
*full path: /rest/search/*

You can search questions by words presented in the text or title of the question or by tags.

Parameters:
* page \<int> *page of list of the questions | default = 1*
* search \<string> *search query | required | variants:*
    * words separated with white spaces
    * tag:<your-tag> construction
* batch \<int> *number of questions on one page in response | default = 10*

#### Example

```
>>> curl "http://localhost:8000/rest/search/search=?tag:prisoner"

{
    "page": 1,
    "has next": false,
    "has prev": false,
    "questions": [
        {
            "id": 260,
            "question_title": "supposed sector learning thin admit factor manner demonstrate grab prisoner",
            "author": "Genesis Eva",
            "pub_date": "04/22/18 12:12:48",
            "question_tags": [
                "prisoner",
                "thin",
                "admit"
            ],
            "number_of_answers": 4,
            "rating": 27
        },
    ...
]

```

### 6. POST your credentials to obtain JWT token
*full path: /rest/api-token-auth/*

Create POST request, provide your credential and you can get JWT authentication token.

#### Example

```
>>> curl -X POST -d "username=marylou&password=sweetmary" "http://localhost:8000/rest/api-token-auth/"

{"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo4NywidXNlcm5hbWUiOiJtYXJ5bG91IiwiZXhwIjoxNTI1ODE5MjMyLCJlbWFpbCI6Im1hcnlsb3VAbWFpbC5jb20ifQ.koWxU19C4iuAd_OHaIucS0r7qEgr3NbUliftPR-YxG8"}
```