# Google Cloud Datastore

## Incredibly quick demo

You need a few packages, so take a look at requirements.txt and `pip install` them.

    $ pip install -r requirements.txt

Then you should be all set to run the demo...

    $ python demo/demo.py

## Doing this on your own

### Create a project

- Visit https://cloud.google.com/console
- Click the big red button that says "Create Project".
- In the name box, pick something friendly.
- In the ID box, pick something unique to you (ie, jgatsby-storage).

### Enable the Cloud Datastore

- Click on APIs & Auth, and scroll down to Google Cloud Datastore API.
- Click the "Off" button on the right to turn it into an "On" :)

### Enable a Service Account

- Click on Credentials (under APIs & Auth).
- Under the OAuth section (the first one) click the big red button that says "Create New Client ID".
- Choose Service Account, and click the blue button "Create Client ID".
- This will automatically download a private key, don't lose this.
- Rename this key something shorter... like "jgatsby-storage.key".
- Copy the long weird e-mail address (it's labeled "E-mail address" in the information for the service account you just created).

### Add some demo data (manually)

- Click on Cloud Datastore towards the bottom.
- Click the big red button that says "Create Entity".
- Leave Namespace alone (should be in the default one).
- For Kind, type in "Thing".
- Leave Key set to ID (this will automatically pick a numeric ID for you).
- In the first textbox, type in "name" (this is like one of the columns in a regular database).
- Leave it as a string, and indexed.
- For the value, type in "Computer".
- Click "Create Entity".

What you just did there is add an entity that equates to a Python object you'd construct like... Thing(name='Computer').

Feel free to add another Thing. Maybe a "Beer"? And a "Desk"?

### Write some code

You can use `demo/demo.py` as a reference.

    import gclouddatastore

    CLIENT_EMAIL = '<the e-mail address you copied>'
    KEY_PATH = './jgatsby-storage.key'  # Make this the path to the key that auto-downloaded.

    connection = gclouddatastore.get_connection(
        'jgatsby-storage',  # Make this the project ID you picked before.
        CLIENT_EMAIL, KEY_PATH)

    # This will print out all the Thing's you created.
    print connection.query('Thing').fetch()

### Yay, you're done

Go build cool stuff :)

## Hmm, that's not on the Google Cloud website...

You might notice that the other tutorials are a bit different.
This introduction is focused on you, on your home computer, with no interest
at all in using Google Compute Engine.
