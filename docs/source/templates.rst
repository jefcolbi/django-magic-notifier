Templates
---------


Django Magic Notifier supports templates out of the box. 
To add new templates to your project to be used with DMN, you have to create 
a folder named **notifier** in one of your template's folder. 

If your app name is **app_name** then create a directory **app_name/templates/notifier** 

Now suppose you want to have a template named hello, then within the newly created
folder created another folder like that **app_name/templates/notifier/hello**

Now in this folder you have to create some files depending on how you will send your
notifications. If you will send your notification via email then you must create
two files within the hello folder named **email.html** and **email.txt**.
If you will send notifications via sms then you must create a file named **sms.txt**.

It is a common behavior to have a base template, you can do the same by creating a
folder named **base** in the notifier folder and creating the files **email.html**,
**email.txt** and **sms.txt**.

Django Magic Notifier is shipped with some base templates that you can use. Let look
at this example:

*app_name/templates/notifier/base/email.html*::

    {% extends "base_notifier/email.html" %}

*app_name/templates/notifier/base/email.txt*::

    {% extends "base_notifier/email.txt" %}

*app_name/templates/notifier/base/sms.txt*::

    {% extends "base_notifier/sms.txt" %}


Now in the hello template folder, you do:

*app_name/templates/notifier/hello/email.html*::

    {% extends "notifier/base/email.html" %}
    {% block content %}
    <tr>
        <td><p>Hello {{ user.email }}
        </td>
    </tr>
    {% endblock %}

*app_name/templates/notifier/hello/email.txt*::

    {% extends "notifier/hello/email.txt" %}
    {% block content %}
    >Hello {{ user.email }}
    {% endblock %}

*app_name/templates/notifier/hello/sms.txt*::

    {% extends "notifier/hello/sms.txt" %}
    {% block content %}
    >Hello {{ user.email }}
    {% endblock %}

