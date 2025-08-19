# Changelog

<!--
   You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst
-->

<!-- towncrier release notes start -->

## 1.0.0 (2025-08-18)


### New features:

- Test with Listmonk 5. @davisagli 


### Internal:

- Update CI configuration. @davisagli 

## 1.0.0a7 (2024-04-24)


### Bug fixes:

- If a subscriber unsubscribes but still has an unconfirmed subscription to another list, don't delete the subscriber. @davisagli #16
- Fix translation of unsubscribe link. @davisagli #17

## 1.0.0a6 (2024-04-22)


### New features:

- Unsubscribe links now include a subscriber UUID, so it's not possible to unsubscribe a different subscriber.
  Also, if the user is unsubscribed from all lists, the listmonk subscriber will be deleted, to avoid retaining private data. @davisagli #14
- Add options to customize the confirmation email for a newsletter. @davisagli #15

## 1.0.0a5 (2024-04-15)


### Bug fixes:

- Make @mailings GET service available on any content where the user has Send Newsletter permission. @davisagli #13

## 1.0.0a4 (2024-04-09)


### New features:

- Send an email confirmation of a new subscription. @davisagli #12

## 1.0.0a3 (2024-04-07)


### Bug fixes:

- Don't add header and footer to the email automatically, so the editor has control. @davisagli #11

## 1.0.0a2 (2024-04-07)


### Bug fixes:

- Avoid runtime dependency on plone.app.robotframework. @davisagli #10

## 1.0.0a1 (2024-04-07)

No significant changes.


## 1.0a1 (unreleased)

- Initial development. @davisagli
