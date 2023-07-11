Usage
-----


Send an email with a direct final string (no template) to a user instance::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, [user], final_message="Nice if you get this")


Send an email with a template (hello) to a user instance::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, [user], template='hello')


Send an email with a template to all superuser::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, "admins", template='hello')


Send an email with a template to all staff users::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, "staff", template='hello')


Send an email with a template to all users::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, "all", template='hello')


Send an email with a template to all users excluding staff::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, "all-staff", template='hello')


Send an email with a file and a template to all users::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email"], subject, "all-staff", template='hello',
        files=['path/to/file.ext'])


Send a sms with a direct message (no template) to a set of users::

    users = User.objects.filter(pk<10)
    subject = "Test magic notifier"
    notify(["sms"], subject, users, final_message="Nice if you get this")


Send a sms with a template to a set of users::

    users = User.objects.filter(pk<10)
    subject = "Test magic notifier"
    notify(["sms"], subject, users, template='hello')


Send an email and sms with a template to all users excluding staff::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email", 'sms'], subject, "all-staff", template='hello')

Send an email, a sms and a push notification with a template to all users excluding staff::

    user = User(email="testuser@localhost", username="testuser")
    subject = "Test magic notifier"
    notify(["email", 'sms', 'push'], subject, "all-staff", template='hello')
