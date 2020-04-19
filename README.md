Sprinkle files from one source to multiple different sources.

User configures in a file source:
    - google photos

User configures sinks:
    - other google photos accounts
    - dropbox
    - onedrive

[Free storage tiers](https://www.howtogeek.com/310776/all-the-cloud-storage-services-that-offer-free-storage)


MVP sync files accross google accounts

An app is required to review files & adjust/add accounts and manage settings. - react native looks like a good choice.

python.

Implementation notes:
- enable Photos Library api from google cloud console
- create a consent screen with required scopes
- create an oauth2 client id (save id and secret)


Do we need a "sprnklr account"?)
Yes - we do need a way to map an account on our side to a set of remote (third party) accounts.

# Primary Account

If you move files all over the place willy nilly the user is going to get annoyed.
Instead, we should define a primary account so that all new photos stay there
and we move photos from the tail end of the date range out to linked accounts.
This way they have a decent sized buffer as to which photos stay editable and
close by, and which ones get moved out.

