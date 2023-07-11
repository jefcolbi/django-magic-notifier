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
two files within the hello folder named **email.html** and **email.txt** or **email.mjml**
and **email**. Because DMN supports also mjml via 3rd party package.
If you will send notifications via sms then you must create a file named **sms.txt**.
If you want to send push notification then you must create a file **push.json**

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

*app_name/templates/notifier/base/push.json*::

    {% extends "base_notifier/push.json" %}


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

    {% extends "notifier/base/email.txt" %}
    {% block content %}
    >Hello {{ user.email }}
    {% endblock %}

*app_name/templates/notifier/hello/email.mjml*::

    <mjml>
      <mj-head>
        <mj-attributes>
          <mj-text align="center" color="#555" />
        </mj-attributes>
      </mj-head>
      <mj-body background-color="#eee">
        <mj-section>
          <mj-column>
            My Logo
          </mj-column>
        </mj-section>
        <mj-section background-color="#fff">
          <mj-column>
            <mj-text align="center">
              <h2>Welcome</h2>
            </mj-text>
            <mj-text>
              Welcome to our company
            </mj-text>
          </mj-column>

        </mj-section>
        <mj-section>
          <mj-column>
            <mj-text> My Company </mj-text>
            </mj-column>
        </mj-section>
      </mj-body>
    </mjml>


*app_name/templates/notifier/hello/sms.txt*::

    {% extends "notifier/base/sms.txt" %}
    {% block content %}
    >Hello {{ user.email }}
    {% endblock %}

*app_name/templates/notifier/hello/push.json*::

    {% extends "notifier/base/push.json" %}
    {% block subject %}Hello {{ user.username }}{% endblock %}

